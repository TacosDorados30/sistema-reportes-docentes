# Sistema de Reportes Docentes

Sistema de Data Science para la recolección, análisis y generación automática de reportes académicos.

## Características

- Formulario web público sin registro
- Panel administrativo para validación
- Procesamiento automático de datos
- Dashboard con visualizaciones interactivas
- Generación automática de reportes (narrativos y tabulares)
- Despliegue en la nube

## Instalación

1. Clonar el repositorio
2. Instalar dependencias: `pip install -r requirements.txt`
3. Copiar `.env.template` a `.env` y configurar
4. Ejecutar: `streamlit run dashboard/streamlit_app.py`

## Estructura del Proyecto

```
sistema-reportes-docentes/
├── app/                 # Backend FastAPI
├── dashboard/           # Frontend Streamlit
├── static/             # Archivos estáticos
├── templates/          # Templates de reportes
└── tests/              # Pruebas
```

## Uso

1. Acceder al formulario público via URL
2. Los docentes llenan y envían información
3. La administradora revisa y aprueba formularios
4. El sistema genera reportes automáticamente

## Tecnologías

- Python 3.9+
- FastAPI + Streamlit
- SQLite
- Pandas + Plotly
- ReportLab + OpenPyXL