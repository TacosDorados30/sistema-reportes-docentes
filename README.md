# 📊 Sistema de Reportes Docentes

Sistema web optimizado para la recolección y gestión de actividades académicas de docentes universitarios.

## 🚀 Inicio Rápido

### Instalación
```bash
git clone <url-del-repositorio>
cd sistema-reportes-docentes
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Ejecutar Sistema
```bash
python run_unified.py
```
**URL**: http://localhost:8501  
**Admin**: admin / admin123

## 📋 Características Principales

- ✅ **Formulario Público**: Interfaz optimizada para docentes
- ✅ **Panel Admin**: Dashboard con métricas en tiempo real  
- ✅ **8 Categorías**: Cursos, publicaciones, eventos, diseño curricular, movilidad, reconocimientos, certificaciones, otras
- ✅ **Reportes Múltiples**: PDF, Excel, PowerPoint, Markdown
- ✅ **Visualizaciones**: Gráficos interactivos con Plotly
- ✅ **Notificaciones**: Sistema de emails automáticos
- ✅ **Versionado**: Sistema de correcciones con tokens
- ✅ **Auditoría**: Registro completo de acciones

## 🛠️ Scripts de Utilidad

```bash
# Limpiar datos
python reset_db.py              # Toda la base de datos
python reset_maestros.py        # Solo maestros

# Optimización
python scripts/cleanup_system.py   # Limpiar archivos temporales

# Datos de prueba  
python scripts/add_sample_data.py  # Formularios de ejemplo
```

## 📁 Estructura Optimizada

```
sistema-reportes-docentes/
├── app/                 # Lógica de negocio
├── dashboard/           # Interfaz Streamlit  
├── scripts/            # Utilidades y limpieza
├── data/               # Base de datos
├── reports/            # Reportes generados
└── run_unified.py      # Launcher principal
```

## ⚙️ Configuración (.env)

```env
DATABASE_URL=sqlite:///reportes_docentes.db
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password
SECRET_KEY=tu-clave-secreta
DEBUG=false
```

## 🔧 Optimizaciones Implementadas

- **Carga Lazy**: Imports bajo demanda
- **Cache**: Métricas con TTL de 10 minutos  
- **Logs Mínimos**: Solo warnings y errores
- **Startup Rápido**: Inicialización silenciosa
- **Limpieza Auto**: Scripts de mantenimiento

## 📊 Funcionalidades por Rol

### Docentes
- Formulario público sin login
- Validación en tiempo real
- Guardado automático cada 30s
- Confirmación de envío

### Administradores  
- Dashboard con métricas
- Gestión CRUD de maestros
- Revisión y aprobación de formularios
- Generación de reportes en 4 formatos
- Sistema de notificaciones masivas
- Seguimiento de maestros pendientes

## 🚀 Despliegue

### Streamlit Cloud
1. Push a GitHub
2. Conectar en Streamlit Cloud  
3. Configurar variables de entorno
4. Deploy automático

### Local Optimizado
```bash
python run_unified.py  # Configuración de producción
```

## 🔍 Solución de Problemas

```bash
# Dependencias
pip install --upgrade -r requirements.txt

# Base de datos corrupta
python reset_db.py

# Limpieza completa
python scripts/cleanup_system.py
```

## 📈 Métricas del Sistema

- **32 archivos** de código principal
- **~3,200 líneas** implementadas  
- **8 módulos** completamente funcionales
- **4 formatos** de reporte
- **100% funcional** en producción

---

**Sistema optimizado para máximo rendimiento y facilidad de uso** 🎯