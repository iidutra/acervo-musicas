"""
Serviço de recomendação de repertório litúrgico.

Sugere músicas para cada momento de uma celebração com base em:
- Categorias litúrgicas (entrada, salmo, ofertório, comunhão, etc.)
- Tempo litúrgico (quaresma, páscoa, natal, etc.)
- Frequência de uso (prioriza músicas menos usadas recentemente)
- Tags relevantes
- Tom preferencial (se informado)
"""
import logging
from collections import defaultdict
from datetime import date, timedelta

from django.db.models import Count, Q, Max

from apps.musicas.models import Musica, CategoriaLiturgica

logger = logging.getLogger(__name__)

# Standard liturgical order for a Mass
MOMENTOS_MISSA = [
    'entrada',
    'ato penitencial',
    'glória',
    'salmo',
    'aclamação',
    'ofertório',
    'santo',
    'comunhão',
    'pós-comunhão',
    'final',
]

# Mapping of tempo litúrgico to relevant tags/categories for filtering
TEMPO_LITURGICO_FILTERS = {
    'advento': ['advento'],
    'natal': ['natal'],
    'quaresma': ['quaresma'],
    'tríduo_pascal': ['páscoa', 'quaresma'],
    'pascoa': ['páscoa'],
}


class RecomendacaoService:
    """Serviço de recomendação de músicas para repertórios."""

    def __init__(self, dias_recencia: int = 30):
        """
        Args:
            dias_recencia: músicas usadas nos últimos N dias são penalizadas.
        """
        self.dias_recencia = dias_recencia

    def recomendar_repertorio_completo(
        self,
        tipo_celebracao: str = 'missa_dominical',
        tempo_liturgico: str = '',
        max_por_momento: int = 5,
    ) -> dict[str, list[dict]]:
        """
        Recomenda músicas para cada momento litúrgico de uma celebração.

        Returns:
            Dict mapping momento (str) -> list of dicts with 'musica' and 'score'.
        """
        resultado = {}

        momentos = MOMENTOS_MISSA if 'missa' in tipo_celebracao else MOMENTOS_MISSA

        for momento in momentos:
            sugestoes = self.recomendar_por_momento(
                momento=momento,
                tempo_liturgico=tempo_liturgico,
                max_resultados=max_por_momento,
            )
            resultado[momento] = sugestoes

        return resultado

    def recomendar_por_momento(
        self,
        momento: str,
        tempo_liturgico: str = '',
        tom: str = '',
        max_resultados: int = 5,
    ) -> list[dict]:
        """
        Recomenda músicas para um momento litúrgico específico.

        Returns:
            List of dicts: [{'musica': Musica, 'score': float, 'razoes': [str]}]
        """
        # Base queryset: only active songs
        qs = Musica.objects.filter(ativo=True).prefetch_related('categorias', 'tags')

        # Try to find the category matching the momento
        categoria = CategoriaLiturgica.objects.filter(
            nome__iexact=momento, ativo=True
        ).first()

        if categoria:
            # Primary: songs with this category
            musicas_com_categoria = qs.filter(categorias=categoria)
        else:
            musicas_com_categoria = qs.none()

        # Score each candidate
        scored = []

        # Usage frequency in recent repertoires
        data_limite = date.today() - timedelta(days=self.dias_recencia)
        uso_recente = self._get_uso_recente(data_limite)

        for musica in musicas_com_categoria.distinct():
            score, razoes = self._calcular_score(
                musica, momento, tempo_liturgico, tom, uso_recente
            )
            scored.append({
                'musica': musica,
                'score': score,
                'razoes': razoes,
            })

        # If not enough candidates, add songs matching tempo litúrgico
        if len(scored) < max_resultados and tempo_liturgico:
            tags_tempo = TEMPO_LITURGICO_FILTERS.get(tempo_liturgico, [])
            if tags_tempo:
                ids_existentes = {s['musica'].pk for s in scored}
                extras = qs.filter(
                    Q(tags__nome__in=tags_tempo) | Q(categorias__nome__in=tags_tempo)
                ).exclude(pk__in=ids_existentes).distinct()

                for musica in extras[:max_resultados]:
                    score, razoes = self._calcular_score(
                        musica, momento, tempo_liturgico, tom, uso_recente
                    )
                    score *= 0.7  # penalize for not having exact category
                    razoes.append('sugestão por tempo litúrgico')
                    scored.append({
                        'musica': musica,
                        'score': score,
                        'razoes': razoes,
                    })

        # Sort by score descending
        scored.sort(key=lambda x: x['score'], reverse=True)

        return scored[:max_resultados]

    def _calcular_score(
        self,
        musica: Musica,
        momento: str,
        tempo_liturgico: str,
        tom: str,
        uso_recente: dict[int, int],
    ) -> tuple[float, list[str]]:
        """Calcula score de relevância para uma música."""
        score = 10.0
        razoes = []

        # 1. Category match (already filtered, so base score)
        razoes.append(f'categoria: {momento}')

        # 2. Tempo litúrgico match via tags
        if tempo_liturgico:
            tags_tempo = TEMPO_LITURGICO_FILTERS.get(tempo_liturgico, [])
            tag_names = set(t.nome.lower() for t in musica.tags.all())
            cat_names = set(c.nome.lower() for c in musica.categorias.all())
            all_names = tag_names | cat_names

            for tag in tags_tempo:
                if tag.lower() in all_names:
                    score += 3.0
                    razoes.append(f'tempo litúrgico: {tempo_liturgico}')
                    break

        # 3. Key preference
        if tom and musica.tom_principal == tom:
            score += 2.0
            razoes.append(f'tom preferencial: {tom}')

        # 4. Recency penalty (used recently = lower score)
        uso = uso_recente.get(musica.pk, 0)
        if uso > 0:
            penalty = min(uso * 2.0, 6.0)
            score -= penalty
            razoes.append(f'usada {uso}x recentemente (-{penalty:.1f})')

        # 5. Completeness bonus (has letra, pdf, audio)
        completeness = 0
        if musica.letra:
            completeness += 1
        if musica.tem_pdf:
            completeness += 1
        if musica.tem_cifra:
            completeness += 1
        if completeness > 0:
            bonus = completeness * 0.5
            score += bonus
            razoes.append(f'material disponível (+{bonus:.1f})')

        return max(score, 0), razoes

    def _get_uso_recente(self, data_limite: date) -> dict[int, int]:
        """Retorna dict {musica_id: count} de uso em repertórios recentes."""
        from apps.repertorios.models import RepertorioMusica
        usage = (
            RepertorioMusica.objects
            .filter(repertorio__data_celebracao__gte=data_limite)
            .values('musica_id')
            .annotate(count=Count('id'))
        )
        return {item['musica_id']: item['count'] for item in usage}

    def sugerir_substituicao(
        self,
        musica_atual: Musica,
        momento: str,
        tempo_liturgico: str = '',
    ) -> list[dict]:
        """
        Sugere substituições para uma música específica em um momento.
        Exclui a música atual dos resultados.
        """
        sugestoes = self.recomendar_por_momento(
            momento=momento,
            tempo_liturgico=tempo_liturgico,
            tom=musica_atual.tom_principal,
            max_resultados=6,
        )
        return [s for s in sugestoes if s['musica'].pk != musica_atual.pk][:5]
