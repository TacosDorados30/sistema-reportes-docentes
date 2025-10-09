# Sistema de Reportes Docentes

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

Sistema web completo para la gestión, análisis y generación automática de reportes de actividades académicas de docentes. Desarrollado con Python y Streamlit, incluye funcionalidades avanzadas de procesamiento de datos, monitoreo de rendimiento y sistema de backup.

## 🚀 Características Principales

### 📝 Gestión de Formularios
- **Formulario público** sin autenticación para docentes
- **Validación automática** de datos en tiempo real
- **Campos dinámicos** para múltiples entradas
- **Soporte para período académico** (año y trimestre)

### 👩‍💼 Panel Administrativo
- **Autenticación segura** con hash de contraseñas
- **Revisión y aprobación** de formularios
- **Dashboard interactivo** con métricas en tiempo real
- **Gestión de usuarios** y sesiones

### 📊 Análisis de Datos
- **Procesamiento automático** de datos aprobados
- **Detección de duplicados** con algoritmos avanzados
- **Cálculo de métricas** por trimestre y año
- **Visualizaciones interactivas** con Plotly

### 📄 Generación de Reportes
- **Reportes narrativos automáticos** usando NLG
- **Múltiples formatos**: PDF, Excel, PowerPoint
- **Templates personalizables** con Jinja2
- **Historial de reportes** generados

### 📤 Exportación de Datos
- **Excel multi-hoja** con datos estructurados
- **CSV** para análisis externos
- **Filtros avanzados** por fecha y categoría
- **Metadatos incluidos** en exportaciones

### 💾 Sistema de Backup
- **Backup automático** de base de datos
- **Verificación de integridad** de backups
- **Importación/exportación** en formato JSON
- **Gestión completa** desde el dashboard

### 📈 Monitoreo de Rendimiento
- **Métricas en tiempo real** (CPU, memoria, disco)
- **Monitoreo de queries** de base de datos
- **Sistema de alertas** configurables
- **Dashboard de rendimiento** interactivo

### 🔍 Auditoría y Logging
- **Registro completo** de todas las acciones
- **Logs estructurados** con múltiples niveles
- **Trazabilidad** de cambios y decisiones
- **Exportación de logs** para análisis

## 🛠️ Tecnologías

### Backend
- **Python 3.9+**: Lenguaje principal
- **Streamlit 1.28+**: Framework web
- **SQLAlchemy 2.0+**: ORM para base de datos
- **Pandas 2.1+**: Procesamiento de datos
- **Pydantic 2.5+**: Validación de datos

### Base de Datos
- **SQLite**: Desarrollo y producción pequeña
- **PostgreSQL**: Producción escalable
- **Índices optimizados** para rendimiento

### Visualización
- **Plotly 5.17+**: Gráficos interactivos
- **Matplotlib 3.8+**: Gráficos estáticos
- **Seaborn 0.13+**: Visualizaciones estadísticas

### Reportes
- **Jinja2 3.1+**: Templates de reportes
- **ReportLab 4.0+**: Generación de PDFs
- **OpenPyXL 3.1+**: Archivos Excel
- **python-pptx 0.6+**: Presentaciones PowerPoint

### Monitoreo
- **psutil 5.9+**: Métricas del sistema
- **Custom monitoring**: Sistema propio de rendimiento

## 📦 Instalación

### Requisitos Previos
- Python 3.9 o superior
- Git
- 2GB RAM mínimo (recomendado 4GB)
- 10GB espacio en disco

### Instalación Local

1. **Clonar el repositorio**:
```bash
git clone https://github.com/tu-usuario/sistema-reportes-docentes.git
cd sistema-reportes-docentes
```

2. **Crear entorno virtual**:
```bash
python -m venv venv

# En Linux/Mac:
source venv/bin/activate

# En Windows:
venv\Scripts\activate
```

3. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**:
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar configuración
nano .env
```

5. **Inicializar la aplicación**:
```bash
python -c "
from app.startup import startup_application
result = startup_application()
print('✅ Application initialized:', result['status'])
"
```

6. **Ejecutar la aplicación**:
```bash
# Dashboard administrativo
streamlit run dashboard/streamlit_app.py

