# Requirements Document

## Introduction

El Sistema de Reportes Docentes es una plataforma web completa construida con Streamlit que automatiza la recolección, validación y análisis de información académica enviada por docentes. El sistema incluye un formulario público integrado, un dashboard administrativo con múltiples páginas especializadas, generación automática de reportes en múltiples formatos (PDF, Excel, PowerPoint), y un sistema completo de gestión de maestros autorizados con notificaciones por email.

## Requirements

### Requirement 1

**User Story:** Como docente autorizado, quiero acceder a un formulario integrado en Streamlit sin necesidad de registro adicional, para que pueda enviar mi información académica de manera rápida y organizada.

#### Acceptance Criteria

1. WHEN un docente accede al formulario público THEN el sistema SHALL mostrar un formulario Streamlit con validación en tiempo real
2. WHEN el formulario se carga THEN el sistema SHALL mostrar pestañas organizadas por categorías (Cursos, Publicaciones, Eventos, etc.)
3. WHEN el usuario completa campos múltiples THEN el sistema SHALL permitir agregar múltiples entradas dinámicamente
4. WHEN el usuario envía el formulario THEN el sistema SHALL validar completitud y formato de datos
5. WHEN la validación es exitosa THEN el sistema SHALL almacenar los datos con versionado automático y estado "pendiente"

### Requirement 2

**User Story:** Como administradora, quiero acceder a una página especializada de revisión de formularios, para que pueda aprobar o rechazar información de manera eficiente con vista detallada.

#### Acceptance Criteria

1. WHEN accedo a "Revision Formularios" THEN el sistema SHALL mostrar formularios pendientes con filtros avanzados
2. WHEN selecciono un formulario THEN el sistema SHALL mostrar vista detallada con pestañas por categoría de actividad
3. WHEN reviso un formulario THEN el sistema SHALL proporcionar botones de "Aprobar" y "Rechazar" con confirmación
4. WHEN apruebo un formulario THEN el sistema SHALL actualizar estado y registrar auditoría con timestamp
5. WHEN rechazo un formulario THEN el sistema SHALL excluir de análisis y mantener historial de versiones
6. WHEN proceso formularios THEN el sistema SHALL mostrar estadísticas de revisión y progreso

### Requirement 3

**User Story:** Como administradora, quiero un dashboard principal con visualizaciones interactivas y métricas en tiempo real, para que pueda monitorear el estado del sistema de manera visual.

#### Acceptance Criteria

1. WHEN accedo al dashboard principal THEN el sistema SHALL mostrar métricas generales con tarjetas de resumen
2. WHEN visualizo datos THEN el sistema SHALL mostrar gráficos de pastel para distribución de estados
3. WHEN analizo actividades THEN el sistema SHALL mostrar gráfico de barras con todas las categorías incluyendo certificaciones
4. WHEN reviso métricas THEN el sistema SHALL calcular automáticamente totales por formularios aprobados
5. WHEN filtro datos THEN el sistema SHALL actualizar visualizaciones en tiempo real
6. WHEN necesito detalles THEN el sistema SHALL proporcionar información contextual en tooltips
7. WHEN monitoreo progreso THEN el sistema SHALL mostrar estadísticas de formularios pendientes vs procesados

### Requirement 4

**User Story:** Como administradora, quiero una página especializada de generación de reportes con múltiples formatos, para que pueda crear documentos profesionales automáticamente.

#### Acceptance Criteria

1. WHEN accedo a "Generacion Reportes" THEN el sistema SHALL mostrar opciones de tipo de reporte (Anual/Trimestral)
2. WHEN selecciono parámetros THEN el sistema SHALL permitir filtrar por año y trimestre específico
3. WHEN genero reportes THEN el sistema SHALL ofrecer formatos PDF, Excel, PowerPoint y Markdown
4. WHEN creo reportes trimestrales THEN el sistema SHALL mostrar todas las actividades sin palabra "ejemplo"
5. WHEN genero PowerPoint THEN el sistema SHALL crear títulos dinámicos según tipo de reporte seleccionado
6. WHEN exporto datos THEN el sistema SHALL incluir visualizaciones y datos limpios sin asteriscos
7. WHEN reviso historial THEN el sistema SHALL mantener registro de reportes generados con metadatos

### Requirement 5

**User Story:** Como administradora, quiero gestionar maestros autorizados con notificaciones automáticas, para que pueda controlar acceso y hacer seguimiento de envíos pendientes.

#### Acceptance Criteria

1. WHEN accedo a "Maestros Autorizados" THEN el sistema SHALL mostrar lista completa con opciones de gestión
2. WHEN agrego maestros THEN el sistema SHALL validar emails únicos y almacenar información completa
3. WHEN reviso maestros THEN el sistema SHALL mostrar estado de formularios enviados por cada docente
4. WHEN accedo a "Seguimiento Maestros" THEN el sistema SHALL identificar maestros sin formularios enviados
5. WHEN envío recordatorios THEN el sistema SHALL usar configuración SMTP para notificaciones por email
6. WHEN gestiono notificaciones THEN el sistema SHALL rastrear última fecha de recordatorio enviado
7. WHEN filtro maestros THEN el sistema SHALL permitir búsqueda por nombre, email y estado de envío

### Requirement 6

**User Story:** Como administradora, quiero un sistema unificado con navegación por páginas y autenticación integrada, para que pueda acceder a todas las funcionalidades desde una interfaz cohesiva.

#### Acceptance Criteria

1. WHEN accedo al sistema THEN el sistema SHALL mostrar formulario público y dashboard admin según parámetros URL
2. WHEN me autentico THEN el sistema SHALL mostrar navegación automática entre páginas especializadas
3. WHEN navego entre páginas THEN el sistema SHALL mantener estado de sesión y contexto de usuario
4. WHEN uso la aplicación THEN el sistema SHALL ejecutarse con comando unificado "python run_unified.py"
5. WHEN accedo a funciones admin THEN el sistema SHALL requerir autenticación con gestión de sesiones
6. WHEN cambio configuraciones THEN el sistema SHALL persistir preferencias y configuraciones de usuario
7. WHEN el sistema se despliega THEN el sistema SHALL funcionar en GitHub con respaldo automático

### Requirement 7

**User Story:** Como docente, quiero un formulario completo con todas las categorías académicas y versionado automático, para que pueda reportar mis actividades con historial de cambios.

#### Acceptance Criteria

1. WHEN completo información personal THEN el sistema SHALL capturar datos básicos con validación de email institucional
2. WHEN registro cursos THEN el sistema SHALL permitir múltiples entradas con nombre, fecha, horas y detalles
3. WHEN reporto publicaciones THEN el sistema SHALL capturar autores, título, evento/revista y estatus de publicación
4. WHEN informo eventos THEN el sistema SHALL registrar eventos académicos con fecha y tipo de participación
5. WHEN reporto diseño curricular THEN el sistema SHALL capturar cursos diseñados con descripciones detalladas
6. WHEN registro movilidad THEN el sistema SHALL permitir experiencias nacionales e internacionales con fechas
7. WHEN informo reconocimientos THEN el sistema SHALL capturar premios, distinciones y certificaciones
8. WHEN agrego certificaciones THEN el sistema SHALL registrar certificaciones profesionales con fechas de vigencia
9. WHEN reporto otras actividades THEN el sistema SHALL capturar actividades académicas adicionales por categoría
10. WHEN envío formularios THEN el sistema SHALL crear versiones automáticas manteniendo historial completo