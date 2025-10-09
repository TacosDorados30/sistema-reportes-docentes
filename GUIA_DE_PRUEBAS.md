# 🧪 Guía Completa de Pruebas del Sistema

## 🚀 Cómo Iniciar el Sistema

### Opción 1 - Script Mejorado (Recomendado):
```bash
python run_system.py
```

### Opción 2 - Script Original:
```bash
python start_system.py
```

**URL del Sistema:** http://localhost:8502 (o el puerto que se muestre al iniciar)

---

## 👨‍💼 PRUEBAS COMO ADMINISTRADOR

### 🔑 **Credenciales de Administrador:**
- **Usuario:** `admin`
- **Contraseña:** `admin123`

### 📊 **1. Dashboard Principal**
**Qué probar:**
- ✅ Métricas generales (formularios totales, pendientes, aprobados, rechazados)
- ✅ Gráficos de distribución por estado
- ✅ Gráfico de actividades académicas
- ✅ Tabla de actividad reciente

**Funcionalidades esperadas:**
- Visualización de estadísticas en tiempo real
- Gráficos interactivos con Plotly
- Datos actualizados automáticamente

### 📋 **2. Revisión de Formularios**
**Navegación:** Sidebar → "Revisión de Formularios"

**Qué probar:**
- ✅ Ver lista de formularios pendientes
- ✅ Seleccionar un formulario específico
- ✅ Revisar detalles completos en pestañas:
  - Cursos y Capacitaciones
  - Publicaciones
  - Eventos Académicos
  - Diseño Curricular
  - Movilidad
  - Reconocimientos
  - Certificaciones
- ✅ **Aprobar** un formulario
- ✅ **Rechazar** un formulario (con comentario opcional)

**Funcionalidades esperadas:**
- Interfaz organizada por pestañas
- Botones de acción funcionales
- Actualización automática después de aprobar/rechazar

### 📈 **3. Métricas Detalladas**
**Navegación:** Sidebar → "Métricas Detalladas"

**Qué probar:**
- ✅ Filtros por año y trimestre
- ✅ Métricas específicas del período seleccionado
- ✅ Comparaciones con períodos anteriores
- ✅ Resumen de actividades académicas

### 🔍 **4. Análisis de Datos**
**Navegación:** Sidebar → "Análisis de Datos"

**Qué probar:**
- ✅ **Tendencias Temporales:** Gráficos de formularios por mes
- ✅ **Calidad de Datos:** Detección de duplicados y validaciones
- ✅ **Estadísticas Generales:** Distribución y patrones

### 📊 **5. Análisis Avanzado**
**Navegación:** Sidebar → "Análisis Avanzado"

**Qué probar:**
- ✅ Análisis predictivo
- ✅ Correlaciones entre variables
- ✅ Visualizaciones avanzadas
- ✅ Insights automáticos

### 📤 **6. Exportar Datos**
**Navegación:** Sidebar → "Exportar Datos"

**Qué probar:**
- ✅ Filtros de exportación (fechas, estados, tipos)
- ✅ **Exportar a Excel** (.xlsx)
- ✅ **Exportar a CSV**
- ✅ **Exportar a PDF**
- ✅ Descarga automática de archivos

### 📄 **7. Generación de Reportes**
**Navegación:** Sidebar → "Generación de Reportes"

**Qué probar:**
- ✅ Selección de tipo de reporte
- ✅ Configuración de parámetros
- ✅ **Generar reporte automático**
- ✅ **Generar reporte con NLG** (narrativa automática)
- ✅ Historial de reportes generados
- ✅ Descargar reportes anteriores

### 📝 **8. Logs de Auditoría**
**Navegación:** Sidebar → "Logs de Auditoría"

**Qué probar:**
- ✅ Ver logs de todas las actividades
- ✅ Filtros por fecha, usuario, acción
- ✅ Detalles de cada acción registrada
- ✅ Exportar logs de auditoría

### 👥 **9. Gestión de Usuarios** (Si está disponible)
**Navegación:** Sidebar → Menú de usuario → "Gestión de Usuarios"

**Qué probar:**
- ✅ Ver usuarios registrados
- ✅ Crear nuevos usuarios
- ✅ Modificar permisos
- ✅ Gestionar sesiones activas

---

## 👨‍🏫 PRUEBAS COMO DOCENTE

### 📝 **Formulario Público para Docentes**

**Acceso:** 
- Misma URL pero **SIN iniciar sesión** como administrador
- O usar una ventana de incógnito/privada

### 📋 **1. Información Personal**
**Qué probar:**
- ✅ Llenar nombre completo
- ✅ Ingresar correo institucional
- ✅ Validación de formato de email
- ✅ Campos obligatorios marcados

