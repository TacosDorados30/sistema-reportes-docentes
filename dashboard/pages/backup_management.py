"""
Backup Management Page
Página para gestionar backups y recuperación de datos
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import json
import tempfile
import os
from pathlib import Path

# Initialize auth first
from app.auth.streamlit_auth import auth

# Try to import backup manager with error handling
try:
    from app.utils.backup_manager import backup_manager
    BACKUP_AVAILABLE = True
except Exception as e:
    BACKUP_AVAILABLE = False
    BACKUP_ERROR = str(e)

try:
    from app.core.audit_logger import audit_logger
    AUDIT_AVAILABLE = True
except Exception as e:
    AUDIT_AVAILABLE = False

def show_backup_management():
    """Show backup management interface"""
    
    # Require authentication
    if not auth.is_authenticated():
        auth.show_login_form()
        return
    
    st.title("🗄️ Gestión de Backups")
    st.markdown("Administra los backups de la base de datos y recuperación de datos")
    
    # Check if backup system is available
    if not BACKUP_AVAILABLE:
        st.error(f"❌ Sistema de backup no disponible: {BACKUP_ERROR}")
        st.info("💡 El sistema de backup requiere configuración adicional.")
        
        # Show basic backup information
        show_backup_info_only()
        return
    
    # Create tabs for different backup operations
    tab1, tab2, tab3, tab4 = st.tabs([
        "📦 Crear Backup", 
        "📋 Lista de Backups", 
        "🔄 Restaurar Backup", 
        "📊 Importar Datos"
    ])
    
    with tab1:
        show_create_backup_section()
    
    with tab2:
        show_backup_list_section()
    
    with tab3:
        show_restore_backup_section()
    
    with tab4:
        show_import_data_section()

def show_backup_info_only():
    """Show backup information when system is not available"""
    
    st.subheader("📋 Información de Backup")
    
    st.markdown("""
    ### ¿Qué son los Backups?
    
    Los backups son copias de seguridad de tu base de datos que incluyen:
    
    - **Base de datos completa**: Todos los formularios y datos
    - **Configuración**: Ajustes del sistema
    - **Exportación JSON**: Datos en formato portable
    - **Metadatos**: Información sobre el backup
    
    ### ¿Por qué son importantes?
    
    - 🛡️ **Protección de datos**: Evita pérdida de información
    - 🔄 **Recuperación**: Restaura el sistema en caso de problemas
    - 📊 **Migración**: Transfiere datos entre sistemas
    - 📈 **Historial**: Mantiene versiones anteriores
    
    ### Backup Manual
    
    Mientras el sistema automático no esté disponible, puedes hacer backup manual:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Opción 1: Exportar Datos**
        1. Ve a "Exportar Datos"
        2. Selecciona formato Excel o CSV
        3. Descarga todos los formularios
        """)
    
    with col2:
        st.markdown("""
        **Opción 2: Copia Manual**
        1. Localiza el archivo `data/sistema_reportes.db`
        2. Copia el archivo a ubicación segura
        3. Incluye fecha en el nombre del archivo
        """)
    
    # Show current database info
    st.subheader("📊 Información Actual")
    
    try:
        from app.database.connection import SessionLocal
        from app.database.crud import FormularioCRUD
        
        db = SessionLocal()
        crud = FormularioCRUD(db)
        
        # Get basic stats
        stats = crud.get_estadisticas_generales()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Formularios", stats.get("total_formularios", 0))
        
        with col2:
            st.metric("Formularios Aprobados", stats.get("formularios_aprobados", 0))
        
        with col3:
            st.metric("Formularios Pendientes", stats.get("formularios_pendientes", 0))
        
        db.close()
        
    except Exception as e:
        st.warning(f"No se pudo obtener estadísticas: {e}")
    
    # Manual backup button
    st.subheader("🔧 Acciones Disponibles")
    
    if st.button("📥 Ir a Exportar Datos"):
        st.switch_page("dashboard/pages/data_export.py")

def show_create_backup_section():
    """Show backup creation interface"""
    
    st.header("Crear Nuevo Backup")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **¿Qué incluye un backup?**
        - Base de datos completa (SQLite)
        - Configuración de la aplicación
        - Exportación de datos en formato JSON
        - Metadatos del backup (fecha, versión, etc.)
        """)
        
        include_data = st.checkbox(
            "Incluir exportación de datos JSON", 
            value=True,
            help="Incluye una exportación legible de todos los datos para portabilidad"
        )
    
    with col2:
        if st.button("🗄️ Crear Backup", type="primary", use_container_width=True):
            create_backup_action(include_data)

