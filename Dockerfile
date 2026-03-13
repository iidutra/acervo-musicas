FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/prod.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=config.settings.prod

RUN SECRET_KEY=build-placeholder python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["python", "-c", "import subprocess, os; port = os.environ.get('PORT', '8000'); subprocess.run(['python', 'manage.py', 'migrate', '--noinput']); os.execvp('gunicorn', ['gunicorn', 'config.wsgi:application', '--bind', f'0.0.0.0:{port}', '--workers', '3', '--timeout', '120'])"]
