# Dockerfile para Sistema de Reportes Docentes
# Uso: docker build -t reportes-docentes .
#      docker run -p 8501:8501 reportes-docentes

FROM python:3.8-slim

# Información del mantenedor
LABEL maintainer="Sistema de Reportes Docentes"
LABEL version="1.0.0"
LABEL description="Sistema integral para gestión de reportes académicos"

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libfreetype6-dev \
    libfontconfig1-dev \
    libjpeg-dev \
    libpng-dev \
    libssl-dev \
    libffi-dev \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt .
COPY packages.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p data logs reports uploads backups && \
    chown -R app:app /app

# Cambiar a usuario no-root
USER app

# Inicializar base de datos
RUN python -c "from app.database.connection import init_database; init_database()"

# Exponer puerto
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from app.core.health_check import get_simple_health; health = get_simple_health(); exit(0 if health['status'] == 'healthy' else 1)"

# Comando por defecto
CMD ["streamlit", "run", "dashboard/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]