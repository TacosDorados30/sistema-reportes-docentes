"""
Página de Backup y Restauración
Permite descargar y restaurar toda la información del sistema
"""

import streamlit as st
import json
import sys
import os
from datetime import datetime
from io import BytesIO

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.connection import SessionLocal
from app.models.database import (
    FormularioEnvioDB, MaestroAutorizadoDB, NotificacionEmailDB,
    CursoCapacitacionDB, PublicacionDB, EventoAcademicoDB,
    DisenoCurricularDB, ExperienciaMovilidadDB, ReconocimientoDB,
    CertificacionDB, OtraActividadAcademicaDB
)
from app.models.audit import AuditLog
from app.auth.streamlit_auth import auth


def serialize_datetime(obj):
    """Convierte objetos datetime a string para JSON"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)


def export_all_data(include_audit_logs=False):
    """Exporta toda la información de la base de datos a un diccionario"""
    db = SessionLocal()
    try:
        data = {
            "export_date": datetime.now().isoformat(),
            "version": "1.0",
            "maestros_autorizados": [],
            "formularios": [],
            "notificaciones": []
        }
        
        if include_audit_logs:
            data["audit_logs"] = []
        
        # Exportar maestros autorizados (solo activos)
        maestros = db.query(MaestroAutorizadoDB).filter(MaestroAutorizadoDB.activo == True).all()
        for maestro in maestros:
            data["maestros_autorizados"].append({
                "id": maestro.id,
                "nombre_completo": maestro.nombre_completo,
                "correo_institucional": maestro.correo_institucional,
                "activo": maestro.activo,
                "fecha_creacion": serialize_datetime(maestro.fecha_creacion),
                "fecha_actualizacion": serialize_datetime(maestro.fecha_actualizacion)
            })
        
        # Exportar formularios con todas sus actividades
        formularios = db.query(FormularioEnvioDB).all()
        for form in formularios:
            form_data = {
                "id": form.id,
                "nombre_completo": form.nombre_completo,
                "correo_institucional": form.correo_institucional,
                "año_academico": form.año_academico,
                "trimestre": form.trimestre,
                "fecha_envio": serialize_datetime(form.fecha_envio),
                "estado": form.estado.value if hasattr(form.estado, 'value') else str(form.estado),
                "fecha_revision": serialize_datetime(form.fecha_revision) if form.fecha_revision else None,
                "revisado_por": form.revisado_por,
                "es_version_activa": form.es_version_activa,
                "version": form.version,
                "token_correccion": form.token_correccion,
                "formulario_original_id": form.formulario_original_id,
                "cursos": [],
                "publicaciones": [],
                "eventos": [],
                "disenos": [],
                "movilidades": [],
                "reconocimientos": [],
                "certificaciones": [],
                "otras_actividades": []
            }
            
            # Cursos
            for curso in db.query(CursoCapacitacionDB).filter_by(formulario_id=form.id).all():
                form_data["cursos"].append({
                    "nombre_curso": curso.nombre_curso,
                    "fecha": serialize_datetime(curso.fecha),
                    "horas": curso.horas
                })
            
            # Publicaciones
            for pub in db.query(PublicacionDB).filter_by(formulario_id=form.id).all():
                form_data["publicaciones"].append({
                    "titulo": pub.titulo,
                    "tipo": pub.tipo,
                    "fecha_publicacion": serialize_datetime(pub.fecha_publicacion),
                    "editorial_revista": pub.editorial_revista
                })
            
            # Eventos
            for evento in db.query(EventoAcademicoDB).filter_by(formulario_id=form.id).all():
                form_data["eventos"].append({
                    "nombre_evento": evento.nombre_evento,
                    "tipo_participacion": evento.tipo_participacion,
                    "fecha": serialize_datetime(evento.fecha),
                    "lugar": evento.lugar
                })
            
            # Diseños curriculares
            for diseno in db.query(DisenoCurricularDB).filter_by(formulario_id=form.id).all():
                form_data["disenos"].append({
                    "nombre_producto": diseno.nombre_producto,
                    "tipo": diseno.tipo,
                    "fecha_liberacion": serialize_datetime(diseno.fecha_liberacion),
                    "descripcion": diseno.descripcion
                })
            
            # Movilidades
            for mov in db.query(ExperienciaMovilidadDB).filter_by(formulario_id=form.id).all():
                form_data["movilidades"].append({
                    "tipo": mov.tipo,
                    "institucion": mov.institucion,
                    "pais": mov.pais,
                    "fecha_inicio": serialize_datetime(mov.fecha_inicio),
                    "fecha_fin": serialize_datetime(mov.fecha_fin)
                })
            
            # Reconocimientos
            for rec in db.query(ReconocimientoDB).filter_by(formulario_id=form.id).all():
                form_data["reconocimientos"].append({
                    "nombre": rec.nombre,
                    "institucion": rec.institucion,
                    "fecha": serialize_datetime(rec.fecha),
                    "descripcion": rec.descripcion
                })
            
            # Certificaciones
            for cert in db.query(CertificacionDB).filter_by(formulario_id=form.id).all():
                form_data["certificaciones"].append({
                    "nombre": cert.nombre,
                    "institucion": cert.institucion,
                    "fecha_obtencion": serialize_datetime(cert.fecha_obtencion),
                    "vigencia": cert.vigencia
                })
            
            # Otras actividades
            for otra in db.query(OtraActividadAcademicaDB).filter_by(formulario_id=form.id).all():
                form_data["otras_actividades"].append({
                    "descripcion": otra.descripcion,
                    "fecha": serialize_datetime(otra.fecha),
                    "tipo": otra.tipo
                })
            
            data["formularios"].append(form_data)
        
        # Exportar notificaciones (solo de maestros activos)
        notificaciones = db.query(NotificacionEmailDB).join(
            MaestroAutorizadoDB, NotificacionEmailDB.maestro_id == MaestroAutorizadoDB.id
        ).filter(MaestroAutorizadoDB.activo == True).all()
        for notif in notificaciones:
            data["notificaciones"].append({
                "maestro_id": notif.maestro_id,
                "tipo_notificacion": notif.tipo_notificacion,
                "asunto": notif.asunto,
                "mensaje": notif.mensaje,
                "fecha_envio": serialize_datetime(notif.fecha_envio),
                "estado": notif.estado,
                "periodo_academico": notif.periodo_academico
            })
        
        # Exportar audit logs (opcional)
        if include_audit_logs:
            logs = db.query(AuditLog).all()
            for log in logs:
                data["audit_logs"].append({
                    "timestamp": serialize_datetime(log.timestamp),
                    "action": log.action.value if hasattr(log.action, 'value') else str(log.action),
                    "severity": log.severity.value if hasattr(log.severity, 'value') else str(log.severity),
                    "user_id": log.user_id,
                    "user_name": log.user_name,
                    "description": log.description
                })
        
        return data
        
    finally:
        db.close()


def import_all_data(data):
    """Importa toda la información desde un diccionario y reemplaza los datos existentes"""
    db = SessionLocal()
    try:
        # Borrar todos los datos existentes
        # IMPORTANTE: El orden importa por las foreign keys
        st.info("🗑️ Borrando datos existentes...")
        
        # Usar TRUNCATE CASCADE para PostgreSQL (más eficiente y maneja FKs automáticamente)
        # Para SQLite, usar DELETE normal
        from sqlalchemy import text
        
        try:
            # Intentar con TRUNCATE CASCADE (PostgreSQL)
            db.execute(text("TRUNCATE TABLE audit_log CASCADE"))
            db.execute(text("TRUNCATE TABLE otras_actividades_academicas CASCADE"))
            db.execute(text("TRUNCATE TABLE certificaciones CASCADE"))
            db.execute(text("TRUNCATE TABLE reconocimientos CASCADE"))
            db.execute(text("TRUNCATE TABLE experiencias_movilidad CASCADE"))
            db.execute(text("TRUNCATE TABLE disenos_curriculares CASCADE"))
            db.execute(text("TRUNCATE TABLE eventos_academicos CASCADE"))
            db.execute(text("TRUNCATE TABLE publicaciones CASCADE"))
            db.execute(text("TRUNCATE TABLE cursos_capacitacion CASCADE"))
            db.execute(text("TRUNCATE TABLE notificaciones_email CASCADE"))
            db.execute(text("TRUNCATE TABLE formularios_envio CASCADE"))
            db.execute(text("TRUNCATE TABLE maestros_autorizados CASCADE"))
            db.commit()
        except Exception as e:
            # Si falla TRUNCATE (SQLite), usar DELETE en orden correcto
            db.rollback()
            
            # 1. Primero borrar audit logs (tiene FK a formularios y maestros)
            db.query(AuditLog).delete(synchronize_session=False)
            db.commit()
            
            # 2. Luego borrar actividades relacionadas con formularios
            db.query(OtraActividadAcademicaDB).delete(synchronize_session=False)
            db.query(CertificacionDB).delete(synchronize_session=False)
            db.query(ReconocimientoDB).delete(synchronize_session=False)
            db.query(ExperienciaMovilidadDB).delete(synchronize_session=False)
            db.query(DisenoCurricularDB).delete(synchronize_session=False)
            db.query(EventoAcademicoDB).delete(synchronize_session=False)
            db.query(PublicacionDB).delete(synchronize_session=False)
            db.query(CursoCapacitacionDB).delete(synchronize_session=False)
            db.commit()
            
            # 3. Borrar notificaciones (tiene FK a maestros)
            db.query(NotificacionEmailDB).delete(synchronize_session=False)
            db.commit()
            
            # 4. Borrar formularios
            db.query(FormularioEnvioDB).delete(synchronize_session=False)
            db.commit()
            
            # 5. Finalmente borrar maestros
            db.query(MaestroAutorizadoDB).delete(synchronize_session=False)
            db.commit()
        
        # Importar maestros autorizados
        st.info("👥 Importando maestros autorizados...")
        for maestro_data in data.get("maestros_autorizados", []):
            maestro = MaestroAutorizadoDB(
                nombre_completo=maestro_data["nombre_completo"],
                correo_institucional=maestro_data["correo_institucional"],
                activo=maestro_data.get("activo", True)
            )
            db.add(maestro)
        
        db.commit()
        
        # Crear mapeo de IDs antiguos a nuevos
        maestros_map = {}
        for maestro_data in data.get("maestros_autorizados", []):
            maestro = db.query(MaestroAutorizadoDB).filter_by(
                correo_institucional=maestro_data["correo_institucional"]
            ).first()
            if maestro:
                maestros_map[maestro_data["id"]] = maestro.id
        
        # Importar formularios
        st.info("📝 Importando formularios...")
        formularios_map = {}
        
        for form_data in data.get("formularios", []):
            formulario = FormularioEnvioDB(
                nombre_completo=form_data["nombre_completo"],
                correo_institucional=form_data["correo_institucional"],
                año_academico=form_data["año_academico"],
                trimestre=form_data["trimestre"],
                estado=form_data.get("estado", "PENDIENTE"),
                revisado_por=form_data.get("revisado_por"),
                es_version_activa=form_data.get("es_version_activa", True),
                version=form_data.get("version", 1),
                token_correccion=form_data.get("token_correccion"),
                formulario_original_id=form_data.get("formulario_original_id")
            )
            db.add(formulario)
            db.flush()
            
            formularios_map[form_data["id"]] = formulario.id
            
            # Importar cursos
            for curso_data in form_data.get("cursos", []):
                from datetime import datetime
                fecha = datetime.fromisoformat(curso_data["fecha"]) if isinstance(curso_data["fecha"], str) else curso_data["fecha"]
                curso = CursoCapacitacionDB(
                    formulario_id=formulario.id,
                    nombre_curso=curso_data["nombre_curso"],
                    fecha=fecha,
                    horas=curso_data.get("horas")
                )
                db.add(curso)
            
            # Importar publicaciones
            for pub_data in form_data.get("publicaciones", []):
                pub = PublicacionDB(
                    formulario_id=formulario.id,
                    titulo=pub_data["titulo"],
                    tipo=pub_data.get("tipo"),
                    editorial_revista=pub_data.get("editorial_revista")
                )
                db.add(pub)
            
            # Importar eventos
            for evento_data in form_data.get("eventos", []):
                evento = EventoAcademicoDB(
                    formulario_id=formulario.id,
                    nombre_evento=evento_data["nombre_evento"],
                    tipo_participacion=evento_data.get("tipo_participacion"),
                    lugar=evento_data.get("lugar")
                )
                db.add(evento)
            
            # Importar diseños
            for diseno_data in form_data.get("disenos", []):
                diseno = DisenoCurricularDB(
                    formulario_id=formulario.id,
                    nombre_producto=diseno_data["nombre_producto"],
                    tipo=diseno_data.get("tipo"),
                    descripcion=diseno_data.get("descripcion")
                )
                db.add(diseno)
            
            # Importar movilidades
            for mov_data in form_data.get("movilidades", []):
                mov = ExperienciaMovilidadDB(
                    formulario_id=formulario.id,
                    tipo=mov_data.get("tipo"),
                    institucion=mov_data.get("institucion"),
                    pais=mov_data.get("pais")
                )
                db.add(mov)
            
            # Importar reconocimientos
            for rec_data in form_data.get("reconocimientos", []):
                rec = ReconocimientoDB(
                    formulario_id=formulario.id,
                    nombre=rec_data["nombre"],
                    institucion=rec_data.get("institucion"),
                    descripcion=rec_data.get("descripcion")
                )
                db.add(rec)
            
            # Importar certificaciones
            for cert_data in form_data.get("certificaciones", []):
                cert = CertificacionDB(
                    formulario_id=formulario.id,
                    nombre=cert_data["nombre"],
                    institucion=cert_data.get("institucion"),
                    vigencia=cert_data.get("vigencia")
                )
                db.add(cert)
            
            # Importar otras actividades
            for otra_data in form_data.get("otras_actividades", []):
                otra = OtraActividadAcademicaDB(
                    formulario_id=formulario.id,
                    descripcion=otra_data["descripcion"],
                    tipo=otra_data.get("tipo")
                )
                db.add(otra)
        
        db.commit()
        
        # Importar notificaciones
        st.info("📧 Importando notificaciones...")
        for notif_data in data.get("notificaciones", []):
            old_maestro_id = notif_data["maestro_id"]
            new_maestro_id = maestros_map.get(old_maestro_id)
            
            if new_maestro_id:
                notif = NotificacionEmailDB(
                    maestro_id=new_maestro_id,
                    tipo_notificacion=notif_data["tipo_notificacion"],
                    asunto=notif_data["asunto"],
                    mensaje=notif_data["mensaje"],
                    estado=notif_data.get("estado", "ENVIADO"),
                    periodo_academico=notif_data.get("periodo_academico")
                )
                db.add(notif)
        
        db.commit()
        
        return True
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def show_backup_restauracion_page():
    """Muestra la página de backup y restauración"""
    
    # Require authentication
    if not auth.is_authenticated():
        st.warning("⚠️ Debe iniciar sesión para acceder a esta página")
        st.stop()
    
    st.title("💾 Backup y Restauración")
    st.markdown("---")
    
    st.info("""
    **📦 Sistema de Backup Completo**
    
    Esta herramienta te permite:
    - ✅ Descargar TODA la información del sistema en un archivo JSON
    - ✅ Restaurar la información desde un archivo de backup
    - ✅ Mantener copias de seguridad independientes de la base de datos
    """)
    
    # Tabs para organizar
    tab1, tab2, tab3 = st.tabs(["📥 Descargar Backup", "📤 Restaurar Backup", "ℹ️ Información"])
    
    with tab1:
        st.subheader("📥 Descargar Backup Completo")
        
        st.write("""
        Descarga un archivo JSON con **toda** la información del sistema:
        - 👥 Maestros autorizados
        - 📝 Formularios enviados (con todas sus actividades)
        - 📧 Notificaciones enviadas
        """)
        
        include_logs = st.checkbox(
            "📊 Incluir Audit Logs (puede aumentar el tamaño del archivo)",
            value=False,
            help="Los logs de auditoría son históricos y no son necesarios para recuperar el sistema"
        )
        
        if st.button("🔽 Generar y Descargar Backup", type="primary"):
            with st.spinner("Exportando datos..."):
                try:
                    # Exportar datos
                    data = export_all_data(include_audit_logs=include_logs)
                    
                    # Convertir a JSON
                    json_str = json.dumps(data, indent=2, ensure_ascii=False)
                    json_bytes = json_str.encode('utf-8')
                    
                    # Generar nombre de archivo con fecha
                    filename = f"backup_reportes_docentes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    
                    # Mostrar estadísticas
                    st.success("✅ Backup generado exitosamente!")
                    
                    cols = st.columns(4 if include_logs else 3)
                    with cols[0]:
                        st.metric("Maestros", len(data["maestros_autorizados"]))
                    with cols[1]:
                        st.metric("Formularios", len(data["formularios"]))
                    with cols[2]:
                        st.metric("Notificaciones", len(data["notificaciones"]))
                    if include_logs:
                        with cols[3]:
                            st.metric("Audit Logs", len(data.get("audit_logs", [])))
                    
                    # Botón de descarga
                    st.download_button(
                        label="💾 Descargar Archivo JSON",
                        data=json_bytes,
                        file_name=filename,
                        mime="application/json"
                    )
                    
                    st.info(f"📁 Tamaño del archivo: {len(json_bytes) / 1024:.2f} KB")
                    
                except Exception as e:
                    st.error(f"❌ Error al generar backup: {e}")
    
    with tab2:
        st.subheader("📤 Restaurar desde Backup")
        
        st.warning("""
        ⚠️ **ADVERTENCIA:** Al restaurar un backup:
        - Se borrarán **TODOS** los datos actuales
        - Se reemplazarán con los datos del archivo
        - Esta acción **NO SE PUEDE DESHACER**
        
        Asegúrate de descargar un backup actual antes de restaurar.
        """)
        
        uploaded_file = st.file_uploader(
            "Selecciona un archivo de backup (JSON)",
            type=['json'],
            help="Sube el archivo JSON que descargaste previamente"
        )
        
        if uploaded_file is not None:
            try:
                # Leer y parsear el JSON
                json_str = uploaded_file.read().decode('utf-8')
                data = json.loads(json_str)
                
                # Mostrar información del backup
                st.success("✅ Archivo cargado correctamente")
                
                st.write("**📊 Contenido del backup:**")
                has_logs = "audit_logs" in data
                cols = st.columns(4 if has_logs else 3)
                with cols[0]:
                    st.metric("Maestros", len(data.get("maestros_autorizados", [])))
                with cols[1]:
                    st.metric("Formularios", len(data.get("formularios", [])))
                with cols[2]:
                    st.metric("Notificaciones", len(data.get("notificaciones", [])))
                if has_logs:
                    with cols[3]:
                        st.metric("Audit Logs", len(data.get("audit_logs", [])))
                
                st.info(f"📅 Fecha del backup: {data.get('export_date', 'Desconocida')}")
                
                # Confirmación
                st.markdown("---")
                confirmar = st.checkbox("⚠️ Entiendo que esto borrará todos los datos actuales")
                
                if confirmar:
                    if st.button("🔄 RESTAURAR BACKUP", type="primary"):
                        with st.spinner("Restaurando datos... Esto puede tomar unos momentos."):
                            try:
                                import_all_data(data)
                                st.success("✅ ¡Backup restaurado exitosamente!")
                                st.balloons()
                                st.info("🔄 Recarga la página para ver los cambios reflejados")
                            except Exception as e:
                                st.error(f"❌ Error al restaurar backup: {e}")
                
            except json.JSONDecodeError:
                st.error("❌ El archivo no es un JSON válido")
            except Exception as e:
                st.error(f"❌ Error al leer el archivo: {e}")
    
    with tab3:
        st.subheader("ℹ️ Información del Sistema de Backup")
        
        st.markdown("""
        ### 📖 ¿Cómo funciona?
        
        **Descargar Backup:**
        1. Click en "Generar y Descargar Backup"
        2. Se exportan todos los datos a formato JSON
        3. Descargas el archivo a tu computadora
        4. Guarda el archivo en un lugar seguro
        
        **Restaurar Backup:**
        1. Sube el archivo JSON que descargaste
        2. Verifica que sea el backup correcto
        3. Confirma que entiendes que se borrarán los datos actuales
        4. Click en "RESTAURAR BACKUP"
        5. Espera a que termine el proceso
        
        ### 💡 Recomendaciones
        
        - 📅 Descarga backups regularmente (semanal o mensual)
        - 💾 Guarda los backups en múltiples lugares (computadora, USB, nube)
        - 🏷️ Los archivos tienen fecha en el nombre para identificarlos fácilmente
        - ⚠️ Siempre descarga un backup antes de restaurar otro
        - 🔒 Los archivos JSON son legibles, no guardes información sensible
        
        ### 🔧 Formato del Archivo
        
        El archivo JSON contiene:
        - `export_date`: Fecha y hora del backup
        - `version`: Versión del formato
        - `maestros_autorizados`: Lista de maestros
        - `formularios`: Lista de formularios con todas sus actividades
        - `notificaciones`: Historial de emails enviados
        - `audit_logs`: Logs de auditoría del sistema
        
        ### ⚡ Ventajas
        
        - ✅ Independiente de la base de datos
        - ✅ Portátil (puedes mover los datos entre servidores)
        - ✅ Legible (puedes ver el contenido en cualquier editor)
        - ✅ Versionable (puedes tener múltiples copias)
        - ✅ Recuperación rápida en caso de pérdida de datos
        """)


if __name__ == "__main__":
    show_backup_restauracion_page()
