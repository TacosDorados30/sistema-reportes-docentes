# Sistema de Reportes Docentes

Sistema integral para la gestión y reporte de actividades académicas del cuerpo docente universitario.

## 🚀 Características Principales

- **Formulario Público**: Interfaz web para que los docentes reporten sus actividades
- **Dashboard Administrativo**: Panel de control para revisar y aprobar formularios
- **Procesamiento Inteligente**: Análisis automático de datos y detección de duplicados
- **Reportes Automáticos**: Generación de reportes trimestrales y anuales
- **Exportación Multi-formato**: CSV, Excel, JSON, PDF, PowerPoint
- **Sistema de Auditoría**: Registro completo de todas las acciones administrativas
- **Monitoreo de Salud**: Health checks y métricas de rendimiento

## 📋 Requisitos del Sistema

### Requisitos Mínimos
- Python 3.8+
- 2GB RAM
- 1GB espacio en disco
- Conexión a internet

### Dependencias Principales
- Streamlit 1.28.1
- FastAPI 0.104.1
- SQLAlchemy 2.0.23
- Pandas 2.1.3
- Plotly 5.17.0

## 🛠️ Instalación Local

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd sistema-reportes-docentes
```

### 2. Crear Entorno Virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

### 5. Inicializar Base de Datos
```bash
python -c "from app.database.connection import init_database; init_database()"
```

### 6. Ejecutar la Aplicación
```bash
streamlit run dashboard/streamlit_app.py
```

## ☁️ Despliegue en Streamlit Cloud

### Preparación del Repositorio

1. **Subir a GitHub**:
   ```bash
   git add .
   git commit -m "Deploy to Streamlit Cloud"
   git push origin main
   ```

2. **Configurar Secretos**:
   - Ve a [share.streamlit.io](https://share.streamlit.io)
   - Conecta tu repositorio de GitHub
   - Configura los secretos en el dashboard

### Configuración de Secretos en Streamlit Cloud

En el dashboard de Streamlit Cloud, agrega estos secretos:

```toml
[database]
DATABASE_URL = "sqlite:///./data/reportes_docentes.db"

[auth]
SECRET_KEY = "tu-clave-secreta-super-segura-aqui"
JWT_SECRET = "tu-jwt-secret-aqui"
ADMIN_PASSWORD_HASH = "$2b$12$tu.hash.de.password.aqui"

[app]
ENVIRONMENT = "production"
DEBUG = false
LOG_LEVEL = "INFO"
```

### Configuración del Repositorio

1. **Archivo Principal**: `dashboard/streamlit_app.py`
2. **Versión de Python**: 3.8+
3. **Dependencias**: `requirements.txt`
4. **Configuración**: `.streamlit/config.toml`

## 🔧 Configuración Avanzada

### Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `DATABASE_URL` | URL de la base de datos | `sqlite:///./data/reportes_docentes.db` |
| `SECRET_KEY` | Clave secreta para autenticación | `dev-secret-key` |
| `ENVIRONMENT` | Entorno de ejecución | `development` |
| `DEBUG` | Modo debug | `false` |
| `LOG_LEVEL` | Nivel de logging | `INFO` |

### Configuración de Base de Datos

#### SQLite (Desarrollo)
```python
DATABASE_URL = "sqlite:///./data/reportes_docentes.db"
```

#### PostgreSQL (Producción)
```python
DATABASE_URL = "postgresql://user:password@host:port/database"
```

### Configuración de Autenticación

1. **Generar Hash de Password**:
   ```python
   from passlib.context import CryptContext
   pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
   hash = pwd_context.hash("tu_password")
   print(hash)
   ```

2. **Configurar en Secretos**:
   ```toml
   [auth]
   ADMIN_PASSWORD_HASH = "hash_generado_aqui"
   ```

## 📊 Monitoreo y Salud del Sistema

### Health Checks

El sistema incluye endpoints de monitoreo:

- **Health Check Simple**: `/health`
- **Health Check Detallado**: `/health/detailed`
- **Readiness Probe**: `/health/readiness`
- **Liveness Probe**: `/health/liveness`

### Métricas de Rendimiento

