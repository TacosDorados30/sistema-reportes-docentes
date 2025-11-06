# 📧 Guía de Configuración de Email Personal

## ¿Cómo funciona?

El sistema permite que **usted envíe recordatorios desde su cuenta personal** hacia los maestros. Esto hace que los emails sean más personales y confiables.

## 🚀 Configuración Rápida

### 1. Acceder a la Configuración
1. Abra el dashboard administrativo: `http://localhost:8501?admin=true`
2. Inicie sesión con sus credenciales
3. Vaya a **"Configuración Email"** en el menú lateral

### 2. Configurar su Cuenta Personal

#### Para Gmail Personal (Recomendado):
1. **Servidor SMTP:** `smtp.gmail.com`
2. **Puerto:** `587`
3. **Su Email:** `su-email@gmail.com`
4. **Contraseña:** Use una **App Password** (más seguro)
5. **Su Nombre:** `Dra. María González` (su nombre real)

#### ¿Cómo crear App Password en Gmail?
1. Vaya a su cuenta de Google
2. **Seguridad** → **Verificación en 2 pasos** (activar si no está)
3. **App passwords** → **Generar** → Seleccionar **"Correo"**
4. Copie la contraseña de 16 caracteres
5. Use esa contraseña en el sistema (NO su contraseña normal)

#### Para Outlook Personal:
1. **Servidor SMTP:** `smtp-mail.outlook.com`
2. **Puerto:** `587`
3. **Su Email:** `su-email@outlook.com`
4. **Contraseña:** Su contraseña normal de Outlook
5. **Su Nombre:** `Dra. María González` (su nombre real)

### 3. Probar el Sistema
1. Vaya a la pestaña **"Prueba de Envío"**
2. Ingrese un email de prueba (puede ser el suyo)
3. Seleccione el tipo de mensaje
4. Haga clic en **"Enviar Prueba"**
5. Revise que llegue el email

### 4. Enviar Recordatorios Reales
1. Vaya a **"Seguimiento de Maestros"**
2. Vea la lista de maestros sin formularios
3. Seleccione el tipo de recordatorio:
   - **RECORDATORIO:** Mensaje amistoso
   - **URGENTE:** Mensaje más directo
   - **FINAL:** Último aviso
4. Envíe individual o masivamente

## ✅ Ventajas de usar su cuenta personal:

- **Más personal:** Los maestros ven su nombre real como remitente
- **Más confiable:** No parece spam o email automático
- **Pueden responder:** Los maestros pueden responderle directamente
- **Más efectivo:** Mayor tasa de apertura y respuesta

## 🔒 Seguridad:

- Sus credenciales se guardan localmente en su computadora
- Use App Passwords para Gmail (más seguro)
- El sistema no comparte su información con terceros
- Puede cambiar la configuración en cualquier momento

## 📋 Ejemplo de Email que se envía:

```
De: Dra. María González <su-email@gmail.com>
Para: maestro@universidad.edu
Asunto: Recordatorio amistoso: Informe de Actividades Académicas

Hola Juan Pérez,

Espero que te encuentres muy bien. Te escribo para recordarte de manera 
amistosa que aún no hemos recibido tu informe de actividades académicas 
del período actual.

¿Qué necesitas hacer?
1. Entra al formulario en línea: http://localhost:8501
2. Completa la información de tus actividades académicas
3. Envía el formulario para que podamos revisarlo

Si tienes alguna duda, no dudes en escribirme.

Saludos cordiales,
Dra. María González
```

## 🆘 Problemas Comunes:

### "Error de autenticación"
- Verifique que su email y contraseña sean correctos
- Para Gmail, use App Password, no su contraseña normal
- Para Outlook, verifique si tiene verificación en 2 pasos

### "No se puede conectar al servidor"
- Verifique su conexión a internet
- Confirme el servidor SMTP y puerto
- Algunos antivirus bloquean conexiones SMTP

### "Los emails no llegan"
- Revise la carpeta de spam del destinatario
- Verifique que el email del maestro sea correcto
- Algunos proveedores tienen límites de envío

## 📞 Soporte:

Si tiene problemas, puede:
1. Revisar los logs en la aplicación
2. Probar con un email de prueba primero
3. Consultar con su administrador de IT si usa email institucional

---

**¡Listo!** Ahora puede enviar recordatorios personales y efectivos a sus maestros.