def create_backup_action(include_data: bool):
    """Execute backup creation"""
    
    if not BACKUP_AVAILABLE:
        st.error("Sistema de backup no disponible")
        return
    
    try:
        with st.spinner("Creando backup..."):
            result = backup_manager.create_backup(include_data=include_data)
        
        if result["success"]:
            st.success(f"✅ Backup creado exitosamente!")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Nombre del backup", result["backup_name"])
                st.metric("Tamaño", f"{result['size_mb']} MB")
            
            with col2:
                st.metric("Timestamp", result["timestamp"])
                st.metric("Ruta", result["backup_path"])
            
            # Log the action if available
            if AUDIT_AVAILABLE:
                try:
                    from app.core.audit_logger import AuditActionEnum
                    audit_logger.log_action(
                        action=AuditActionEnum.BACKUP_CREATED,
                        description=f"Backup created: {result['backup_name']}",
                        user_id=auth.get_current_user().get("username") if auth.get_current_user() else "admin",
                        user_name=auth.get_current_user().get("name") if auth.get_current_user() else "Admin",
                        metadata={
                            "backup_name": result["backup_name"],
                            "size_mb": result["size_mb"],
                            "include_data": include_data
                        }
                    )
                except Exception as e:
                    st.warning(f"No se pudo registrar en auditoría: {e}")
            
            # Auto-refresh the backup list
            st.rerun()
            
        else:
            st.error(f"❌ Error al crear backup: {result['error']}")
            
    except Exception as e:
        st.error(f"❌ Error inesperado al crear backup: {str(e)}")

