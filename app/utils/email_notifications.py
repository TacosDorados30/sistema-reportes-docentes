"""
Sistema de notificaciones por email para maestros
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os
from sqlalchemy.orm import Session
from app.models.database import MaestroAutorizadoDB, NotificacionEmailDB, FormularioEnvioDB
from app.database.crud import MaestroAutorizadoCRUD
import logging

logger = logging.getLogger(__name__)

class EmailNotificationManager:
    def __init__(self, db: Session):
        self.db = db
        self.maestros_crud = MaestroAutorizadoCRUD(db)
        
        # Configuración de email usando SendGrid
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY", "")
        self.email_user = os.getenv("EMAIL_USER", "josueemmanul@gmail.com")
        self.from_email = self.email_user
        self.from_name = "Sistema de Reportes Docentes"
        
        # URL de la aplicación
        self.app_url = os.getenv("APP_URL", "http://localhost:8501")
        
        # Fallback a SMTP si no hay SendGrid (para desarrollo local)
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_password = os.getenv("EMAIL_PASSWORD", "")
    
    def get_maestros_sin_formulario(self, periodo_academico: Optional[str] = None) -> List[Dict]:
        """
        Obtiene la lista de maestros autorizados que no han enviado formulario
        en el período especificado
        """
        try:
            # Obtener todos los maestros autorizados
            maestros_autorizados = self.maestros_crud.get_all_maestros()
            
            # Obtener maestros que SÍ han enviado formularios (versiones activas)
            if periodo_academico:
                # Filtrar por período específico si se proporciona
                year, quarter = self._parse_periodo(periodo_academico)
                formularios_enviados = self.db.query(FormularioEnvioDB.correo_institucional).filter(
                    FormularioEnvioDB.es_version_activa == True,
                    FormularioEnvioDB.año_academico == year,
                    FormularioEnvioDB.trimestre == quarter
                ).distinct().all()
            else:
                # Obtener todos los formularios activos
                formularios_enviados = self.db.query(FormularioEnvioDB.correo_institucional).filter(
                    FormularioEnvioDB.es_version_activa == True
                ).distinct().all()
            
            emails_con_formulario = {f.correo_institucional for f in formularios_enviados}
            
            # Filtrar maestros sin formulario
            maestros_sin_formulario = []
            for maestro in maestros_autorizados:
                if maestro.correo_institucional not in emails_con_formulario:
                    # Obtener notificaciones filtradas por período específico
                    if periodo_academico:
                        # Filtrar notificaciones por período específico
                        ultima_notificacion = self.db.query(NotificacionEmailDB).filter(
                            NotificacionEmailDB.maestro_id == maestro.id,
                            NotificacionEmailDB.periodo_academico == periodo_academico
                        ).order_by(NotificacionEmailDB.fecha_envio.desc()).first()
                        
                        total_notificaciones = self.db.query(NotificacionEmailDB).filter(
                            NotificacionEmailDB.maestro_id == maestro.id,
                            NotificacionEmailDB.periodo_academico == periodo_academico
                        ).count()
                    else:
                        # Sin filtro de período (comportamiento original)
                        ultima_notificacion = self.db.query(NotificacionEmailDB).filter(
                            NotificacionEmailDB.maestro_id == maestro.id
                        ).order_by(NotificacionEmailDB.fecha_envio.desc()).first()
                        
                        total_notificaciones = self.db.query(NotificacionEmailDB).filter(
                            NotificacionEmailDB.maestro_id == maestro.id
                        ).count()
                    
                    maestros_sin_formulario.append({
                        'id': maestro.id,
                        'nombre_completo': maestro.nombre_completo,
                        'correo_institucional': maestro.correo_institucional,
                        'fecha_creacion': maestro.fecha_creacion,
                        'ultima_notificacion': ultima_notificacion.fecha_envio if ultima_notificacion else None,
                        'tipo_ultima_notificacion': ultima_notificacion.tipo_notificacion if ultima_notificacion else None,
                        'total_notificaciones': total_notificaciones
                    })
            
            return maestros_sin_formulario
            
        except Exception as e:
            logger.error(f"Error obteniendo maestros sin formulario: {e}")
            return []
    
    def _parse_periodo(self, periodo: str) -> tuple:
        """Parsea un período académico como '2024-Q1' a (año, trimestre)"""
        try:
            year_str, quarter_str = periodo.split('-')
            year = int(year_str)
            quarter = f"Trimestre {quarter_str[1]}"
            return year, quarter
        except:
            return datetime.now().year, "Trimestre 1"
    
    def generar_mensaje_recordatorio(self, maestro: Dict, tipo: str = "RECORDATORIO") -> Dict[str, str]:
        """Genera el contenido del mensaje según el tipo de recordatorio"""
        
        # Obtener el nombre de quien envía (configurado en FROM_NAME)
        nombre_remitente = self.from_name if self.from_name != "Sistema de Reportes Docentes" else "Coordinación Académica"
        
        templates = {
            "RECORDATORIO": {
                "asunto": "Recordatorio amistoso: Informe de Actividades Académicas",
                "mensaje": f"""Hola {maestro['nombre_completo']},