- Tiempo de respuesta de consultas
- Uso de recursos del sistema
- Estadísticas de base de datos
- Logs de auditoría

## 🔒 Seguridad

### Mejores Prácticas Implementadas

- ✅ Autenticación segura con hash de passwords
- ✅ Validación de entrada de datos
- ✅ Sanitización de inputs
- ✅ Logging de auditoría completo
- ✅ Manejo seguro de errores
- ✅ Configuración de CORS apropiada

### Configuración de Seguridad

1. **Cambiar Claves por Defecto**:
   - Generar `SECRET_KEY` único
   - Crear password de administrador seguro
   - Configurar JWT secret

2. **Configurar HTTPS** (en producción):
   - Streamlit Cloud maneja HTTPS automáticamente
   - Para despliegues propios, configurar certificados SSL

## 📁 Estructura del Proyecto

```
sistema-reportes-docentes/
├── app/                          # Lógica de aplicación
│   ├── api/                      # Endpoints FastAPI
│   ├── auth/                     # Sistema de autenticación
│   ├── core/                     # Funcionalidades centrales
│   ├── database/                 # Modelos y CRUD
│   ├── models/                   # Modelos de datos
│   ├── reports/                  # Generación de reportes
│   └── utils/                    # Utilidades
├── dashboard/                    # Interfaz Streamlit
│   └── pages/                    # Páginas del dashboard
├── static/                       # Archivos estáticos
├── templates/                    # Plantillas HTML
├── data/                         # Base de datos
├── logs/                         # Archivos de log
├── reports/                      # Reportes generados
├── .streamlit/                   # Configuración Streamlit
├── requirements.txt              # Dependencias Python
├── packages.txt                  # Dependencias del sistema
└── README.md                     # Este archivo
```

## 🧪 Testing

### Ejecutar Pruebas

```bash
# Prueba integral del sistema
python test_sistema_completo.py

# Pruebas específicas
python test_audit_final.py
python test_error_handling_final.py
python test_cloud_optimization.py
```

### Pruebas Incluidas

- ✅ Inicialización del sistema
- ✅ Conexión a base de datos
- ✅ Validación y manejo de errores
- ✅ Sistema de auditoría
- ✅ Procesamiento de datos
- ✅ Exportación de datos
- ✅ Generación de reportes
- ✅ Autenticación
- ✅ Health checks
- ✅ Optimización de rendimiento

## 🚨 Troubleshooting

### Problemas Comunes

#### Error de Base de Datos
```bash
# Reinicializar base de datos
python -c "from app.database.connection import init_database; init_database()"
```

#### Error de Dependencias
```bash
# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

#### Error de Permisos
```bash
# Verificar permisos de directorios
chmod 755 data/ logs/ reports/
```

### Logs y Debugging

- **Logs de aplicación**: `logs/application.log`
- **Logs de auditoría**: Base de datos tabla `audit_logs`
- **Health checks**: `/health/detailed`

## 📞 Soporte

### Información del Sistema

- **Versión**: 1.0.0
- **Autor**: Sistema de Reportes Docentes
- **Licencia**: MIT

### Contacto

Para soporte técnico o preguntas:
- Revisar logs del sistema
- Ejecutar health checks
- Consultar documentación de troubleshooting

## 🔄 Actualizaciones

### Proceso de Actualización

1. **Backup de datos**:
   ```bash
   cp data/reportes_docentes.db data/backup_$(date +%Y%m%d).db
   ```

2. **Actualizar código**:
   ```bash
   git pull origin main
   pip install -r requirements.txt
   ```

3. **Migrar base de datos** (si es necesario):
   ```bash
   python -c "from app.database.connection import init_database; init_database()"
   ```

4. **Verificar funcionamiento**:
   ```bash
   python test_sistema_completo.py
   ```

## 📈 Roadmap

### Próximas Funcionalidades

- [ ] Integración con sistemas universitarios existentes
- [ ] Notificaciones por email
- [ ] API REST completa
- [ ] Dashboard móvil
- [ ] Análisis predictivo
- [ ] Integración con calendarios académicos

---

**¡El sistema está listo para producción!** 🚀

Para comenzar, sigue las instrucciones de instalación local o despliegue en Streamlit Cloud.