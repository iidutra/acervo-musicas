"""
Management command para enriquecer links externos com metadados.

Usage:
    python manage.py enrich_links
    python manage.py enrich_links --provider youtube
    python manage.py enrich_links --limit 50
"""
from django.core.management.base import BaseCommand

from apps.arquivos.models import LinkExterno
from apps.integracoes.services import enrich_link


class Command(BaseCommand):
    help = 'Enriquece links externos com metadados das plataformas (título, thumbnail, embed)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--provider',
            type=str,
            help='Filtrar por provider (youtube, spotify, etc.)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Limite de links a processar (default: 100)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Reprocessar mesmo links que já têm metadados',
        )

    def handle(self, *args, **options):
        qs = LinkExterno.objects.all()

        if options['provider']:
            qs = qs.filter(provider=options['provider'])

        if not options['force']:
            qs = qs.filter(titulo_externo='')

        qs = qs[:options['limit']]

        total = qs.count()
        updated = 0
        errors = 0

        self.stdout.write(f'Processando {total} links...')

        for link in qs:
            try:
                if enrich_link(link):
                    updated += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'  [OK] {link.url} -> "{link.titulo_externo}"')
                    )
                else:
                    self.stdout.write(f'  [--] {link.url} (sem metadados)')
            except Exception as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(f'  [ERRO] {link.url}: {e}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nConcluído: {updated} atualizados, {errors} erros, {total - updated - errors} sem alteração.'
            )
        )
