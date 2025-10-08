import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.audit_logger import AuditLogger, AuditActionEnum, AuditSeverityEnum
from app.auth.streamlit_auth import auth

def show_audit_logs_page():
    """Show audit logs page with filtering and analysis"""
    
    # Require authentication
    if not auth.require_authentication():
        return
    
    st.title("📋 Logs de Auditoría")
    st.markdown("Visualice y analice todas las acciones administrativas del sistema.")
    
    # Initialize audit logger
    audit_logger = AuditLogger()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filtros")
    
    # Date range filter
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input(
            "Fecha inicio:",
            value=date.today() - timedelta(days=30),
            max_value=date.today()
        )
    
    with col2:
        end_date = st.date_input(
            "Fecha fin:",
            value=date.today(),
            max_value=date.today()
        )
    
    # Action filter
    action_options = ["Todas"] + [action.value for action in AuditActionEnum]
    selected_action = st.sidebar.selectbox("Acción:", action_options)
    
    # Severity filter
    severity_options = ["Todas"] + [severity.value for severity in AuditSeverityEnum]
    selected_severity = st.sidebar.selectbox("Severidad:", severity_options)
    
    # User filter
    user_filter = st.sidebar.text_input("Usuario (opcional):", placeholder="Filtrar por usuario")
    
    # Resource type filter
    resource_filter = st.sidebar.text_input("Tipo de recurso (opcional):", placeholder="formulario, user, report")
    
    # Advanced options
    with st.sidebar.expander("⚙️ Opciones Avanzadas"):
        limit = st.number_input("Límite de registros:", min_value=10, max_value=1000, value=100)
        show_metadata = st.checkbox("Mostrar metadatos", value=False)
        auto_refresh = st.checkbox("Auto-actualizar (30s)", value=False)
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Resumen", "📋 Logs Detallados", "📈 Análisis", "🧹 Mantenimiento"])
    
    with tab1:
        show_audit_summary(audit_logger, start_date, end_date)
    
    with tab2:
        show_detailed_logs(
            audit_logger, start_date, end_date, selected_action, 
            selected_severity, user_filter, resource_filter, limit, show_metadata
        )
    
    with tab3:
        show_audit_analysis(audit_logger, start_date, end_date)
    
    with tab4:
        show_maintenance_options(audit_logger)
    
    # Auto-refresh functionality
    if auto_refresh:
        st.rerun()

