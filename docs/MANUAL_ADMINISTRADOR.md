# Manual del Administrador - Sistema de Reportes Docentes

## Índice
1. [Introducción](#introducción)
2. [Acceso al Sistema](#acceso-al-sistema)
3. [Dashboard Principal](#dashboard-principal)
4. [Revisión de Formularios](#revisión-de-formularios)
5. [Análisis de Datos](#análisis-de-datos)
6. [Generación de Reportes](#generación-de-reportes)
7. [Exportación de Datos](#exportación-de-datos)
8. [Gestión de Backups](#gestión-de-backups)
9. [Monitoreo de Rendimiento](#monitoreo-de-rendimiento)
10. [Logs de Auditoría](#logs-de-auditoría)
11. [Solución de Problemas](#solución-de-problemas)

---

## Introducción

El Sistema de Reportes Docentes es una plataforma web que automatiza la recolección, validación y análisis de información académica enviada por docentes. Como administrador, usted tiene acceso completo a todas las funcionalidades del sistema.

### Características Principales
- ✅ Revisión y aprobación de formularios docentes
- 📊 Análisis automático de datos académicos
- 📄 Generación de reportes narrativos
- 📤 Exportación en múltiples formatos
- 💾 Sistema de backup y recuperación
- 📈 Monitoreo de rendimiento en tiempo real
- 🔍 Logs de auditoría completos

---

## Acceso al Sistema

### URL del Sistema
- **Dashboard Administrativo**: `https://tu-dominio.streamlit.app`
- **Formulario Público**: `https://tu-dominio.streamlit.app/public_form`

### Credenciales de Acceso
- **Usuario**: `admin`
- **Contraseña**: [Configurada en variables de entorno]

### Primer Acceso
1. Navegue a la URL del dashboard
2. Ingrese sus credenciales
3. El sistema lo redirigirá al dashboard principal
4. Cambie la contraseña por defecto en **Configuración > Cambiar Contraseña**

---

## Dashboard Principal

El dashboard principal proporciona una vista general del estado del sistema.

### Métricas Principales
- **Total Formularios**: Número total de formularios recibidos
- **Pendientes**: Formularios esperando revisión
- **Aprobados**: Formularios validados y procesados
- **Rechazados**: Formularios que no cumplieron criterios

### Visualizaciones
- **Gráfico de Pastel**: Distribución por estado de formularios
- **Gráfico de Barras**: Actividades académicas por categoría
- **Tabla de Actividad Reciente**: Últimos 10 formularios procesados

### Navegación
Use el menú lateral para acceder a las diferentes secciones:
- Dashboard Principal
- Revisión de Formularios
- Métricas Detalladas
- Análisis de Datos
- Análisis Avanzado
- Exportar Datos
- Generación de Reportes
- Logs de Auditoría
- Gestión de Backups
- Monitoreo de Rendimiento

---

## Revisión de Formularios

Esta sección permite revisar y procesar formularios enviados por docentes.

### Proceso de Revisión

#### 1. Acceder a Formularios Pendientes
- Navegue a **Revisión de Formularios**
- Verá la lista de formularios con estado "PENDIENTE"
- Seleccione un formulario de la lista desplegable

#### 2. Revisar Contenido
El sistema muestra la información organizada en pestañas:
- **Cursos**: Capacitaciones y cursos impartidos
- **Publicaciones**: Artículos, libros y publicaciones académicas
- **Eventos**: Seminarios, conferencias y eventos organizados
- **Diseño Curricular**: Cursos diseñados o actualizados
- **Movilidad**: Experiencias de intercambio académico
- **Reconocimientos**: Premios, distinciones y grados obtenidos
- **Certificaciones**: Certificaciones profesionales vigentes

#### 3. Tomar Decisión
- **✅ Aprobar**: Si la información es correcta y completa
- **❌ Rechazar**: Si hay inconsistencias o información faltante
  - Agregue un comentario explicando el motivo del rechazo

#### 4. Resultado
- Los formularios aprobados se incluyen automáticamente en análisis
- Los formularios rechazados quedan excluidos del procesamiento
- Todas las acciones quedan registradas en los logs de auditoría

### Criterios de Aprobación
- Información personal completa y válida
- Fechas coherentes y realistas
- Descripciones claras y específicas
- Datos verificables cuando sea posible

---

## Análisis de Datos

### Métricas Detalladas
Acceda a **Métricas Detalladas** para análisis específicos por período:

#### Filtros Disponibles
- **Año**: Seleccione el año académico
- **Trimestre**: Elija trimestre específico o "Todos"

#### Métricas Calculadas
- Formularios procesados por período
- Resumen de actividades académicas
- Comparación con períodos anteriores
- Destacados y tendencias

### Análisis Avanzado
La sección **Análisis Avanzado** proporciona:
- Análisis de tendencias temporales
- Detección de patrones en los datos
- Estadísticas de calidad de datos
- Identificación de duplicados

### Visualizaciones Interactivas
- Gráficos de líneas para tendencias temporales
- Gráficos de barras para comparaciones
- Mapas de calor para correlaciones
- Tablas dinámicas para exploración detallada

---

## Generación de Reportes

El sistema genera automáticamente reportes narrativos usando técnicas de procesamiento de lenguaje natural.

### Tipos de Reportes

#### 1. Reporte Trimestral
- Resumen de actividades del trimestre
- Estadísticas específicas por categoría
- Datos duros organizados en tablas
- Comparación con trimestres anteriores

#### 2. Reporte Anual Narrativo
- Texto narrativo automático
- Estadísticas destacadas
- Nombres específicos de cursos y eventos
- Análisis de tendencias anuales

### Proceso de Generación

#### 1. Configurar Reporte
- Seleccione el tipo de reporte
- Elija el período (trimestre/año)
- Configure filtros adicionales si es necesario

#### 2. Generar Contenido
- El sistema procesa automáticamente los datos aprobados
- Genera texto narrativo usando algoritmos de NLG
- Incluye gráficas y visualizaciones relevantes

#### 3. Exportar Reporte
Formatos disponibles:
- **PDF**: Documento profesional con gráficas
- **Excel**: Tablas y datos estructurados
- **PowerPoint**: Presentación con slides automáticos

### Personalización
- Agregue comentarios adicionales
- Modifique el texto generado si es necesario
- Incluya o excluya secciones específicas

---

## Exportación de Datos

### Formatos de Exportación

#### Excel (.xlsx)
- **Múltiples hojas**: Formularios, Cursos, Publicaciones, Eventos
- **Formato estructurado**: Columnas organizadas y etiquetadas
- **Filtros aplicados**: Solo datos aprobados
- **Metadatos incluidos**: Fechas de generación y configuración

#### CSV (.csv)
- **Formato universal**: Compatible con cualquier software
- **Codificación UTF-8**: Soporte completo para caracteres especiales
- **Datos consolidados**: Información resumida por formulario
- **Conteos de actividades**: Totales por categoría

### Proceso de Exportación

1. **Acceder a Exportar Datos**
2. **Configurar Filtros**:
   - Rango de fechas
   - Estado de formularios
   - Categorías específicas
3. **Seleccionar Formato**
4. **Descargar Archivo**

### Usos Recomendados
- **Excel**: Análisis detallado y reportes personalizados
- **CSV**: Integración con otros sistemas o análisis estadístico

---

## Gestión de Backups

El sistema incluye un sistema robusto de backup y recuperación.

### Crear Backup

#### 1. Acceder a Gestión de Backups
- Navegue a **Gestión de Backups**
- Pestaña **Crear Backup**

#### 2. Configurar Backup
- ✅ **Incluir exportación de datos JSON**: Recomendado para portabilidad
- El backup incluye automáticamente:
  - Base de datos completa (SQLite)
  - Configuración de la aplicación
  - Metadatos del backup

#### 3. Crear y Verificar
- Haga clic en **🗄️ Crear Backup**
- El sistema verificará automáticamente la integridad
- Recibirá confirmación con detalles del backup

### Gestionar Backups Existentes

#### Lista de Backups
- **Nombre**: Identificador único con timestamp
- **Fecha Creación**: Cuándo se creó el backup
- **Tamaño**: Espacio ocupado en MB
- **Acciones**: Ver info, verificar, descargar, eliminar

#### Acciones Disponibles
- **ℹ️ Ver Info**: Metadatos y contenido del backup
- **✅ Verificar**: Comprobar integridad del archivo
- **📥 Descargar**: Obtener copia local del backup
- **🗑️ Eliminar**: Remover backup (requiere confirmación)

### Restaurar Backup

⚠️ **ADVERTENCIA**: Restaurar reemplaza todos los datos actuales

#### Proceso de Restauración
1. **Seleccionar Backup**: Elija de la lista disponible
2. **Revisar Detalles**: Verifique fecha y contenido
3. **Confirmar Acción**: Marque la casilla de confirmación
4. **Ejecutar Restauración**: El sistema creará un backup de seguridad automáticamente

### Importar Datos

#### Desde Archivo JSON
- Suba archivos JSON exportados desde otros sistemas
- Vista previa del contenido antes de importar
- Opciones de importación:
  - **Agregar**: Mantiene datos existentes
  - **Reemplazar**: Elimina datos actuales primero

### Mantenimiento Automático
- **Limpieza Automática**: Mantiene solo los últimos N backups
- **Configuración**: Ajuste cuántos backups conservar
- **Programación**: Configure limpieza automática periódica

---

## Monitoreo de Rendimiento

El sistema incluye monitoreo en tiempo real del rendimiento.

### Dashboard de Rendimiento

#### Métricas del Sistema
- **CPU Usage**: Uso del procesador en porcentaje
- **Memoria**: Uso de RAM en porcentaje y MB
- **Disco**: Espacio utilizado en el disco
- **Conexiones**: Conexiones de red activas

#### Métricas de Rendimiento
- **Total Requests**: Número total de solicitudes procesadas
- **Error Rate**: Porcentaje de errores en las solicitudes
- **Tiempo Respuesta**: Tiempo promedio de respuesta en ms
- **Total Queries**: Consultas de base de datos ejecutadas

### Historial de Métricas

#### Períodos Disponibles
- Última hora
- Últimas 6 horas
- Últimas 12 horas
- Últimas 24 horas
- Últimos 2-3 días

#### Gráficos Históricos
- **CPU y Memoria**: Tendencias de uso de recursos
- **Tiempo de Respuesta**: Rendimiento de la aplicación
- **Base de Datos**: Rendimiento de consultas

### Alertas de Rendimiento

#### Umbrales Configurables
- **CPU**: Por defecto 80%
- **Memoria**: Por defecto 85%
- **Tiempo de Respuesta**: Por defecto 5000ms

#### Gestión de Alertas
- **Ver Alertas Recientes**: Últimas 20 alertas generadas
- **Estadísticas**: Distribución por tipo de alerta
- **Limpieza**: Eliminar alertas antiguas

### Configuración

#### Ajustar Umbrales
- Modifique los límites según sus necesidades
- Configure intervalos de monitoreo
- Active/desactive el monitoreo automático

#### Mantenimiento
- **Limpiar Métricas Antiguas**: Elimina archivos de más de 7 días
- **Reiniciar Contadores**: Resetea estadísticas acumuladas
- **Exportar Métricas**: Descarga datos de rendimiento

---

## Logs de Auditoría

El sistema mantiene un registro completo de todas las acciones administrativas.

### Tipos de Eventos Registrados
- **LOGIN/LOGOUT**: Accesos al sistema
- **FORM_APPROVAL/REJECTION**: Decisiones sobre formularios
- **DATA_EXPORT**: Exportaciones de datos
- **REPORT_GENERATION**: Generación de reportes
- **BACKUP_CREATED/RESTORED**: Operaciones de backup
- **SYSTEM_ACCESS**: Accesos a secciones del sistema

### Consultar Logs

#### Filtros Disponibles
- **Rango de Fechas**: Desde/hasta fechas específicas
- **Tipo de Acción**: Filtrar por tipo de evento
- **Usuario**: Filtrar por usuario específico
- **Severidad**: INFO, WARNING, ERROR, CRITICAL

#### Información Mostrada
- **Timestamp**: Fecha y hora exacta
- **Acción**: Tipo de evento realizado
- **Usuario**: Quién realizó la acción
- **Descripción**: Detalles de la acción
- **Detalles Técnicos**: Información adicional cuando aplique

### Resumen de Auditoría

#### Estadísticas Generales
- **Total de Logs**: Número total de eventos registrados
- **Por Acción**: Conteo por tipo de evento
- **Por Severidad**: Distribución de niveles de severidad
- **Por Usuario**: Actividad por usuario
- **Actividad Reciente**: Eventos de las últimas 24 horas

#### Exportación de Logs
- Descargue logs en formato CSV para análisis externo
- Incluya filtros aplicados en la exportación
- Útil para auditorías y reportes de cumplimiento

---

## Solución de Problemas

### Problemas Comunes

#### 1. No Puedo Acceder al Sistema
**Síntomas**: Error de autenticación o página no carga
**Soluciones**:
- Verifique la URL correcta
- Confirme credenciales de acceso
- Limpie caché del navegador
- Intente en modo incógnito

#### 2. Formularios No Aparecen
**Síntomas**: Lista de formularios pendientes vacía
**Soluciones**:
- Verifique que hay formularios enviados
- Confirme filtros aplicados
- Revise logs de auditoría para errores
- Contacte soporte técnico si persiste

#### 3. Error al Generar Reportes
**Síntomas**: Falla en generación de reportes
**Soluciones**:
- Verifique que hay datos aprobados
- Confirme rango de fechas seleccionado
- Revise logs de sistema para errores específicos
- Intente con un período más pequeño

#### 4. Backup Falla
**Síntomas**: Error al crear o restaurar backup
**Soluciones**:
- Verifique espacio disponible en disco
- Confirme permisos de escritura
- Revise logs de sistema
- Intente con backup más pequeño

#### 5. Rendimiento Lento
**Síntomas**: Sistema responde lentamente
**Soluciones**:
- Revise dashboard de rendimiento
- Verifique alertas de recursos
- Limpie datos antiguos si es necesario
- Reinicie la aplicación si es crítico

### Contacto de Soporte

#### Información a Proporcionar
Cuando contacte soporte, incluya:
- **Descripción del problema**: Qué estaba intentando hacer
- **Pasos para reproducir**: Secuencia exacta de acciones
- **Mensajes de error**: Capturas de pantalla si es posible
- **Timestamp**: Cuándo ocurrió el problema
- **Usuario afectado**: Qué cuenta experimentó el problema

#### Logs Útiles
- Logs de auditoría del período relevante
- Métricas de rendimiento si aplica
- Capturas de pantalla de errores

---

## Mejores Prácticas

### Revisión de Formularios
- ✅ Revise formularios diariamente para evitar acumulación
- ✅ Use criterios consistentes para aprobación/rechazo
- ✅ Proporcione comentarios claros en rechazos
- ✅ Documente criterios especiales para referencia futura

### Gestión de Datos
- ✅ Cree backups semanalmente como mínimo
- ✅ Verifique integridad de backups periódicamente
- ✅ Mantenga copias locales de backups críticos
- ✅ Documente procedimientos de recuperación

### Monitoreo
- ✅ Revise métricas de rendimiento regularmente
- ✅ Configure alertas apropiadas para su entorno
- ✅ Investigue alertas de rendimiento prontamente
- ✅ Mantenga histórico de métricas para análisis de tendencias

### Seguridad
- ✅ Cambie contraseñas por defecto inmediatamente
- ✅ Revise logs de auditoría regularmente
- ✅ Mantenga el sistema actualizado
- ✅ Limite acceso solo a personal autorizado

---

## Apéndices

### A. Códigos de Estado de Formularios
- **PENDIENTE**: Formulario enviado, esperando revisión
- **APROBADO**: Formulario validado e incluido en análisis
- **RECHAZADO**: Formulario rechazado, excluido de análisis

### B. Tipos de Archivos de Exportación
- **.xlsx**: Excel con múltiples hojas
- **.csv**: Valores separados por comas
- **.pdf**: Documento portable con formato
- **.pptx**: Presentación de PowerPoint

### C. Niveles de Severidad en Logs
- **INFO**: Información general de operaciones
- **WARNING**: Advertencias que requieren atención
- **ERROR**: Errores que afectan funcionalidad
- **CRITICAL**: Errores críticos que requieren acción inmediata

---

*Documento actualizado: Octubre 2024*
*Versión del Sistema: 1.0.0*