### 🎓 **2. Cursos y Capacitaciones**
**Qué probar:**
- ✅ Agregar múltiples cursos
- ✅ Campos: nombre del curso, fecha, horas
- ✅ Validación de fechas
- ✅ Botón "Agregar otro curso"
- ✅ Eliminar cursos agregados

### 📚 **3. Publicaciones**
**Qué probar:**
- ✅ Agregar publicaciones académicas
- ✅ Campos: autores, título, evento/revista, estatus
- ✅ Selección de estatus (Publicado, En revisión, Aceptado)
- ✅ Validación de campos requeridos

### 🎤 **4. Eventos Académicos**
**Qué probar:**
- ✅ Registrar participación en eventos
- ✅ Campos: nombre del evento, fecha, tipo de participación
- ✅ Tipos: Ponente, Asistente, Organizador, Moderador
- ✅ Validación de fechas futuras/pasadas

### 📖 **5. Diseño Curricular**
**Qué probar:**
- ✅ Agregar diseños de cursos
- ✅ Campos: nombre del curso, descripción
- ✅ Descripción opcional pero recomendada

### ✈️ **6. Experiencias de Movilidad**
**Qué probar:**
- ✅ Registrar movilidades académicas
- ✅ Campos: descripción, tipo, fecha
- ✅ Tipos: Nacional, Internacional
- ✅ Validación de descripciones

### 🏆 **7. Reconocimientos**
**Qué probar:**
- ✅ Agregar reconocimientos recibidos
- ✅ Campos: nombre, tipo, fecha
- ✅ Tipos: Académico, Profesional, Institucional
- ✅ Validación de fechas

### 📜 **8. Certificaciones**
**Qué probar:**
- ✅ Registrar certificaciones profesionales
- ✅ Campos: nombre, fecha obtención, fecha vencimiento, vigencia
- ✅ Checkbox de "vigente"
- ✅ Validación de fechas de vencimiento

### 📤 **9. Envío del Formulario**
**Qué probar:**
- ✅ Validación completa antes del envío
- ✅ Mensaje de confirmación
- ✅ Generación de ID de seguimiento
- ✅ Estado inicial "PENDIENTE"

---

## 🔄 FLUJO COMPLETO DE PRUEBA

### **Escenario 1: Docente → Administrador**
1. **Como Docente:** Llenar y enviar un formulario completo
2. **Como Administrador:** 
   - Ver el nuevo formulario en "Revisión de Formularios"
   - Revisar todos los detalles
   - Aprobar el formulario
   - Verificar que aparezca en las métricas

### **Escenario 2: Rechazo y Corrección**
1. **Como Administrador:** Rechazar un formulario con comentarios
2. **Verificar:** Que el estado cambie a "RECHAZADO"
3. **Verificar:** Que aparezca en los logs de auditoría

### **Escenario 3: Análisis y Reportes**
1. **Generar datos:** Crear varios formularios de prueba
2. **Como Administrador:**
   - Ver tendencias en "Análisis de Datos"
   - Generar reportes en diferentes formatos
   - Exportar datos filtrados
   - Revisar logs de todas las actividades

---

## 🎯 PUNTOS CLAVE A VERIFICAR

### ✅ **Funcionalidad:**
- Todos los formularios se guardan correctamente
- Las aprobaciones/rechazos funcionan
- Los filtros y búsquedas responden
- Las exportaciones se descargan

### ✅ **Interfaz:**
- Navegación intuitiva
- Mensajes de confirmación claros
- Gráficos interactivos
- Responsive design

### ✅ **Seguridad:**
- Autenticación funciona correctamente
- Sesiones se mantienen
- Logs registran todas las acciones
- Validaciones de datos funcionan

### ✅ **Rendimiento:**
- Carga rápida de páginas
- Gráficos se renderizan correctamente
- Base de datos responde eficientemente
- Exportaciones se generan sin errores

---

## 🚨 Problemas Comunes y Soluciones

### **Si el puerto está ocupado:**
```bash
# El sistema detectará automáticamente otro puerto
# Busca la URL correcta en la salida del comando
```

### **Si hay errores de importación:**
```bash
pip install -r requirements.txt
```

### **Si la base de datos tiene problemas:**
```bash
# Eliminar y recrear la base de datos
rm data/reportes_docentes.db
python run_system.py
```

### **Para ver logs detallados:**
```bash
# En otra terminal
tail -f logs/application.log
tail -f logs/audit.log
```

---

## 📞 **¿Listo para Probar?**

1. **Ejecuta:** `python run_system.py`
2. **Abre:** La URL que se muestre (ej: http://localhost:8502)
3. **Prueba primero como administrador** con admin/admin123
4. **Luego abre una ventana privada** para probar como docente
5. **Experimenta con todas las funcionalidades**

¡El sistema está completamente funcional y listo para uso en producción! 🎉