def show_audit_summary(audit_logger: AuditLogger, start_date: date, end_date: date):
    """Show audit summary dashboard"""
    
    st.subheader("📊 Resumen de Auditoría")
    
    try:
        # Convert dates to datetime
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        # Get summary data
        summary = audit_logger.get_audit_summary(start_datetime, end_datetime)
        
        if "error" in summary:
            st.error(f"Error al obtener resumen: {summary['error']}")
            return
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Logs", summary.get("total_logs", 0))
        
        with col2:
            action_counts = summary.get("action_counts", {})
            login_count = action_counts.get("LOGIN", 0)
            st.metric("Inicios de Sesión", login_count)
        
        with col3:
            form_approvals = action_counts.get("FORM_APPROVAL", 0)
            form_rejections = action_counts.get("FORM_REJECTION", 0)
            st.metric("Acciones de Formularios", form_approvals + form_rejections)
        
        with col4:
            severity_counts = summary.get("severity_counts", {})
            error_count = severity_counts.get("ERROR", 0) + severity_counts.get("CRITICAL", 0)
            st.metric("Errores/Críticos", error_count)
        
        # Charts section
        col1, col2 = st.columns(2)
        
        with col1:
            # Action distribution
            if action_counts:
                fig_actions = px.pie(
                    values=list(action_counts.values()),
                    names=list(action_counts.keys()),
                    title="Distribución de Acciones"
                )
                st.plotly_chart(fig_actions, use_container_width=True)
        
        with col2:
            # Severity distribution
            if severity_counts:
                colors = {
                    'INFO': '#17a2b8',
                    'WARNING': '#ffc107', 
                    'ERROR': '#dc3545',
                    'CRITICAL': '#6f42c1'
                }
                
                fig_severity = px.bar(
                    x=list(severity_counts.keys()),
                    y=list(severity_counts.values()),
                    title="Distribución por Severidad",
                    color=list(severity_counts.keys()),
                    color_discrete_map=colors
                )
                st.plotly_chart(fig_severity, use_container_width=True)
        
        # Top users
        top_users = summary.get("top_users", [])
        if top_users:
            st.subheader("👥 Usuarios Más Activos")
            
            users_df = pd.DataFrame(top_users, columns=["Usuario", "Actividad"])
            
            fig_users = px.bar(
                users_df,
                x="Usuario",
                y="Actividad",
                title="Actividad por Usuario"
            )
            st.plotly_chart(fig_users, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error al generar resumen: {e}")

def show_detailed_logs(audit_logger: AuditLogger, start_date: date, end_date: date,
                      selected_action: str, selected_severity: str, user_filter: str,
                      resource_filter: str, limit: int, show_metadata: bool):
    """Show detailed audit logs table"""
    
    st.subheader("📋 Logs Detallados")
    
    try:
        # Convert dates to datetime
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        # Prepare filters
        action_filter = None
        if selected_action != "Todas":
            action_filter = AuditActionEnum(selected_action)
        
        severity_filter = None
        if selected_severity != "Todas":
            severity_filter = AuditSeverityEnum(selected_severity)
        
        user_id_filter = user_filter.strip() if user_filter.strip() else None
        resource_type_filter = resource_filter.strip() if resource_filter.strip() else None
        
        # Get logs
        logs = audit_logger.get_audit_logs(
            limit=limit,
            user_id=user_id_filter,
            action=action_filter,
            severity=severity_filter,
            start_date=start_datetime,
            end_date=end_datetime,
            resource_type=resource_type_filter
        )
        
        if not logs:
            st.info("No se encontraron logs con los filtros aplicados.")
            return
        
        st.info(f"Mostrando {len(logs)} logs (máximo {limit})")
        
        # Convert to DataFrame
        logs_data = []
        for log in logs:
            log_entry = {
                "ID": log.id,
                "Timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "Acción": log.action.value,
                "Severidad": log.severity.value,
                "Usuario": log.user_name or log.user_id or "Sistema",
                "Descripción": log.description,
                "Recurso": f"{log.resource_type}#{log.resource_id}" if log.resource_type and log.resource_id else "",
                "IP": log.ip_address or "",
            }
            
            if show_metadata and log.metadata:
                log_entry["Metadatos"] = log.metadata
            
            if log.error_message:
                log_entry["Error"] = log.error_message
            
            logs_data.append(log_entry)
        
        df_logs = pd.DataFrame(logs_data)
        
        # Style the dataframe
        def style_severity(val):
            colors = {
                'INFO': 'color: #17a2b8',
                'WARNING': 'color: #ffc107',
                'ERROR': 'color: #dc3545',
                'CRITICAL': 'color: #6f42c1; font-weight: bold'
            }
            return colors.get(val, '')
        
        styled_df = df_logs.style.applymap(style_severity, subset=['Severidad'])
        st.dataframe(styled_df, use_container_width=True)
        
        # Export options
        st.subheader("📤 Exportar Logs")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Descargar CSV"):
                csv = df_logs.to_csv(index=False)
                st.download_button(
                    label="Descargar archivo CSV",
                    data=csv,
                    file_name=f"audit_logs_{start_date}_{end_date}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("📄 Descargar JSON"):
                import json
                json_data = df_logs.to_json(orient='records', indent=2)
                st.download_button(
                    label="Descargar archivo JSON",
                    data=json_data,
                    file_name=f"audit_logs_{start_date}_{end_date}.json",
                    mime="application/json"
                )
    
    except Exception as e:
        st.error(f"Error al cargar logs: {e}")

def show_audit_analysis(audit_logger: AuditLogger, start_date: date, end_date: date):
    """Show audit analysis and trends"""
    
    st.subheader("📈 Análisis de Tendencias")
    
    try:
        # Convert dates to datetime
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        # Get all logs for analysis
        logs = audit_logger.get_audit_logs(
            limit=1000,
            start_date=start_datetime,
            end_date=end_datetime
        )
        
        if not logs:
            st.info("No hay datos suficientes para el análisis.")
            return
        
        # Convert to DataFrame for analysis
        logs_df = pd.DataFrame([{
            "timestamp": log.timestamp,
            "action": log.action.value,
            "severity": log.severity.value,
            "user_id": log.user_id,
            "user_name": log.user_name,
            "resource_type": log.resource_type,
            "hour": log.timestamp.hour,
            "day_of_week": log.timestamp.weekday(),
            "date": log.timestamp.date()
        } for log in logs])
        
        # Time-based analysis
        col1, col2 = st.columns(2)
        
        with col1:
            # Activity by hour
            hourly_activity = logs_df.groupby('hour').size()
            
            fig_hourly = px.bar(
                x=hourly_activity.index,
                y=hourly_activity.values,
                title="Actividad por Hora del Día",
                labels={"x": "Hora", "y": "Número de Acciones"}
            )
            st.plotly_chart(fig_hourly, use_container_width=True)
        
        with col2:
            # Activity by day of week
            day_names = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
            daily_activity = logs_df.groupby('day_of_week').size()
            
            fig_daily = px.bar(
                x=[day_names[i] for i in daily_activity.index],
                y=daily_activity.values,
                title="Actividad por Día de la Semana",
                labels={"x": "Día", "y": "Número de Acciones"}
            )
            st.plotly_chart(fig_daily, use_container_width=True)
        
        # Timeline analysis
        st.subheader("📅 Línea de Tiempo")
        
        # Daily activity timeline
        daily_timeline = logs_df.groupby('date').size().reset_index()
        daily_timeline.columns = ['date', 'count']
        
        fig_timeline = px.line(
            daily_timeline,
            x='date',
            y='count',
            title="Actividad Diaria",
            markers=True
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # User activity analysis
        st.subheader("👤 Análisis de Usuarios")
        
        user_activity = logs_df.groupby(['user_name', 'action']).size().reset_index()
        user_activity.columns = ['user', 'action', 'count']
        
        # Top actions by user
        if not user_activity.empty:
            fig_user_actions = px.sunburst(
                user_activity,
                path=['user', 'action'],
                values='count',
                title="Acciones por Usuario"
            )
            st.plotly_chart(fig_user_actions, use_container_width=True)
        
        # Security analysis
        st.subheader("🔒 Análisis de Seguridad")
        
        # Failed logins and errors
        security_events = logs_df[
            (logs_df['severity'].isin(['WARNING', 'ERROR', 'CRITICAL'])) |
            (logs_df['action'] == 'LOGIN')
        ]
        
        if not security_events.empty:
            security_summary = security_events.groupby(['action', 'severity']).size().reset_index()
            security_summary.columns = ['action', 'severity', 'count']
            
            fig_security = px.bar(
                security_summary,
                x='action',
                y='count',
                color='severity',
                title="Eventos de Seguridad",
                color_discrete_map={
                    'INFO': '#17a2b8',
                    'WARNING': '#ffc107',
                    'ERROR': '#dc3545',
                    'CRITICAL': '#6f42c1'
                }
            )
            st.plotly_chart(fig_security, use_container_width=True)
        else:
            st.info("No se encontraron eventos de seguridad relevantes.")
    
    except Exception as e:
        st.error(f"Error en el análisis: {e}")

def show_maintenance_options(audit_logger: AuditLogger):
    """Show maintenance and cleanup options"""
    
    st.subheader("🧹 Mantenimiento de Logs")
    
    # Current user info
    current_user = auth.get_current_user()
    if not current_user:
        st.error("No se pudo obtener información del usuario actual.")
        return
    
    # Log cleanup
    st.write("**Limpieza de Logs Antiguos**")
    st.info("Los logs antiguos pueden ser eliminados para liberar espacio en la base de datos.")
    
    days_to_keep = st.number_input(
        "Días a conservar:",
        min_value=30,
        max_value=3650,
        value=365,
        help="Los logs más antiguos que este número de días serán eliminados"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Limpiar Logs Antiguos", type="secondary"):
            with st.spinner("Limpiando logs antiguos..."):
                try:
                    deleted_count = audit_logger.cleanup_old_logs(days_to_keep)
                    
                    # Log this maintenance action
                    audit_logger.log_action(
                        action=AuditActionEnum.CONFIGURATION_CHANGE,
                        description=f"Cleanup of old audit logs: {deleted_count} logs deleted (keeping {days_to_keep} days)",
                        user_id=current_user['username'],
                        user_name=current_user['name'],
                        session_id=current_user.get('session_id'),
                        resource_type="audit_logs",
                        metadata={
                            "deleted_count": deleted_count,
                            "days_kept": days_to_keep
                        }
                    )
                    
                    st.success(f"✅ Se eliminaron {deleted_count} logs antiguos.")
                    
                except Exception as e:
                    st.error(f"Error durante la limpieza: {e}")
    
    with col2:
        if st.button("📊 Vista Previa de Limpieza"):
            try:
                # Get count of logs that would be deleted
                cutoff_date = datetime.now() - timedelta(days=days_to_keep)
                old_logs = audit_logger.get_audit_logs(
                    limit=1000,
                    end_date=cutoff_date
                )
                
                st.info(f"Se eliminarían aproximadamente {len(old_logs)} logs (muestra de hasta 1000).")
                
            except Exception as e:
                st.error(f"Error al calcular vista previa: {e}")
    
    # Manual log entry (for testing)
    st.markdown("---")
    st.write("**Entrada Manual de Log (Solo para Pruebas)**")
    
    with st.expander("➕ Crear Log de Prueba"):
        test_action = st.selectbox(
            "Acción:",
            [action.value for action in AuditActionEnum]
        )
        
        test_description = st.text_input(
            "Descripción:",
            placeholder="Descripción del log de prueba"
        )
        
        test_severity = st.selectbox(
            "Severidad:",
            [severity.value for severity in AuditSeverityEnum]
        )
        
        if st.button("Crear Log de Prueba"):
            if test_description:
                try:
                    audit_logger.log_action(
                        action=AuditActionEnum(test_action),
                        description=f"TEST LOG: {test_description}",
                        user_id=current_user['username'],
                        user_name=current_user['name'],
                        session_id=current_user.get('session_id'),
                        severity=AuditSeverityEnum(test_severity),
                        resource_type="test",
                        metadata={"test_log": True, "created_via": "dashboard"}
                    )
                    
                    st.success("Log de prueba creado exitosamente.")
                    
                except Exception as e:
                    st.error(f"Error al crear log de prueba: {e}")
            else:
                st.error("Por favor, ingrese una descripción.")

if __name__ == "__main__":
    show_audit_logs_page()