Espero que te encuentres muy bien. Te escribo para recordarte de manera amistosa que aún no hemos recibido tu informe de actividades académicas del período actual.

**¿Qué necesitas hacer?**
1. Entra al formulario en línea: {self.app_url}
2. Completa la información de tus actividades académicas
3. Envía el formulario para que podamos revisarlo

**Información importante:**
- Tu correo registrado es: {maestro['correo_institucional']}
- El formulario incluye secciones para cursos, publicaciones, eventos y otras actividades
- Una vez que lo envíes, lo revisaremos y te confirmaremos

Si tienes alguna duda o problema técnico, no dudes en escribirme o llamarme.

Saludos cordiales,
{nombre_remitente}

P.D.: Agradezco mucho tu colaboración con este proceso.
"""
            },
            "URGENTE": {
                "asunto": "Urgente: Necesitamos tu informe de actividades",
                "mensaje": f"""Estimado/a {maestro['nombre_completo']},

Te escribo con carácter urgente sobre tu informe de actividades académicas que aún está pendiente de envío.

**NECESITO QUE ACTÚES HOY:**
Por favor, completa y envía tu formulario lo antes posible entrando a:
{self.app_url}

**Tu información:**
- Nombre: {maestro['nombre_completo']}
- Email registrado: {maestro['correo_institucional']}

La fecha límite se acerca rápidamente y necesitamos completar la recopilación de información de todos los maestros.

Si necesitas ayuda técnica o tienes algún problema, contáctame inmediatamente por este mismo correo o por teléfono.

Gracias por tu pronta atención,
{nombre_remitente}
"""
            },
            "FINAL": {
                "asunto": "ÚLTIMO AVISO: Tu informe debe enviarse HOY",
                "mensaje": f"""Estimado/a {maestro['nombre_completo']},

Este es mi ÚLTIMO AVISO sobre tu informe de actividades académicas pendiente.

**ACCIÓN INMEDIATA REQUERIDA - HOY:**
Debes completar tu formulario ANTES del cierre del período.

Entra AHORA a: {self.app_url}

**Consecuencias importantes del no envío:**
- Tu información no será incluida en los reportes institucionales
- Puede afectar procesos administrativos y evaluaciones posteriores
- Tendré que reportar la falta de cumplimiento

Por favor, completa el formulario HOY mismo. Si tienes algún problema técnico, llámame inmediatamente.

Espero tu pronta respuesta,
{nombre_remitente}

