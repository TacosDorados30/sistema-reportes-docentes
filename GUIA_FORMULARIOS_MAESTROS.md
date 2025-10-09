# 👨‍🏫 Guía de Pruebas - Formularios para Maestros

## 🚀 **Cómo Acceder al Formulario de Maestros**

### **Opción 1 - Ventana de Incógnito (Recomendado):**
1. Abre una **ventana privada/incógnito** en tu navegador
2. Ve a: **http://localhost:8501**
3. Verás directamente el formulario público para docentes

### **Opción 2 - Cerrar Sesión de Admin:**
1. Si estás logueado como admin, haz clic en "🚪 Cerrar Sesión" en el sidebar
2. Refresca la página
3. Verás el formulario público

---

## 📋 **Formulario Completo para Probar**

### **📝 1. Información Personal**
```
Nombre Completo: Dr. Juan Carlos Pérez García
Correo Institucional: juan.perez@universidad.edu.mx
```

### **🎓 2. Cursos y Capacitaciones**
**Curso 1:**
- Nombre: Metodologías Activas de Aprendizaje
- Fecha: 2024-03-15
- Horas: 40

**Curso 2:**
- Nombre: Tecnologías Educativas Digitales
- Fecha: 2024-06-20
- Horas: 30

**Curso 3:**
- Nombre: Evaluación por Competencias
- Fecha: 2024-09-10
- Horas: 25

### **📚 3. Publicaciones**
**Publicación 1:**
- Autores: Juan Carlos Pérez, María González
- Título: Innovación Pedagógica en la Era Digital
- Evento/Revista: Revista de Educación Superior
- Estatus: Publicado

**Publicación 2:**
- Autores: Juan Carlos Pérez, Roberto Martínez, Ana López
- Título: Metodologías Activas en Ingeniería
- Evento/Revista: Congreso Internacional de Educación
- Estatus: En revisión

### **🎤 4. Eventos Académicos**
**Evento 1:**
- Nombre: Congreso Nacional de Innovación Educativa
- Fecha: 2024-05-15
- Tipo de Participación: Ponente

**Evento 2:**
- Nombre: Seminario de Tecnología Educativa
- Fecha: 2024-08-22
- Tipo de Participación: Moderador

**Evento 3:**
- Nombre: Workshop de Metodologías Activas
- Fecha: 2024-11-30
- Tipo de Participación: Organizador

### **📖 5. Diseño Curricular**
**Diseño 1:**
- Nombre del Curso: Programación Avanzada
- Descripción: Curso enfocado en algoritmos avanzados y estructuras de datos para estudiantes de ingeniería en sistemas

**Diseño 2:**
- Nombre del Curso: Metodología de la Investigación
- Descripción: Curso integral que abarca desde la formulación del problema hasta la presentación de resultados

### **✈️ 6. Experiencias de Movilidad**
**Movilidad 1:**
- Descripción: Estancia de investigación en Universidad Politécnica de Madrid
- Tipo: Internacional
- Fecha: 2024-07-01

**Movilidad 2:**
- Descripción: Intercambio académico con UNAM
- Tipo: Nacional
- Fecha: 2024-04-15

### **🏆 7. Reconocimientos**
**Reconocimiento 1:**
- Nombre: Premio a la Excelencia Docente
- Tipo: Institucional
- Fecha: 2024-12-01

**Reconocimiento 2:**
- Nombre: Mejor Investigador del Año
- Tipo: Académico
- Fecha: 2024-10-15

### **📜 8. Certificaciones**
**Certificación 1:**
- Nombre: Certificación en Metodologías Ágiles
- Fecha de Obtención: 2024-02-20
- Fecha de Vencimiento: 2027-02-20
- Vigente: ✅ Sí

**Certificación 2:**
- Nombre: Google for Education Certified Trainer
- Fecha de Obtención: 2024-01-10
- Fecha de Vencimiento: 2025-01-10
- Vigente: ✅ Sí

---

## ✅ **Qué Verificar Durante las Pruebas**

### **🔍 Validaciones a Probar:**

#### **Campos Obligatorios:**
- [ ] Nombre completo no puede estar vacío
- [ ] Email debe tener formato válido (@universidad.edu.mx)
- [ ] Al menos un curso debe ser agregado
- [ ] Fechas no pueden ser futuras (excepto eventos programados)

