# 🚀 Guía de Despliegue

## Configuración Inicial para Producción

### 1. Configurar Variables de Entorno

**IMPORTANTE:** Cada instalación debe configurar su propio archivo `.env`

1. **Copiar archivo de ejemplo:**
   ```bash
   copy .env.example .env
   ```

2. **Editar `.env` y configurar:**
   - `EMAIL_USER` - Tu email de Gmail
   - `EMAIL_PASSWORD` - Contraseña de aplicación de Gmail
   - `SECRET_KEY` - Clave secreta aleatoria
   - `JWT_SECRET` - Otra clave secreta aleatoria

**Nota:** El archivo `.env` NO se sube a git por seguridad.

### 2. Configurar Administrador

Editar `auth_config.json`:
```json
{
  "admin_users": {
    "admin": {
      "email": "admin@tu-universidad.edu.mx",
      "name": "Nombre del Administrador"
    }
  }
}
```

### 3. Configurar Email de Gmail

1. Ir a https://myaccount.google.com/security
2. Activar "Verificación en 2 pasos"
3. Ir a "Contraseñas de aplicaciones"
4. Generar una contraseña para "Correo"
5. Copiar la contraseña generada a `EMAIL_PASSWORD` en `.env`

### 4. Inicializar Base de Datos

```bash
# Limpiar datos de prueba
.\venv\Scripts\python.exe reset_db.py
.\venv\Scripts\python.exe reset_maestros.py
```

### 5. Ejecutar Sistema

```bash
python run_unified.py
```

## Seguridad

### Archivos que NO deben subirse a Git:
- ✅ `.env` - Credenciales y configuración
- ✅ `auth_config.json` - Usuarios y contraseñas
- ✅ `*.db` - Base de datos
- ✅ `uploads/` - Archivos subidos
- ✅ `reports/` - Reportes generados
- ✅ `logs/` - Archivos de log

### Cambiar Contraseña del Administrador

1. Iniciar sesión con email: `admin@sistema.edu.mx`
2. Ir a "⚙️ Administración" → "🔑 Cambiar Contraseña y Email"
3. Configurar nueva contraseña segura

## Mantenimiento

### Limpiar Archivos Temporales
```bash
python scripts/cleanup_system.py
```

### Backup de Base de Datos
```bash
copy reportes_docentes.db backups\reportes_docentes_YYYYMMDD.db
```

### Ver Logs
```bash
type logs\app.log
```

## Soporte

Para problemas o preguntas, contactar al equipo de desarrollo.
