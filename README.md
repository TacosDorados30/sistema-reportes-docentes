# 📊 Sistema de Reportes Docentes

Sistema completo para la gestión y análisis de reportes de actividades académicas de docentes.

## 🚀 Inicio Rápido

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Iniciar el Sistema
```bash
python start_system.py
```

### 3. Acceder al Sistema
- **URL:** Se mostrará automáticamente al iniciar (generalmente http://localhost:8501 o similar)
- **Usuario:** `admin`
- **Contraseña:** `admin123`

## 📋 Funcionalidades

### ✅ Para Docentes
- Formulario de envío de actividades académicas
- Seguimiento del estado de sus reportes
- Interfaz intuitiva y fácil de usar

### ✅ Para Administradores
- **Panel de Control:** Dashboard con métricas generales
- **Revisión de Formularios:** Aprobar/rechazar reportes pendientes
- **Análisis de Datos:** Visualizaciones y estadísticas detalladas
- **Exportación:** Datos en Excel, PDF y otros formatos
- **Reportes:** Generación automática de informes
- **Auditoría:** Logs completos de todas las actividades

## 🏗️ Estructura del Proyecto

```
├── app/                    # Lógica de negocio
│   ├── auth/              # Sistema de autenticación
│   ├── core/              # Funcionalidades principales
│   ├── database/          # Modelos y conexión a BD
│   └── models/            # Esquemas de datos
├── dashboard/             # Interfaz web (Streamlit)
│   └── pages/            # Páginas específicas
├── data/                  # Base de datos SQLite
├── logs/                  # Archivos de log
├── reports/               # Reportes generados
└── uploads/               # Archivos subidos
```

## 🔧 Configuración

### Variables de Entorno (.env)
```env
DATABASE_URL=sqlite:///./data/reportes_docentes.db
SECRET_KEY=tu-clave-secreta
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

### Base de Datos
- **Por defecto:** SQLite (ideal para desarrollo)
- **Producción:** PostgreSQL recomendado
- **Inicialización:** Automática al primer inicio

## 🛠️ Comandos Útiles

### Probar el Sistema
```bash
python test_fixes.py
```

### Ejecutar Solo Streamlit
```bash
streamlit run dashboard/streamlit_app.py
```

### Ver Logs
```bash
# Logs de aplicación
tail -f logs/application.log

# Logs de auditoría
tail -f logs/audit.log
```

## 📊 Tipos de Datos Soportados

### Actividades Académicas
- **Cursos y Capacitaciones:** Nombre, fecha, horas
- **Publicaciones:** Autores, título, revista/evento, estatus
- **Eventos Académicos:** Participación en congresos, seminarios
- **Diseño Curricular:** Desarrollo de cursos y programas
- **Movilidad Académica:** Intercambios, estancias
- **Reconocimientos:** Premios, distinciones
- **Certificaciones:** Certificados profesionales

### Estados de Formularios
- **Pendiente:** Esperando revisión
- **Aprobado:** Validado por administrador
- **Rechazado:** Requiere correcciones

## 🔐 Seguridad

- Autenticación basada en sesiones
- Validación de datos de entrada
- Logs de auditoría completos
- Protección CSRF habilitada
- Sanitización de datos

## 📈 Métricas y Análisis

### Dashboard Principal
- Resumen de formularios por estado
- Distribución de actividades académicas
- Actividad reciente del sistema

### Análisis Avanzado
- Tendencias temporales
- Comparaciones por período
- Estadísticas de calidad de datos
- Reportes personalizables

## 🚨 Solución de Problemas

### Error de Puerto Ocupado
```bash
# Verificar procesos en puerto 8501
netstat -ano | findstr :8501

# Matar proceso si es necesario
taskkill /PID <PID> /F
```

### Error de Base de Datos
```bash
# Eliminar base de datos y reinicializar
rm data/reportes_docentes.db
python start_system.py
```

### Problemas de Dependencias
```bash
# Reinstalar dependencias
pip install --upgrade -r requirements.txt
```

## 📞 Soporte

Para problemas o sugerencias:
1. Revisar los logs en `logs/application.log`
2. Ejecutar `python test_fixes.py` para diagnóstico
3. Verificar la configuración en `.env`

## 🔄 Actualizaciones

El sistema se actualiza automáticamente:
- Base de datos: Migraciones automáticas
- Configuración: Valores por defecto seguros
- Logs: Rotación automática

---

**Versión:** 1.0.0  
**Última actualización:** Octubre 2025