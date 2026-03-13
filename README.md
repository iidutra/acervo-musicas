# Acervo Litúrgico Digital

## Visão Geral
Sistema para centralizar e organizar o acervo musical de uma comunidade/ministério de música. Permite gerenciar músicas, letras, tons, categorias litúrgicas, PDFs próprios, gravações de ensaio, links externos de referência, cifras e repertórios por celebração.

## Stack
- Backend: Django 5.1
- Banco de dados: PostgreSQL
- Frontend: Django Templates + Tailwind CSS (CDN)
- API REST: Django REST Framework + drf-spectacular (Swagger)
- Leitura de PDF: PyMuPDF
- Importação/Exportação: pandas + openpyxl
- Player de áudio: HTML5 nativo
- Autenticação: Django auth + Token auth (API)
- Testes: pytest + pytest-django + factory-boy

## Requisitos
- Docker e Docker Compose **ou**
- Python 3.11+ e PostgreSQL 14+

## Como Rodar com Docker (recomendado)

### 1. Clonar o repositório
```bash
git clone <url-do-repositorio>
cd musicas
```

### 2. Configurar variáveis de ambiente
```bash
cp .env.example .env
```

O `.env` já vem configurado para funcionar com Docker (`DB_HOST=db`).

### 3. Subir os containers
```bash
docker compose up -d --build
```

### 4. Aplicar migrations
```bash
docker compose exec web python manage.py migrate
```

### 5. Criar superusuário
```bash
docker compose exec web python manage.py createsuperuser
```

### 6. Acessar
- Aplicação: http://localhost:8000
- Admin: http://localhost:8000/admin/

### Comandos úteis
```bash
docker compose logs -f web          # ver logs
docker compose exec web bash        # shell no container
docker compose down                 # parar containers
docker compose down -v              # parar e remover volumes
```

---

## Como Rodar sem Docker

### 1. Clonar o repositório
```bash
git clone <url-do-repositorio>
cd musicas
```

### 2. Criar ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instalar dependências
```bash
pip install -r requirements/dev.txt
```

### 4. Configurar variáveis de ambiente
```bash
cp .env.example .env
# Editar .env: trocar DB_HOST=db para DB_HOST=localhost
```

### 5. Criar banco de dados PostgreSQL
```sql
CREATE DATABASE acervo_liturgico;
CREATE USER acervo_user WITH PASSWORD 'sua_senha';
GRANT ALL PRIVILEGES ON DATABASE acervo_liturgico TO acervo_user;
```

### 6. Aplicar migrations
```bash
python manage.py migrate
```

### 7. Criar superusuário
```bash
python manage.py createsuperuser
```

### 8. Rodar servidor
```bash
python manage.py runserver
```

Acessar: http://localhost:8000

Admin: http://localhost:8000/admin/

## Estrutura do Projeto
```
musicas/
├── config/                  # Configurações Django
│   ├── settings/
│   │   ├── base.py         # Settings base
│   │   ├── dev.py          # Settings desenvolvimento
│   │   └── prod.py         # Settings produção
│   ├── urls.py             # URLs raiz
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── core/               # Dashboard, utilitários, normalização de tom
│   ├── musicas/            # Músicas, categorias litúrgicas, tags
│   ├── arquivos/           # PDFs, áudios, cifras, links externos
│   ├── repertorios/        # Repertórios, recomendação de repertório
│   ├── importacao_exportacao/  # Importação e exportação de acervo
│   ├── integracoes/        # Integrações externas (YouTube, Spotify)
│   ├── agenda/             # Agenda litúrgica e celebrações
│   └── api/                # API REST (DRF)
├── tests/                  # Testes automatizados
├── templates/              # Templates Django
├── static/                 # Arquivos estáticos
├── media/                  # Uploads (não versionado)
├── requirements/           # Dependências Python
├── manage.py
├── pytest.ini
├── conftest.py
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Principais Módulos

### Músicas
Cadastro completo com título, letra, tom (com normalização automática), categorias litúrgicas e tags. Suporta inativação sem exclusão física.

### Arquivos
Upload de PDFs próprios (com extração automática de texto), gravações de ensaio (com player HTML5), cifras (texto, PDF ou link) e links externos de referência (YouTube, Spotify, etc.).

### Repertórios
Montagem de repertórios por celebração com ordenação de músicas, categoria litúrgica por momento e tom específico. Exportação para impressão.

### Importação/Exportação
- **Importar:** CSV, Excel, JSON ou ZIP
- **Exportar:** CSV, Excel, JSON ou ZIP (com opção de incluir mídias)
- Validação, log de processamento e histórico de lotes

### Integrações Externas
Enriquecimento automático de links externos com metadados (título, thumbnail, embed URL) via oEmbed:
- YouTube (sem API key)
- Spotify (sem API key)
- Sites genéricos (extração de título)
- Signal automático ao criar link + management command `enrich_links`

### Recomendação de Repertório
Motor de recomendação que sugere músicas para cada momento litúrgico:
- Baseado em categorias litúrgicas, tempo litúrgico, frequência de uso e material disponível
- Penaliza músicas usadas recentemente
- Bonifica músicas com letra, cifra e PDF disponíveis
- Acessível via interface web e API

### Agenda Litúrgica
Calendário mensal de celebrações com:
- Visão de calendário com navegação por mês
- Vínculo com repertórios e tempos litúrgicos
- CRUD completo de celebrações
- Cores por tipo de celebração

### API REST
API completa via Django REST Framework:
- Endpoints para todos os recursos (músicas, categorias, tags, PDFs, áudios, links, cifras, repertórios, celebrações)
- Autenticação via Session e Token
- Filtros, busca e ordenação
- Documentação Swagger em `/api/docs/`
- Actions customizadas (toggle ativo, estatísticas, recomendações)

### Testes
Suite de testes com pytest:
- Testes de models, views, services, API e integrações
- Factories com factory-boy
- Mocking de serviços externos

## Normalização de Tom
O sistema normaliza automaticamente tons em português para notação padrão:
- "Dó" → C
- "Lá menor" → Am
- "Si bemol" → Bb
- "Fá sustenido menor" → F#m

## Comandos Úteis

```bash
# Rodar testes
pytest
pytest --cov=apps              # com cobertura
pytest tests/test_api.py       # apenas API
pytest -k "test_import"        # filtrar por nome

# Enriquecer links externos com metadados
python manage.py enrich_links
python manage.py enrich_links --provider youtube --limit 50

# API docs
# http://localhost:8000/api/docs/    (Swagger UI)
# http://localhost:8000/api/schema/  (OpenAPI schema)
```

## Próximos Passos
- [ ] Suporte a múltiplas comunidades
- [ ] OCR melhorado para PDFs
- [x] Integrações externas (YouTube, Spotify)
- [x] Recomendação de repertório
- [x] Agenda litúrgica
- [x] Docker Compose para desenvolvimento
- [x] Testes automatizados
- [x] API REST