#### **Funcionalidad de Botones:**
- [ ] "➕ Agregar Curso" funciona correctamente
- [ ] "➕ Agregar Publicación" funciona correctamente
- [ ] "➕ Agregar Evento" funciona correctamente
- [ ] "🗑️ Eliminar" funciona en cada sección
- [ ] Botones de "Agregar otro..." aparecen dinámicamente

#### **Validaciones de Fechas:**
- [ ] Fechas de cursos pasados se aceptan
- [ ] Fechas de eventos futuros se aceptan
- [ ] Fechas de certificaciones válidas
- [ ] Fechas de vencimiento posteriores a obtención

#### **Selecciones Desplegables:**
- [ ] Estados de publicación (Publicado, En revisión, Aceptado)
- [ ] Tipos de participación (Ponente, Asistente, Organizador, Moderador)
- [ ] Tipos de movilidad (Nacional, Internacional)
- [ ] Tipos de reconocimiento (Académico, Profesional, Institucional)

### **📤 Envío del Formulario:**
- [ ] Validación completa antes del envío
- [ ] Mensaje de confirmación aparece
- [ ] ID de seguimiento se genera
- [ ] Estado inicial "PENDIENTE" se asigna
- [ ] Redirección o mensaje de éxito

---

## 🎯 **Escenarios de Prueba Específicos**

### **Escenario 1: Formulario Completo**
1. Llena TODOS los campos con los datos de arriba
2. Agrega múltiples entradas en cada sección
3. Verifica que todo se guarde correctamente
4. Envía el formulario

### **Escenario 2: Formulario Mínimo**
1. Solo llena información personal
2. Agrega UN curso básico
3. Intenta enviar
4. Verifica que se acepte

### **Escenario 3: Validaciones de Error**
1. Intenta enviar sin nombre
2. Usa email inválido (sin @)
3. Agrega fechas futuras en cursos pasados
4. Verifica que aparezcan mensajes de error

### **Escenario 4: Funcionalidad Dinámica**
1. Agrega 3 cursos, elimina el segundo
2. Agrega 2 publicaciones, modifica la primera
3. Verifica que los cambios se reflejen correctamente

---

## 📊 **Datos de Prueba Adicionales**

### **Para Múltiples Formularios:**

**Docente 2:**
```
Nombre: Dra. María Elena Rodríguez
Email: maria.rodriguez@universidad.edu.mx
Especialidad: Matemáticas Aplicadas
```

**Docente 3:**
```
Nombre: Ing. Carlos Alberto Mendoza
Email: carlos.mendoza@universidad.edu.mx
Especialidad: Ingeniería Industrial
```

**Docente 4:**
```
Nombre: Dra. Ana Patricia Jiménez
Email: ana.jimenez@universidad.edu.mx
Especialidad: Ciencias de la Computación
```

---

## 🔄 **Flujo de Prueba Recomendado**

### **Paso 1: Prueba Básica (5 minutos)**
1. Abre ventana incógnito → http://localhost:8501
2. Llena solo información personal + 1 curso
3. Envía el formulario
4. Verifica mensaje de confirmación

### **Paso 2: Prueba Completa (15 minutos)**
1. Nueva ventana incógnito
2. Llena formulario completo con todos los datos de arriba
3. Prueba agregar/eliminar elementos
4. Envía y verifica

### **Paso 3: Prueba de Validaciones (10 minutos)**
1. Nueva ventana incógnito
2. Intenta varios escenarios de error
3. Verifica que las validaciones funcionen
4. Corrige errores y envía exitosamente

### **Paso 4: Múltiples Formularios (10 minutos)**
1. Crea 3-4 formularios con diferentes docentes
2. Varía la cantidad de información en cada uno
3. Esto generará datos para probar el panel administrativo

---

## 🎉 **¿Listo para Probar?**

1. **Ejecuta:** `python run_system.py`
2. **Abre ventana incógnito:** http://localhost:8501
3. **Sigue los escenarios de prueba**
4. **Toma notas** de cualquier problema o sugerencia

Una vez que termines de probar los formularios de maestros, podremos pasar a probar el panel administrativo donde verás todos los formularios enviados, podrás aprobarlos/rechazarlos, y explorar todas las funcionalidades de análisis y reportes.

¡Comencemos! 🚀