# O usar el script de inicio
python start_system.py
```

## 🚀 Despliegue

### Streamlit Cloud (Recomendado)

1. **Conectar repositorio** en [share.streamlit.io](https://share.streamlit.io)
2. **Configurar archivo principal**: `dashboard/streamlit_app.py`
3. **Agregar secrets** en el panel de Streamlit Cloud
4. **Desplegar automáticamente**

Ver [Guía Completa de Despliegue](docs/GUIA_DESPLIEGUE_COMPLETA.md) para instrucciones detalladas.

### Heroku

```bash
# Crear aplicación
heroku create tu-app-name

# Configurar variables
heroku config:set SECRET_KEY="tu-clave-secreta"
heroku config:set ADMIN_PASSWORD_HASH="tu-hash-de-contraseña"

# Desplegar
git push heroku main
```

## 📖 Uso

### Acceso Administrativo
- **URL**: `http://localhost:8501` (local) o tu dominio de producción
- **Usuario**: `admin`
- **Contraseña**: Configurada en variables de entorno

### Formulario Público
- **URL**: `http://localhost:8501/public_form`
- **Acceso**: Sin autenticación requerida
- **Funcionalidad**: Envío de reportes académicos

## 📁 Estructura del Proyecto

```
sistema-reportes-docentes/
├── 📁 app/                          # Aplicación principal
│   ├── 📁 auth/                     # Sistema de autenticación
│   ├── 📁 core/                     # Lógica de negocio
│   │   ├── 📄 audit_logger.py       # Sistema de auditoría
│   │   ├── 📄 data_processor.py     # Procesamiento de datos
│   │   ├── 📄 metrics_calculator.py # Cálculo de métricas
│   │   ├── 📄 performance_monitor.py # Monitoreo de rendimiento
│   │   └── 📄 ...
│   ├── 📁 database/                 # Capa de datos
│   ├── 📁 models/                   # Modelos de datos
│   └── 📁 utils/                    # Utilidades
├── 📁 dashboard/                    # Interfaz Streamlit
│   ├── 📄 streamlit_app.py          # Aplicación principal
│   ├── 📄 public_form.py            # Formulario público
│   └── 📁 pages/                    # Páginas del dashboard
├── 📁 docs/                         # Documentación
├── 📁 tests/                        # Pruebas
├── 📄 requirements.txt              # Dependencias Python
└── 📄 README.md                     # Este archivo
```

## 🧪 Pruebas

### Ejecutar Todas las Pruebas
```bash
# Pruebas de integración completas
python test_integration_complete.py

# Pruebas del sistema de backup
python test_backup_system.py

# Pruebas de monitoreo de rendimiento
python test_performance_monitoring.py
```

## 📚 Documentación

- **[Manual del Administrador](docs/MANUAL_ADMINISTRADOR.md)**: Guía completa para usuarios
- **[Documentación Técnica](docs/DOCUMENTACION_TECNICA.md)**: Detalles técnicos y arquitectura
- **[Guía de Despliegue](docs/GUIA_DESPLIEGUE_COMPLETA.md)**: Instrucciones de despliegue

## 🤝 Contribuir

1. **Fork** el proyecto
2. **Crear rama** para feature (`git checkout -b feature/nueva-funcionalidad`)
3. **Desarrollar** y probar cambios
4. **Ejecutar pruebas**: `python test_integration_complete.py`
5. **Commit** cambios (`git commit -am 'Agregar nueva funcionalidad'`)
6. **Push** a la rama (`git push origin feature/nueva-funcionalidad`)
7. **Crear Pull Request**

## 📄 Licencia

Este proyecto está bajo la **Licencia MIT**. Ver [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- **Streamlit Team**: Por el excelente framework web
- **Plotly**: Por las visualizaciones interactivas
- **SQLAlchemy**: Por el ORM robusto y flexible
- **Pandas**: Por las herramientas de análisis de datos

---

**¡Gracias por usar el Sistema de Reportes Docentes!** 🎉

**Versión**: 1.0.0 | **Estado**: Producción | **Actualizado**: Octubre 2024