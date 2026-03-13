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

RUN printf '#!/bin/bash\nset -e\npython manage.py migrate --noinput\nexec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120\n' > /app/start.sh && chmod +x /app/start.sh

EXPOSE 8000

CMD ["/bin/bash", "/app/start.sh"]