def show_backup_list_section():
    """Show list of available backups"""
    
    st.header("Lista de Backups Disponibles")
    
    if not BACKUP_AVAILABLE:
        st.error("Sistema de backup no disponible")
        return
    
    try:
        # Get backup list
        backups = backup_manager.list_backups()
        
        if not backups:
            st.info("📭 No hay backups disponibles. Crea tu primer backup en la pestaña anterior.")
            return
            
    except Exception as e:
        st.error(f"Error al obtener lista de backups: {str(e)}")
        return
    
    # Show backup statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de Backups", len(backups))
    
    with col2:
        total_size = sum(backup["size_mb"] for backup in backups)
        st.metric("Tamaño Total", f"{total_size:.2f} MB")
    
    with col3:
        if backups:
            latest_backup = backups[0]["created"]
            st.metric("Último Backup", latest_backup.strftime("%d/%m/%Y %H:%M"))
    
    # Show backup table
    st.subheader("Backups Disponibles")
    
    backup_df = pd.DataFrame([
        {
            "Nombre": backup["name"],
            "Fecha Creación": backup["created"].strftime("%d/%m/%Y %H:%M:%S"),
            "Tamaño (MB)": backup["size_mb"],
            "Timestamp": backup["timestamp"]
        }
        for backup in backups
    ])
    
    # Display table
    st.dataframe(backup_df, use_container_width=True)
    
    # Selection using selectbox instead
    if len(backups) > 0:
        backup_names = [f"{backup['name']} ({backup['created'].strftime('%d/%m/%Y %H:%M')})" for backup in backups]
        selected_backup_name = st.selectbox(
            "Seleccionar backup para acciones:",
            ["Ninguno"] + backup_names,
            key="backup_selector"
        )
        
        selected_indices = None
        if selected_backup_name != "Ninguno":
            selected_idx = backup_names.index(selected_backup_name)
            selected_indices = type('obj', (object,), {
                'selection': type('obj', (object,), {'rows': [selected_idx]})()
            })()
    
    # Action buttons for selected backup
    if selected_indices and len(selected_indices.selection.rows) > 0:
        selected_idx = selected_indices.selection.rows[0]
        selected_backup = backups[selected_idx]
        
        st.subheader(f"Acciones para: {selected_backup['name']}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("ℹ️ Ver Info", key=f"info_{selected_idx}"):
                show_backup_info(selected_backup["path"])
        
        with col2:
            if st.button("✅ Verificar", key=f"verify_{selected_idx}"):
                verify_backup_integrity(selected_backup["path"])
        
        with col3:
            if st.button("📥 Descargar", key=f"download_{selected_idx}"):
                download_backup(selected_backup["path"])
        
        with col4:
            if st.button("🗑️ Eliminar", key=f"delete_{selected_idx}", type="secondary"):
                delete_backup_action(selected_backup["name"])
    
    # Cleanup section
    st.subheader("Limpieza Automática")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        keep_count = st.number_input(
            "Mantener últimos N backups",
            min_value=1,
            max_value=50,
            value=10,
            help="Los backups más antiguos serán eliminados automáticamente"
        )
    
    with col2:
        if st.button("🧹 Limpiar Backups Antiguos"):
            cleanup_old_backups(keep_count)

def show_backup_info(backup_path: str):
    """Show detailed backup information"""
    
    info = backup_manager.get_backup_info(backup_path)
    
    if info and "error" not in info:
        st.json(info)
    else:
        st.error(f"Error al obtener información: {info.get('error', 'Unknown error')}")

def verify_backup_integrity(backup_path: str):
    """Verify backup file integrity"""
    
    with st.spinner("Verificando integridad del backup..."):
        verification = backup_manager.verify_backup_integrity(backup_path)
    
    if verification["success"]:
        st.success("✅ Backup verificado correctamente")
        
        # Show verification details
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Estado de Archivos:**")
            st.write(f"- Base de datos: {'✅' if verification['has_database'] else '❌'}")
            st.write(f"- Metadatos: {'✅' if verification['has_metadata'] else '❌'}")
            st.write(f"- Exportación JSON: {'✅' if verification['has_data_export'] else '❌'}")
        
        with col2:
            st.write("**Información:**")
            st.write(f"- Tamaño: {verification['file_size'] / (1024*1024):.2f} MB")
            st.write(f"- Extraíble: {'✅' if verification['can_extract'] else '❌'}")
        
        if verification.get("errors"):
            st.warning("⚠️ Errores encontrados:")
            for error in verification["errors"]:
                st.write(f"- {error}")
    
    else:
        st.error(f"❌ Error en verificación: {verification['error']}")

def download_backup(backup_path: str):
    """Provide backup download"""
    
    try:
        with open(backup_path, "rb") as f:
            backup_data = f.read()
        
        backup_name = Path(backup_path).name
        
        st.download_button(
            label="📥 Descargar Backup",
            data=backup_data,
            file_name=backup_name,
            mime="application/zip"
        )
        
    except Exception as e:
        st.error(f"Error al preparar descarga: {str(e)}")

def delete_backup_action(backup_name: str):
    """Delete backup with confirmation"""
    
    if f"confirm_delete_{backup_name}" not in st.session_state:
        st.session_state[f"confirm_delete_{backup_name}"] = False
    
    if not st.session_state[f"confirm_delete_{backup_name}"]:
        st.warning(f"⚠️ ¿Estás seguro de eliminar el backup '{backup_name}'?")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Sí, eliminar", key=f"confirm_yes_{backup_name}"):
                st.session_state[f"confirm_delete_{backup_name}"] = True
                st.rerun()
        
        with col2:
            if st.button("❌ Cancelar", key=f"confirm_no_{backup_name}"):
                st.info("Eliminación cancelada")
    
    else:
        # Execute deletion
        if backup_manager.delete_backup(backup_name):
            st.success(f"✅ Backup '{backup_name}' eliminado correctamente")
            
            # Log the action
            audit_logger.log_action(
                action="BACKUP_DELETED",
                user_id=st.session_state.get("user_id", "admin"),
                details={"backup_name": backup_name}
            )
            
            # Reset confirmation state
            del st.session_state[f"confirm_delete_{backup_name}"]
            st.rerun()
        else:
            st.error(f"❌ Error al eliminar backup '{backup_name}'")

def cleanup_old_backups(keep_count: int):
    """Clean up old backups"""
    
    with st.spinner("Limpiando backups antiguos..."):
        deleted_count = backup_manager.cleanup_old_backups(keep_count)
    
    if deleted_count > 0:
        st.success(f"✅ Se eliminaron {deleted_count} backups antiguos")
        
        # Log the action
        audit_logger.log_action(
            action="BACKUP_CLEANUP",
            user_id=st.session_state.get("user_id", "admin"),
            details={
                "deleted_count": deleted_count,
                "keep_count": keep_count
            }
        )
        
        st.rerun()
    else:
        st.info("ℹ️ No hay backups antiguos para eliminar")

def show_restore_backup_section():
    """Show backup restoration interface"""
    
    st.header("Restaurar desde Backup")
    
    if not BACKUP_AVAILABLE:
        st.error("Sistema de backup no disponible")
        return
    
    st.warning("""
    ⚠️ **ADVERTENCIA**: Restaurar un backup reemplazará completamente la base de datos actual.
    
    **Antes de continuar:**
    1. Se creará automáticamente un backup de la base de datos actual
    2. Todos los datos actuales serán reemplazados
    3. Esta acción no se puede deshacer fácilmente
    """)
    
    try:
        # Get available backups
        backups = backup_manager.list_backups()
        
        if not backups:
            st.info("📭 No hay backups disponibles para restaurar.")
            return
            
    except Exception as e:
        st.error(f"Error al obtener backups: {str(e)}")
        return
    
    # Select backup to restore
    backup_options = [f"{backup['name']} ({backup['created'].strftime('%d/%m/%Y %H:%M')})" for backup in backups]
    
    selected_backup_idx = st.selectbox(
        "Seleccionar backup para restaurar:",
        range(len(backup_options)),
        format_func=lambda x: backup_options[x]
    )
    
    if selected_backup_idx is not None:
        selected_backup = backups[selected_backup_idx]
        
        # Show backup details
        st.subheader("Detalles del Backup Seleccionado")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Nombre:** {selected_backup['name']}")
            st.write(f"**Fecha:** {selected_backup['created'].strftime('%d/%m/%Y %H:%M:%S')}")
        
        with col2:
            st.write(f"**Tamaño:** {selected_backup['size_mb']} MB")
            st.write(f"**Timestamp:** {selected_backup['timestamp']}")
        
        # Confirmation checkbox
        confirm_restore = st.checkbox(
            "Confirmo que entiendo que esta acción reemplazará todos los datos actuales",
            key="confirm_restore"
        )
        
        if confirm_restore:
            if st.button("🔄 Restaurar Backup", type="primary"):
                restore_backup_action(selected_backup["path"])

def restore_backup_action(backup_path: str):
    """Execute backup restoration"""
    
    with st.spinner("Restaurando backup... Esto puede tomar unos minutos."):
        result = backup_manager.restore_backup(backup_path)
    
    if result["success"]:
        st.success("✅ Backup restaurado exitosamente!")
        
        if result.get("current_backup"):
            st.info(f"💾 Se creó un backup de seguridad: {result['current_backup']}")
        
        if result.get("metadata"):
            st.subheader("Información del Backup Restaurado")
            st.json(result["metadata"])
        
        # Log the action
        audit_logger.log_action(
            action="BACKUP_RESTORED",
            user_id=st.session_state.get("user_id", "admin"),
            details={
                "backup_path": backup_path,
                "safety_backup": result.get("current_backup")
            }
        )
        
        st.warning("🔄 Reinicia la aplicación para ver los cambios completamente aplicados.")
        
    else:
        st.error(f"❌ Error al restaurar backup: {result['error']}")

def show_import_data_section():
    """Show data import interface"""
    
    st.header("Importar Datos desde JSON")
    
    if not BACKUP_AVAILABLE:
        st.error("Sistema de backup no disponible")
        st.info("💡 Usa la función 'Exportar Datos' para crear archivos de respaldo manuales.")
        return
    
    st.info("""
    📋 **Importación de Datos**
    
    Puedes importar datos desde:
    - Archivos JSON exportados desde backups
    - Datos exportados desde otras instancias del sistema
    - Archivos de migración de datos
    """)
    
    # File upload
    uploaded_file = st.file_uploader(
        "Seleccionar archivo JSON para importar:",
        type=["json"],
        help="Archivo JSON con formato de exportación del sistema"
    )
    
    if uploaded_file is not None:
        # Preview file content
        try:
            file_content = uploaded_file.read()
            data = json.loads(file_content)
            
            st.subheader("Vista Previa del Archivo")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total de Formularios", data.get("total_forms", 0))
            
            with col2:
                export_date = data.get("export_date", "No disponible")
                if export_date != "No disponible":
                    try:
                        export_dt = datetime.fromisoformat(export_date.replace('Z', '+00:00'))
                        export_date = export_dt.strftime("%d/%m/%Y %H:%M")
                    except:
                        pass
                st.metric("Fecha de Exportación", export_date)
            
            with col3:
                forms_count = len(data.get("forms", []))
                st.metric("Formularios en Archivo", forms_count)
            
            # Show sample data
            if data.get("forms"):
                st.subheader("Muestra de Datos")
                sample_form = data["forms"][0]
                st.json({k: v for k, v in sample_form.items() if k not in ["cursos_capacitacion", "publicaciones", "eventos_academicos", "diseno_curricular", "movilidad", "reconocimientos", "certificaciones"]})
            
            # Import confirmation
            if forms_count > 0:
                st.subheader("Confirmar Importación")
                
                import_mode = st.radio(
                    "Modo de importación:",
                    ["Agregar a datos existentes", "Reemplazar datos existentes"],
                    help="Agregar: mantiene datos actuales y agrega nuevos. Reemplazar: elimina datos actuales primero."
                )
                
                if st.button("📥 Importar Datos", type="primary"):
                    import_data_action(file_content, import_mode == "Reemplazar datos existentes")
            
        except json.JSONDecodeError as e:
            st.error(f"❌ Error al leer archivo JSON: {str(e)}")
        except Exception as e:
            st.error(f"❌ Error al procesar archivo: {str(e)}")

def import_data_action(file_content: bytes, replace_existing: bool):
    """Execute data import"""
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.json', delete=False) as tmp_file:
        tmp_file.write(file_content)
        tmp_file_path = tmp_file.name
    
    try:
        with st.spinner("Importando datos..."):
            # Create backup before import if replacing
            if replace_existing:
                st.info("Creando backup de seguridad antes de reemplazar datos...")
                backup_result = backup_manager.create_backup(include_data=True)
                if not backup_result["success"]:
                    st.error(f"Error al crear backup de seguridad: {backup_result['error']}")
                    return
            
            # Import data
            result = backup_manager.import_data_from_json(tmp_file_path)
        
        if result["success"]:
            st.success(f"✅ Datos importados exitosamente!")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Formularios Importados", result["imported_count"])
            
            with col2:
                st.metric("Total en Archivo", result["total_forms"])
            
            if result.get("errors"):
                st.warning("⚠️ Algunos registros tuvieron errores:")
                for error in result["errors"][:5]:  # Show first 5 errors
                    st.write(f"- {error}")
                
                if len(result["errors"]) > 5:
                    st.write(f"... y {len(result['errors']) - 5} errores más")
            
            # Log the action
            audit_logger.log_action(
                action="DATA_IMPORTED",
                user_id=st.session_state.get("user_id", "admin"),
                details={
                    "imported_count": result["imported_count"],
                    "total_forms": result["total_forms"],
                    "replace_existing": replace_existing,
                    "error_count": len(result.get("errors", []))
                }
            )
            
        else:
            st.error(f"❌ Error al importar datos: {result['error']}")
    
    finally:
        # Clean up temporary file
        try:
            os.unlink(tmp_file_path)
        except:
            pass

if __name__ == "__main__":
    show_backup_management()