NOTA: Este es el último recordatorio que enviaré.
"""
            }
        }
        
        return templates.get(tipo, templates["RECORDATORIO"])
    
    def enviar_notificacion(self, maestro: Dict, tipo: str = "RECORDATORIO", periodo_academico: Optional[str] = None) -> bool:
        """Envía una notificación por email a un maestro específico"""
        
        # Generar contenido del mensaje
        contenido = self.generar_mensaje_recordatorio(maestro, tipo)
        
        # Intentar enviar con SendGrid primero (verificar que tenga valor real)
        if self.sendgrid_api_key and len(self.sendgrid_api_key) > 10:
            return self._enviar_con_sendgrid(maestro, contenido, tipo, periodo_academico)
        # Fallback a SMTP (para desarrollo local)
        elif self.email_user and self.email_password and len(self.email_password) > 5:
            return self._enviar_con_smtp(maestro, contenido, tipo, periodo_academico)
        else:
            logger.warning("Configuración de email no disponible - simulando envío")
            return self._simular_envio(maestro, tipo, periodo_academico)
    
    def _enviar_con_sendgrid(self, maestro: Dict, contenido: Dict, tipo: str, periodo_academico: Optional[str] = None) -> bool:
        """Envía email usando SendGrid API"""
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail, TrackingSettings, ClickTracking
            
            message = Mail(
                from_email=self.from_email,
                to_emails=maestro['correo_institucional'],
                subject=contenido['asunto'],
                plain_text_content=contenido['mensaje']
            )
            
            # Desactivar click tracking para que las URLs no se modifiquen
            message.tracking_settings = TrackingSettings()
            message.tracking_settings.click_tracking = ClickTracking(enable=False, enable_text=False)
            
            sg = SendGridAPIClient(self.sendgrid_api_key)
            response = sg.send(message)
            
            # Registrar notificación en base de datos
            self._registrar_notificacion(maestro['id'], tipo, contenido['asunto'], 
                                       contenido['mensaje'], "ENVIADO", periodo_academico)
            
            logger.info(f"Email enviado exitosamente a {maestro['correo_institucional']} via SendGrid")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email personalizado a {maestro['correo_institucional']}: {e}")
            # Registrar error en base de datos
            self._registrar_notificacion(maestro['id'], tipo, contenido['asunto'], 
                                       contenido['mensaje'], "ERROR", periodo_academico)
            return False
    
    def _enviar_con_smtp(self, maestro: Dict, contenido: Dict, tipo: str, periodo_academico: Optional[str] = None) -> bool:
        """Envía email usando SMTP (fallback para desarrollo local)"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = maestro['correo_institucional']
            msg['Subject'] = contenido['asunto']
            
            # Agregar cuerpo del mensaje
            msg.attach(MIMEText(contenido['mensaje'], 'plain', 'utf-8'))
            
            # Enviar email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            # Registrar notificación en base de datos
            self._registrar_notificacion(maestro['id'], tipo, contenido['asunto'], 
                                       contenido['mensaje'], "ENVIADO", periodo_academico)
            
            logger.info(f"Email enviado exitosamente a {maestro['correo_institucional']} via SMTP")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email via SMTP a {maestro['correo_institucional']}: {e}")
            # Registrar error en base de datos
            self._registrar_notificacion(maestro['id'], tipo, contenido['asunto'], 
                                       contenido['mensaje'], "ERROR", periodo_academico)
            return False
    
    def _enviar_personalizado_con_sendgrid(self, maestro: Dict, mensaje_personalizado: str, periodo_academico: str) -> bool:
        """Envía email personalizado usando SendGrid API"""
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail, TrackingSettings, ClickTracking
            
            # Personalizar el mensaje
            mensaje_final = mensaje_personalizado.replace("{nombre}", maestro['nombre_completo']).replace("{periodo}", periodo_academico).replace("{email}", maestro['correo_institucional'])
            asunto = "Recordatorio - Formulario de Actividades Académicas"
            
            message = Mail(
                from_email=self.from_email,
                to_emails=maestro['correo_institucional'],
                subject=asunto,
                plain_text_content=mensaje_final
            )
            
            # Desactivar click tracking para que las URLs no se modifiquen
            message.tracking_settings = TrackingSettings()
            message.tracking_settings.click_tracking = ClickTracking(enable=False, enable_text=False)
            
            sg = SendGridAPIClient(self.sendgrid_api_key)
            response = sg.send(message)
            
            # Registrar notificación en base de datos
            self._registrar_notificacion(maestro['id'], "RECORDATORIO", asunto, mensaje_final, "ENVIADO", periodo_academico)
            
            logger.info(f"Email personalizado enviado exitosamente a {maestro['correo_institucional']} via SendGrid")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email personalizado via SendGrid a {maestro['correo_institucional']}: {e}")
            # Registrar error en base de datos
            mensaje_final = mensaje_personalizado.replace("{nombre}", maestro['nombre_completo']).replace("{periodo}", periodo_academico).replace("{email}", maestro['correo_institucional'])
            self._registrar_notificacion(maestro['id'], "RECORDATORIO", "Recordatorio - Formulario de Actividades Académicas", mensaje_final, "ERROR", periodo_academico)
            return False
    
    def _enviar_personalizado_con_smtp(self, maestro: Dict, mensaje_personalizado: str, periodo_academico: str) -> bool:
        """Envía email personalizado usando SMTP"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Personalizar el mensaje
            mensaje_final = mensaje_personalizado.replace("{nombre}", maestro['nombre_completo']).replace("{periodo}", periodo_academico).replace("{email}", maestro['correo_institucional'])
            asunto = "Recordatorio - Formulario de Actividades Académicas"
            
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = maestro['correo_institucional']
            msg['Subject'] = asunto
            
            # Agregar cuerpo del mensaje
            msg.attach(MIMEText(mensaje_final, 'plain', 'utf-8'))
            
            # Enviar email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            # Registrar notificación en base de datos
            self._registrar_notificacion(maestro['id'], "RECORDATORIO", asunto, mensaje_final, "ENVIADO", periodo_academico)
            
            logger.info(f"Email personalizado enviado exitosamente a {maestro['correo_institucional']} via SMTP")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email personalizado via SMTP a {maestro['correo_institucional']}: {e}")
            # Registrar error en base de datos
            mensaje_final = mensaje_personalizado.replace("{nombre}", maestro['nombre_completo']).replace("{periodo}", periodo_academico).replace("{email}", maestro['correo_institucional'])
            self._registrar_notificacion(maestro['id'], "RECORDATORIO", "Recordatorio - Formulario de Actividades Académicas", mensaje_final, "ERROR", periodo_academico)
            return False
    
    def _simular_envio(self, maestro: Dict, tipo: str, periodo_academico: Optional[str] = None) -> bool:
        """Simula el envío de email para desarrollo/testing"""
        try:
            contenido = self.generar_mensaje_recordatorio(maestro, tipo)
            
            # Registrar como enviado (simulado)
            self._registrar_notificacion(maestro['id'], tipo, contenido['asunto'], 
                                       contenido['mensaje'], "ENVIADO", periodo_academico)
            
            logger.info(f"Email SIMULADO enviado a {maestro['correo_institucional']}")
            return True
            
        except Exception as e:
            logger.error(f"Error simulando envío: {e}")
            return False
    
    def _registrar_notificacion(self, maestro_id: int, tipo: str, asunto: str, 
                              mensaje: str, estado: str, periodo_academico: Optional[str] = None):
        """Registra la notificación en la base de datos"""
        try:
            notificacion = NotificacionEmailDB(
                maestro_id=maestro_id,
                tipo_notificacion=tipo,
                asunto=asunto,
                mensaje=mensaje,
                estado=estado,
                periodo_academico=periodo_academico
            )
            
            self.db.add(notificacion)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error registrando notificación: {e}")
            self.db.rollback()
    
    def enviar_recordatorios_masivos(self, tipo: str = "RECORDATORIO", 
                                   periodo_academico: Optional[str] = None) -> Dict[str, int]:
        """Envía recordatorios a todos los maestros sin formulario"""
        
        maestros_sin_formulario = self.get_maestros_sin_formulario(periodo_academico)
        
        resultados = {
            'total_maestros': len(maestros_sin_formulario),
            'enviados_exitosos': 0,
            'errores': 0,
            'detalles': []
        }
        
        for maestro in maestros_sin_formulario:
            exito = self.enviar_notificacion(maestro, tipo, periodo_academico)
            
            if exito:
                resultados['enviados_exitosos'] += 1
                resultados['detalles'].append({
                    'maestro': maestro['nombre_completo'],
                    'email': maestro['correo_institucional'],
                    'estado': 'ENVIADO'
                })
            else:
                resultados['errores'] += 1
                resultados['detalles'].append({
                    'maestro': maestro['nombre_completo'],
                    'email': maestro['correo_institucional'],
                    'estado': 'ERROR'
                })
        
        return resultados
    
    def enviar_recordatorios_masivos_personalizado(self, periodo_academico: str, mensaje_personalizado: str) -> Dict[str, int]:
        """Envía recordatorios personalizados a todos los maestros sin formulario"""
        
        maestros_sin_formulario = self.get_maestros_sin_formulario(periodo_academico)
        
        resultados = {
            'total_maestros': len(maestros_sin_formulario),
            'enviados_exitosos': 0,
            'errores': 0,
            'detalles': []
        }
        
        for maestro in maestros_sin_formulario:
            exito = self.enviar_notificacion_personalizada(maestro, mensaje_personalizado, periodo_academico)
            
            if exito:
                resultados['enviados_exitosos'] += 1
                resultados['detalles'].append({
                    'maestro': maestro['nombre_completo'],
                    'email': maestro['correo_institucional'],
                    'estado': 'ENVIADO'
                })
            else:
                resultados['errores'] += 1
                resultados['detalles'].append({
                    'maestro': maestro['nombre_completo'],
                    'email': maestro['correo_institucional'],
                    'estado': 'ERROR'
                })
        
        return resultados
    
    def enviar_notificacion_personalizada(self, maestro: Dict, mensaje_personalizado: str, periodo_academico: str) -> bool:
        """Envía una notificación personalizada por email a un maestro específico"""
        
        # Verificar si hay SendGrid configurado
        if self.sendgrid_api_key and len(self.sendgrid_api_key) > 10:
            return self._enviar_personalizado_con_sendgrid(maestro, mensaje_personalizado, periodo_academico)
        # Fallback a SMTP
        elif self.email_user and self.email_password and len(self.email_password) > 5:
            return self._enviar_personalizado_con_smtp(maestro, mensaje_personalizado, periodo_academico)
        else:
            logger.warning("Configuración de email no disponible - simulando envío")
            return self._simular_envio_personalizado(maestro, mensaje_personalizado, periodo_academico)

    
    def _simular_envio_personalizado(self, maestro: Dict, mensaje_personalizado: str, periodo_academico: str) -> bool:
        """Simula el envío de email personalizado para desarrollo/testing"""
        try:
            mensaje_final = mensaje_personalizado.replace("{nombre}", maestro['nombre_completo']).replace("{periodo}", periodo_academico).replace("{email}", maestro['correo_institucional'])
            asunto = "Recordatorio - Formulario de Actividades Académicas"
            
            # Registrar como enviado (simulado)
            self._registrar_notificacion(maestro['id'], "RECORDATORIO", asunto, mensaje_final, "ENVIADO", periodo_academico)
            
            logger.info(f"Email personalizado SIMULADO enviado a {maestro['correo_institucional']}")
            return True
            
        except Exception as e:
            logger.error(f"Error simulando envío personalizado: {e}")
            return False
    
    def get_historial_notificaciones(self, maestro_id: Optional[int] = None) -> List[Dict]:
        """Obtiene el historial de notificaciones enviadas"""
        try:
            query = self.db.query(NotificacionEmailDB, MaestroAutorizadoDB).join(
                MaestroAutorizadoDB, NotificacionEmailDB.maestro_id == MaestroAutorizadoDB.id
            )
            
            if maestro_id:
                query = query.filter(NotificacionEmailDB.maestro_id == maestro_id)
            
            resultados = query.order_by(NotificacionEmailDB.fecha_envio.desc()).all()
            
            historial = []
            for notificacion, maestro in resultados:
                historial.append({
                    'id': notificacion.id,
                    'maestro_nombre': maestro.nombre_completo,
                    'maestro_email': maestro.correo_institucional,
                    'tipo_notificacion': notificacion.tipo_notificacion,
                    'asunto': notificacion.asunto,
                    'fecha_envio': notificacion.fecha_envio,
                    'estado': notificacion.estado,
                    'periodo_academico': notificacion.periodo_academico
                })
            
            return historial
            
        except Exception as e:
            logger.error(f"Error obteniendo historial: {e}")
            return []