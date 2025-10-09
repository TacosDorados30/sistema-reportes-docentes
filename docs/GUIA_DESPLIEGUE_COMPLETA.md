# Guía Completa de Despliegue - Sistema de Reportes Docentes

## Índice
1. [Preparación para Despliegue](#preparación-para-despliegue)
2. [Despliegue en Streamlit Cloud](#despliegue-en-streamlit-cloud)
3. [Despliegue en Heroku](#despliegue-en-heroku)
4. [Despliegue en VPS/Servidor Propio](#despliegue-en-vpsservidor-propio)
5. [Configuración de Dominio](#configuración-de-dominio)
6. [Monitoreo Post-Despliegue](#monitoreo-post-despliegue)
7. [Mantenimiento y Actualizaciones](#mantenimiento-y-actualizaciones)
8. [Solución de Problemas](#solución-de-problemas)

---

## Preparación para Despliegue

### 1. Verificación del Sistema

#### Ejecutar Pruebas Completas
```bash
# Pruebas de integración
python test_integration_complete.py

# Pruebas de backup
python test_backup_system.py

# Pruebas de rendimiento
python test_performance_monitoring.py

# Pruebas de autenticación
python test_authentication.py
```

#### Verificar Configuración
```bash
# Verificar que todos los módulos están disponibles
python verify_modules.py

# Verificar configuración de base de datos
python -c "
from app.database.connection import SessionLocal
from app.database.crud import FormularioCRUD
db = SessionLocal()
crud = FormularioCRUD(db)
stats = crud.get_estadisticas_generales()
print('✅ Database connection successful')
print(f'Total forms: {stats[\"total_formularios\"]}')
db.close()
"
```

### 2. Preparación de Archivos

#### Crear Archivo de Configuración de Producción
```bash
# .env.production
DATABASE_URL=sqlite:///./data/reportes_docentes.db
SECRET_KEY=your-super-secure-production-key-here
ADMIN_PASSWORD_HASH=$2b$12$your-production-password-hash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
ENABLE_MONITORING=true
```

#### Generar Hash de Contraseña
```python
# generate_password_hash.py
import bcrypt

password = "your-secure-admin-password"
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
print(f"Password hash: {hashed.decode('utf-8')}")
```

#### Verificar Archivos Requeridos
```bash
# Verificar que todos los archivos necesarios están presentes
ls -la requirements.txt
ls -la streamlit_config.toml
ls -la dashboard/streamlit_app.py
ls -la app/
ls -la docs/
```

### 3. Optimización para Producción

#### Limpiar Archivos de Desarrollo
```bash
# Eliminar archivos de prueba y desarrollo
rm -f test_*.py
rm -f quick_test.py
rm -f verify_modules.py
rm -rf __pycache__/
rm -rf .pytest_cache/
rm -rf *.pyc
```

#### Optimizar Base de Datos
```python
# optimize_for_production.py
from app.database.optimization import db_optimizer
from app.database.connection import SessionLocal

print("Optimizing database for production...")
db_optimizer.optimize_database()
print("✅ Database optimization completed")
```

---

## Despliegue en Streamlit Cloud

### 1. Preparación del Repositorio

#### Configurar Repositorio Git
```bash
# Asegurar que todo está en Git
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main

# Verificar que el repositorio está actualizado
git status
git log --oneline -5
```

#### Estructura Requerida
```
your-repo/
├── dashboard/
│   └── streamlit_app.py          # ← Archivo principal
├── app/                          # ← Código de la aplicación
├── requirements.txt              # ← Dependencias
├── streamlit_config.toml         # ← Configuración Streamlit
├── .streamlit/
│   └── secrets.toml              # ← Secretos (no subir a Git)
└── README.md
```

### 2. Configuración en Streamlit Cloud

#### Paso 1: Crear Aplicación
1. Ir a [share.streamlit.io](https://share.streamlit.io)
2. Conectar cuenta de GitHub
3. Seleccionar repositorio
4. Configurar:
   - **Main file path**: `dashboard/streamlit_app.py`
   - **Python version**: `3.9`

#### Paso 2: Configurar Secrets
En el panel de Streamlit Cloud, agregar secrets:

```toml
# Secrets en Streamlit Cloud
[database]
DATABASE_URL = "sqlite:///./data/reportes_docentes.db"

[auth]
SECRET_KEY = "your-production-secret-key-min-32-chars"
JWT_SECRET = "your-production-jwt-secret-min-32-chars"
ADMIN_PASSWORD_HASH = "$2b$12$your-production-password-hash"

[app]
ENVIRONMENT = "production"
DEBUG = false
LOG_LEVEL = "INFO"
APP_VERSION = "1.0.0"

[monitoring]
ENABLE_MONITORING = true
MONITORING_INTERVAL = 60
```

#### Paso 3: Configurar Variables de Entorno Adicionales
```toml
[performance]
CACHE_TTL = 300
MAX_CONCURRENT_REQUESTS = 10
REQUEST_TIMEOUT = 30

[storage]
UPLOAD_DIR = "uploads"
REPORTS_DIR = "reports"
DATA_DIR = "data"
LOGS_DIR = "logs"
```

### 3. Verificación del Despliegue

#### Verificar Funcionalidad Básica
1. **Acceso**: Verificar que la URL funciona
2. **Autenticación**: Probar login con credenciales
3. **Dashboard**: Verificar que carga correctamente
4. **Formulario Público**: Probar envío de formulario
5. **Funciones Admin**: Probar aprobación/rechazo

#### URLs del Sistema
- **Dashboard Principal**: `https://your-app-name.streamlit.app/`
- **Formulario Público**: `https://your-app-name.streamlit.app/public_form`

### 4. Configuración Post-Despliegue

#### Crear Datos Iniciales
```python
# Ejecutar en la consola de Streamlit Cloud o localmente
from app.database.connection import SessionLocal
from app.database.crud import FormularioCRUD

# Crear usuario administrador inicial si es necesario
# Verificar que la base de datos está funcionando
db = SessionLocal()
crud = FormularioCRUD(db)
stats = crud.get_estadisticas_generales()
print(f"Sistema inicializado - Total formularios: {stats['total_formularios']}")
db.close()
```

---

## Despliegue en Heroku

### 1. Preparación para Heroku

#### Crear Archivos Requeridos

**`Procfile`**
```
web: streamlit run dashboard/streamlit_app.py --server.port=$PORT --server.address=0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false
```

**`runtime.txt`**
```
python-3.9.18
```

**`app.json`** (opcional, para Heroku Button)
```json
{
  "name": "Sistema de Reportes Docentes",
  "description": "Sistema web para gestión de reportes académicos docentes",
  "repository": "https://github.com/your-username/your-repo",
  "logo": "https://your-domain.com/logo.png",
  "keywords": ["streamlit", "education", "reports", "academic"],
  "env": {
    "SECRET_KEY": {
      "description": "Secret key for application security",
      "generator": "secret"
    },
    "ADMIN_PASSWORD_HASH": {
      "description": "Hashed admin password"
    }
  },
  "formation": {
    "web": {
      "quantity": 1,
      "size": "free"
    }
  },
  "addons": [],
  "buildpacks": [
    {
      "url": "heroku/python"
    }
  ]
}
```

### 2. Configuración en Heroku

#### Crear y Configurar Aplicación
```bash
# Instalar Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login a Heroku
heroku login

# Crear aplicación
heroku create your-app-name

# Configurar variables de entorno
heroku config:set SECRET_KEY="your-production-secret-key"
heroku config:set ADMIN_PASSWORD_HASH="$2b$12$your-password-hash"
heroku config:set ENVIRONMENT="production"
heroku config:set DEBUG="false"
heroku config:set LOG_LEVEL="INFO"
heroku config:set ENABLE_MONITORING="true"

# Verificar configuración
heroku config
```

#### Configurar Base de Datos (Opcional: PostgreSQL)
```bash
# Agregar PostgreSQL addon (opcional)
heroku addons:create heroku-postgresql:hobby-dev

# Obtener URL de la base de datos
heroku config:get DATABASE_URL

# Configurar URL en variables de entorno
heroku config:set DATABASE_URL="postgresql://..."
```

### 3. Despliegue

#### Desplegar Aplicación
```bash
# Agregar remote de Heroku
heroku git:remote -a your-app-name

# Desplegar
git push heroku main

# Verificar logs
heroku logs --tail

# Abrir aplicación
heroku open
```

#### Configurar Dominio Personalizado (Opcional)
```bash
# Agregar dominio personalizado
heroku domains:add your-domain.com

# Configurar DNS
# Agregar CNAME record: your-domain.com -> your-app-name.herokuapp.com
```

### 4. Configuración de SSL
```bash
# Heroku automáticamente proporciona SSL para dominios .herokuapp.com
# Para dominios personalizados:
heroku certs:auto:enable
```

---

## Despliegue en VPS/Servidor Propio

### 1. Preparación del Servidor

#### Requisitos del Sistema
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **RAM**: Mínimo 1GB, recomendado 2GB+
- **Disco**: Mínimo 10GB disponibles
- **Python**: 3.9+
- **Acceso**: SSH con sudo

#### Instalación de Dependencias
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python y herramientas
sudo apt install -y python3.9 python3.9-venv python3-pip git nginx supervisor

# Instalar Node.js (para algunas dependencias)
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 2. Configuración de la Aplicación

#### Clonar y Configurar Repositorio
```bash
# Crear usuario para la aplicación
sudo useradd -m -s /bin/bash streamlit-app
sudo su - streamlit-app

# Clonar repositorio
git clone https://github.com/your-username/your-repo.git
cd your-repo

# Crear entorno virtual
python3.9 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

#### Configurar Variables de Entorno
```bash
# Crear archivo de configuración
cat > .env << EOF
DATABASE_URL=sqlite:///./data/reportes_docentes.db
SECRET_KEY=your-production-secret-key
ADMIN_PASSWORD_HASH=$2b$12$your-password-hash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
ENABLE_MONITORING=true
EOF

# Configurar permisos
chmod 600 .env
```

#### Inicializar Base de Datos
```bash
# Crear directorios necesarios
mkdir -p data logs reports uploads backups metrics

# Inicializar base de datos
python -c "
from app.startup import startup_application
result = startup_application()
print('✅ Application initialized:', result['status'])
"
```

### 3. Configuración de Nginx

#### Crear Configuración de Nginx
```bash
sudo tee /etc/nginx/sites-available/reportes-docentes << EOF
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 86400;
    }
}
EOF

# Habilitar sitio
sudo ln -s /etc/nginx/sites-available/reportes-docentes /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 4. Configuración de Supervisor

#### Crear Configuración de Supervisor
```bash
sudo tee /etc/supervisor/conf.d/reportes-docentes.conf << EOF
[program:reportes-docentes]
command=/home/streamlit-app/your-repo/venv/bin/streamlit run dashboard/streamlit_app.py --server.port=8501 --server.address=127.0.0.1
directory=/home/streamlit-app/your-repo
user=streamlit-app
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/reportes-docentes.log
environment=PATH="/home/streamlit-app/your-repo/venv/bin"
EOF

# Recargar configuración
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start reportes-docentes
```

### 5. Configuración de SSL con Let's Encrypt

#### Instalar Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx

# Obtener certificado SSL
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Verificar renovación automática
sudo certbot renew --dry-run
```

### 6. Configuración de Firewall

#### Configurar UFW
```bash
# Habilitar firewall
sudo ufw enable

# Permitir SSH, HTTP y HTTPS
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'

# Verificar estado
sudo ufw status
```

---

## Configuración de Dominio

### 1. Configuración DNS

#### Registros DNS Requeridos
```
# Para Streamlit Cloud
Type: CNAME
Name: your-subdomain (o @)
Value: your-app-name.streamlit.app

# Para Heroku
Type: CNAME
Name: your-subdomain (o @)
Value: your-app-name.herokuapp.com

# Para VPS
Type: A
Name: your-subdomain (o @)
Value: YOUR_SERVER_IP
```

### 2. Configuración de Subdominio

#### Ejemplo de Configuración
```
# Subdominios recomendados
admin.your-domain.com     → Dashboard administrativo
forms.your-domain.com     → Formulario público
api.your-domain.com       → API (futuro)
```

### 3. Verificación de DNS

#### Herramientas de Verificación
```bash
# Verificar propagación DNS
nslookup your-domain.com
dig your-domain.com

# Verificar SSL
openssl s_client -connect your-domain.com:443 -servername your-domain.com
```

---

## Monitoreo Post-Despliegue

### 1. Verificación Inicial

#### Checklist de Verificación
- [ ] **Acceso Web**: URL principal funciona
- [ ] **Autenticación**: Login funciona correctamente
- [ ] **Dashboard**: Todas las páginas cargan
- [ ] **Formulario Público**: Envío de formularios funciona
- [ ] **Base de Datos**: Conexión y operaciones funcionan
- [ ] **Backup**: Sistema de backup funciona
- [ ] **Monitoreo**: Métricas se recolectan correctamente
- [ ] **Logs**: Sistema de logging funciona
- [ ] **SSL**: Certificado SSL válido (si aplica)

#### Script de Verificación
```python
# verify_deployment.py
import requests
import time
from datetime import datetime

def verify_deployment(base_url):
    """Verify deployment functionality"""
    
    print(f"🚀 Verifying deployment at {base_url}")
    
    # Test 1: Basic connectivity
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print("✅ Basic connectivity: OK")
        else:
            print(f"❌ Basic connectivity: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Basic connectivity: {e}")
    
    # Test 2: Public form
    try:
        form_url = f"{base_url}/public_form"
        response = requests.get(form_url, timeout=10)
        if response.status_code == 200:
            print("✅ Public form: OK")
        else:
            print(f"❌ Public form: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Public form: {e}")
    
    # Test 3: Performance
    start_time = time.time()
    try:
        response = requests.get(base_url, timeout=10)
        response_time = (time.time() - start_time) * 1000
        if response_time < 5000:  # 5 seconds
            print(f"✅ Performance: {response_time:.0f}ms")
        else:
            print(f"⚠️ Performance: {response_time:.0f}ms (slow)")
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
    
    print("🎉 Deployment verification completed")

if __name__ == "__main__":
    # Cambiar por tu URL de producción
    verify_deployment("https://your-app-name.streamlit.app")
```

### 2. Configuración de Monitoreo Continuo

#### Monitoreo de Uptime
```python
# monitoring/uptime_monitor.py
import requests
import time
import smtplib
from email.mime.text import MimeText
from datetime import datetime

class UptimeMonitor:
    def __init__(self, url, email_config=None):
        self.url = url
        self.email_config = email_config
        self.last_status = None
    
    def check_status(self):
        """Check if site is up"""
        try:
            response = requests.get(self.url, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def send_alert(self, message):
        """Send email alert"""
        if not self.email_config:
            print(f"ALERT: {message}")
            return
        
        # Implementar envío de email
        # ...
    
    def monitor(self, interval=300):  # 5 minutes
        """Continuous monitoring"""
        while True:
            is_up = self.check_status()
            
            if is_up != self.last_status:
                if is_up:
                    self.send_alert(f"✅ Site is UP: {self.url}")
                else:
                    self.send_alert(f"❌ Site is DOWN: {self.url}")
                
                self.last_status = is_up
            
            time.sleep(interval)

# Uso
monitor = UptimeMonitor("https://your-app-name.streamlit.app")
monitor.monitor()
```

### 3. Configuración de Alertas

#### Alertas por Email
```python
# alerts/email_alerts.py
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

class EmailAlerter:
    def __init__(self, smtp_server, smtp_port, username, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
    
    def send_alert(self, to_email, subject, message):
        """Send email alert"""
        msg = MimeMultipart()
        msg['From'] = self.username
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MimeText(message, 'plain'))
        
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

# Configuración
alerter = EmailAlerter(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    username="your-email@gmail.com",
    password="your-app-password"
)

# Enviar alerta de prueba
alerter.send_alert(
    to_email="admin@your-domain.com",
    subject="Sistema de Reportes - Despliegue Completado",
    message="El sistema ha sido desplegado exitosamente y está funcionando correctamente."
)
```

---

## Mantenimiento y Actualizaciones

### 1. Procedimiento de Actualización

#### Para Streamlit Cloud
```bash
# 1. Desarrollar y probar cambios localmente
git checkout -b feature/nueva-funcionalidad
# ... hacer cambios ...
python test_integration_complete.py

# 2. Merge a main
git checkout main
git merge feature/nueva-funcionalidad

# 3. Desplegar
git push origin main
# Streamlit Cloud se actualiza automáticamente
```

#### Para Heroku
```bash
# 1. Preparar cambios
git add .
git commit -m "Update: descripción de cambios"

# 2. Desplegar
git push heroku main

# 3. Verificar
heroku logs --tail
heroku open
```

#### Para VPS
```bash
# 1. Conectar al servidor
ssh streamlit-app@your-server

# 2. Actualizar código
cd your-repo
git pull origin main

# 3. Actualizar dependencias si es necesario
source venv/bin/activate
pip install -r requirements.txt

# 4. Reiniciar aplicación
sudo supervisorctl restart reportes-docentes

# 5. Verificar
sudo supervisorctl status reportes-docentes
```

### 2. Backup Automático

#### Script de Backup Automático
```bash
#!/bin/bash
# backup_script.sh

# Configuración
APP_DIR="/home/streamlit-app/your-repo"
BACKUP_DIR="/home/streamlit-app/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Crear backup
cd $APP_DIR
source venv/bin/activate

python -c "
from app.utils.backup_manager import backup_manager
result = backup_manager.create_backup(include_data=True)
if result['success']:
    print(f'✅ Backup created: {result[\"backup_name\"]}')
else:
    print(f'❌ Backup failed: {result[\"error\"]}')
"

# Limpiar backups antiguos (mantener últimos 30)
python -c "
from app.utils.backup_manager import backup_manager
deleted = backup_manager.cleanup_old_backups(keep_count=30)
print(f'🧹 Cleaned up {deleted} old backups')
"

echo "Backup completed at $(date)"
```

#### Configurar Cron Job
```bash
# Editar crontab
crontab -e

# Agregar backup diario a las 2 AM
0 2 * * * /home/streamlit-app/backup_script.sh >> /home/streamlit-app/logs/backup.log 2>&1

# Agregar backup semanal completo los domingos a las 3 AM
0 3 * * 0 /home/streamlit-app/weekly_backup.sh >> /home/streamlit-app/logs/backup.log 2>&1
```

### 3. Monitoreo de Logs

#### Script de Monitoreo de Logs
```python
# monitoring/log_monitor.py
import re
from datetime import datetime, timedelta
from pathlib import Path

class LogMonitor:
    def __init__(self, log_file):
        self.log_file = Path(log_file)
        self.error_patterns = [
            r'ERROR',
            r'CRITICAL',
            r'Exception',
            r'Traceback',
            r'Failed'
        ]
    
    def check_recent_errors(self, hours=1):
        """Check for errors in recent logs"""
        if not self.log_file.exists():
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        errors = []
        
        with open(self.log_file, 'r') as f:
            for line in f:
                # Check if line contains timestamp
                timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                if timestamp_match:
                    try:
                        log_time = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S')
                        if log_time > cutoff_time:
                            # Check for error patterns
                            for pattern in self.error_patterns:
                                if re.search(pattern, line, re.IGNORECASE):
                                    errors.append({
                                        'timestamp': log_time,
                                        'message': line.strip()
                                    })
                                    break
                    except ValueError:
                        continue
        
        return errors
    
    def generate_report(self):
        """Generate log report"""
        errors = self.check_recent_errors(24)  # Last 24 hours
        
        if errors:
            print(f"⚠️ Found {len(errors)} errors in the last 24 hours:")
            for error in errors[-10:]:  # Show last 10
                print(f"  {error['timestamp']}: {error['message'][:100]}...")
        else:
            print("✅ No errors found in the last 24 hours")

# Uso
monitor = LogMonitor("/var/log/supervisor/reportes-docentes.log")
monitor.generate_report()
```

---

## Solución de Problemas

### 1. Problemas Comunes de Despliegue

#### Error: "Module not found"
```bash
# Verificar que requirements.txt está actualizado
pip freeze > requirements.txt

# Verificar instalación de dependencias
pip install -r requirements.txt

# Verificar versiones de Python
python --version
```

#### Error: "Database connection failed"
```bash
# Verificar permisos de archivos
ls -la data/
chmod 755 data/
chmod 644 data/reportes_docentes.db

# Verificar variables de entorno
echo $DATABASE_URL

# Probar conexión manualmente
python -c "
from app.database.connection import SessionLocal
db = SessionLocal()
print('✅ Database connection successful')
db.close()
"
```

#### Error: "Port already in use"
```bash
# Para VPS - verificar procesos en puerto 8501
sudo lsof -i :8501
sudo kill -9 PID

# Reiniciar supervisor
sudo supervisorctl restart reportes-docentes
```

### 2. Problemas de Rendimiento

#### Aplicación Lenta
```python
# Verificar métricas de rendimiento
from app.core.performance_monitor import performance_monitor

# Obtener métricas actuales
metrics = performance_monitor.get_current_metrics()
print(f"CPU: {metrics['system']['cpu_percent']}%")
print(f"Memory: {metrics['system']['memory_percent']}%")

# Verificar queries lentas
summary = performance_monitor.get_performance_summary()
print(f"Avg response time: {summary['averages']['response_time_ms']}ms")
```

#### Optimización de Base de Datos
```python
# Ejecutar optimización manual
from app.database.optimization import db_optimizer

db_optimizer.analyze_tables()
db_optimizer.vacuum_database()
db_optimizer.update_statistics()
```

### 3. Problemas de Autenticación

#### No Puedo Acceder al Sistema
```python
# Verificar hash de contraseña
import bcrypt

password = "your-password"
stored_hash = "$2b$12$your-stored-hash"

if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
    print("✅ Password is correct")
else:
    print("❌ Password is incorrect")
```

#### Resetear Contraseña de Admin
```python
# reset_admin_password.py
import bcrypt
import json

# Generar nuevo hash
new_password = "new-secure-password"
new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

print(f"New password hash: {new_hash}")
print("Update this in your environment variables or secrets")
```

### 4. Recuperación de Desastres

#### Restaurar desde Backup
```python
# disaster_recovery.py
from app.utils.backup_manager import backup_manager
from pathlib import Path

# Listar backups disponibles
backups = backup_manager.list_backups()
print("Available backups:")
for backup in backups:
    print(f"  - {backup['name']} ({backup['created']})")

# Restaurar backup más reciente
if backups:
    latest_backup = backups[0]
    print(f"Restoring from: {latest_backup['name']}")
    
    result = backup_manager.restore_backup(latest_backup['path'])
    if result['success']:
        print("✅ Backup restored successfully")
    else:
        print(f"❌ Restore failed: {result['error']}")
```

#### Verificar Integridad del Sistema
```python
# system_health_check.py
from app.core.health_check import health_checker
from app.database.connection import SessionLocal
from app.database.crud import FormularioCRUD

print("🏥 System Health Check")
print("=" * 30)

# 1. Health checker
health = health_checker.get_system_health()
print(f"Overall health: {health['status']}")

# 2. Database connectivity
try:
    db = SessionLocal()
    crud = FormularioCRUD(db)
    stats = crud.get_estadisticas_generales()
    print(f"✅ Database: {stats['total_formularios']} forms")
    db.close()
except Exception as e:
    print(f"❌ Database: {e}")

# 3. File system
import os
required_dirs = ['data', 'logs', 'reports', 'uploads', 'backups']
for dir_name in required_dirs:
    if os.path.exists(dir_name):
        print(f"✅ Directory {dir_name}: OK")
    else:
        print(f"❌ Directory {dir_name}: Missing")

print("Health check completed")
```

---

## Checklist Final de Despliegue

### Pre-Despliegue
- [ ] Todas las pruebas pasan
- [ ] Configuración de producción lista
- [ ] Variables de entorno configuradas
- [ ] Hash de contraseña generado
- [ ] Repositorio actualizado en Git

### Durante el Despliegue
- [ ] Aplicación desplegada correctamente
- [ ] Variables de entorno/secrets configurados
- [ ] Base de datos inicializada
- [ ] SSL configurado (si aplica)
- [ ] Dominio configurado (si aplica)

### Post-Despliegue
- [ ] Verificación de funcionalidad básica
- [ ] Pruebas de autenticación
- [ ] Pruebas de formulario público
- [ ] Verificación de backup
- [ ] Configuración de monitoreo
- [ ] Documentación actualizada
- [ ] Equipo notificado

### Mantenimiento Continuo
- [ ] Monitoreo de uptime configurado
- [ ] Backups automáticos programados
- [ ] Alertas configuradas
- [ ] Procedimientos de actualización documentados
- [ ] Plan de recuperación de desastres listo

---

*Guía actualizada: Octubre 2024*
*Versión del Sistema: 1.0.0*

**¡Felicitaciones! Su Sistema de Reportes Docentes está listo para producción.** 🎉