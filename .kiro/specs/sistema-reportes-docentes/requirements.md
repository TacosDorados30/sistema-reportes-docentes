# Requirements Document

## Introduction

El Sistema de Reportes Docentes es una plataforma web de Data Science que automatiza la recolección, validación y análisis de información académica enviada por docentes a través de formularios públicos. El sistema permite a una administradora revisar y aprobar envíos, generar dashboards interactivos, y crear reportes automáticos trimestrales y anuales utilizando técnicas de procesamiento de lenguaje natural.

## Requirements

### Requirement 1

**User Story:** Como docente, quiero acceder a un formulario web público sin necesidad de registro, para que pueda enviar mi información académica de manera rápida y sencilla.

#### Acceptance Criteria

1. WHEN un usuario accede al enlace del formulario THEN el sistema SHALL mostrar un formulario web accesible sin autenticación
2. WHEN el formulario se carga THEN el sistema SHALL mostrar todos los campos requeridos organizados por categorías
3. WHEN el usuario completa un campo de categoría múltiple THEN el sistema SHALL proporcionar un botón "+ agregar otro" para añadir más registros
4. WHEN el usuario envía el formulario THEN el sistema SHALL validar que todos los campos obligatorios estén completos
5. WHEN la validación es exitosa THEN el sistema SHALL almacenar los datos en la base de datos con estado "pendiente de revisión"

### Requirement 2

**User Story:** Como administradora, quiero revisar y validar cada formulario enviado, para que pueda aprobar o rechazar la información antes de incluirla en los análisis.

#### Acceptance Criteria

1. WHEN accedo al panel de administración THEN el sistema SHALL mostrar una lista de todos los formularios pendientes de revisión
2. WHEN selecciono un formulario THEN el sistema SHALL mostrar una previsualización completa de todos los datos enviados
3. WHEN reviso un formulario THEN el sistema SHALL proporcionar opciones claras para "Aprobar" o "Rechazar"
4. WHEN apruebo un formulario THEN el sistema SHALL cambiar su estado a "aprobado" y incluirlo en el conjunto de datos para análisis
5. WHEN rechazo un formulario THEN el sistema SHALL cambiar su estado a "rechazado" y excluirlo de los análisis
6. WHEN proceso formularios THEN el sistema SHALL mantener un registro de auditoría de todas las decisiones tomadas

### Requirement 3

**User Story:** Como administradora, quiero que el sistema procese y analice automáticamente los datos aprobados, para que pueda obtener métricas precisas sin procesamiento manual.

#### Acceptance Criteria

1. WHEN hay datos aprobados THEN el sistema SHALL limpiar y normalizar automáticamente fechas, nombres y categorías
2. WHEN se procesan los datos THEN el sistema SHALL detectar y manejar registros duplicados
3. WHEN se calculan métricas THEN el sistema SHALL generar estadísticas por trimestre y año para cada categoría
4. WHEN se analizan cursos THEN el sistema SHALL calcular total de cursos impartidos y horas acumuladas
5. WHEN se procesan publicaciones THEN el sistema SHALL categorizar por estatus (aceptado, en revisión, publicado)
6. WHEN se evalúan eventos THEN el sistema SHALL contar eventos académicos organizados y participaciones
7. WHEN se revisan certificaciones THEN el sistema SHALL identificar certificaciones vigentes vs vencidas

### Requirement 4

**User Story:** Como administradora, quiero acceder a un dashboard interactivo con visualizaciones, para que pueda monitorear el estado del sistema y analizar tendencias de manera visual.

#### Acceptance Criteria

1. WHEN accedo al dashboard THEN el sistema SHALL mostrar métricas generales de formularios recibidos, aprobados y rechazados
2. WHEN navego por el dashboard THEN el sistema SHALL proporcionar filtros por trimestre, año y categoría
3. WHEN aplico filtros THEN el sistema SHALL actualizar todas las visualizaciones en tiempo real
4. WHEN visualizo datos THEN el sistema SHALL mostrar gráficas interactivas (barras, pastel, líneas) para cada métrica
5. WHEN necesito exportar datos THEN el sistema SHALL proporcionar opciones de exportación en Excel y CSV
6. WHEN reviso estadísticas THEN el sistema SHALL mostrar comparativas entre períodos y tendencias temporales

### Requirement 5

**User Story:** Como administradora, quiero que el sistema genere automáticamente reportes narrativos y tabulares, para que pueda obtener documentos profesionales sin redacción manual.

#### Acceptance Criteria

1. WHEN solicito un reporte anual THEN el sistema SHALL generar texto narrativo automático usando técnicas de NLG
2. WHEN se crea el reporte narrativo THEN el sistema SHALL incluir estadísticas específicas con nombres de cursos, publicaciones y eventos
3. WHEN genero un reporte trimestral THEN el sistema SHALL crear un resumen con datos duros organizados por categorías
4. WHEN se completan los reportes THEN el sistema SHALL permitir exportación en formatos PDF, Excel y PowerPoint
5. WHEN se generan reportes THEN el sistema SHALL incluir gráficas y visualizaciones relevantes automáticamente
6. WHEN creo reportes THEN el sistema SHALL mantener un historial de todos los reportes generados

### Requirement 6

**User Story:** Como administradora, quiero que el sistema funcione completamente en la nube de forma gratuita, para que pueda acceder desde cualquier lugar sin instalaciones locales.

#### Acceptance Criteria

1. WHEN despliego el sistema THEN el sistema SHALL ejecutarse en una plataforma cloud gratuita
2. WHEN el sistema está inactivo THEN la plataforma SHALL reactivarlo automáticamente cuando reciba una solicitud
3. WHEN se almacenan datos THEN el sistema SHALL mantener la persistencia de la base de datos sin pérdida de información
4. WHEN accedo al sistema THEN el sistema SHALL ser completamente funcional desde cualquier navegador web
5. WHEN múltiples usuarios acceden THEN el sistema SHALL manejar concurrencia sin degradación del rendimiento
6. WHEN se realizan actualizaciones THEN el sistema SHALL mantener disponibilidad continua del servicio

### Requirement 7

**User Story:** Como docente, quiero que el formulario capture toda mi información académica de manera estructurada, para que pueda reportar completamente mis actividades profesionales.

#### Acceptance Criteria

1. WHEN completo información personal THEN el sistema SHALL capturar nombre completo y correo institucional
2. WHEN registro capacitaciones THEN el sistema SHALL permitir múltiples entradas con nombre, fecha y horas
3. WHEN reporto publicaciones THEN el sistema SHALL capturar autor(es), título, evento/revista y estatus
4. WHEN informo eventos THEN el sistema SHALL registrar nombre del evento, fecha y tipo de participación
5. WHEN reporto diseño curricular THEN el sistema SHALL capturar nombre del curso y detalles relevantes
6. WHEN registro movilidad THEN el sistema SHALL permitir descripción de experiencias nacionales e internacionales
7. WHEN informo reconocimientos THEN el sistema SHALL capturar grados, premios y certificaciones con fechas de vigencia