FROM python:3.12-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Configurar el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para PostgreSQL y WeasyPrint (pdf)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        libpq-dev \
        gcc \
        pkg-config \
        libcairo2-dev \
        python3-dev \
        musl-dev \
        libpango-1.0-0 \
        libharfbuzz0b \
        libpangoft2-1.0-0 \
        libffi-dev \
        libjpeg-dev \
        libopenjp2-7-dev \
        graphviz \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiar el proyecto
COPY . /app/

# Crear directorios para estáticos y medios (opcional, docker-compose los mapeará)
RUN mkdir -p /app/staticfiles /app/media

# Exponer el puerto
EXPOSE 8000
