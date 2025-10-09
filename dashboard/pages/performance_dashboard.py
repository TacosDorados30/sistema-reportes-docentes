"""
Performance Dashboard Page
Página para monitorear el rendimiento del sistema
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from pathlib import Path

from app.core.performance_monitor import performance_monitor
from app.auth.streamlit_auth import require_auth


def show_performance_dashboard():
    """Show performance monitoring dashboard"""
    
    # Require authentication
    if not require_auth():
        return
    
    st.title("📊 Dashboard de Rendimiento")
    st.markdown("Monitoreo en tiempo real del rendimiento del sistema")
    
    # Control buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("▶️ Iniciar Monitoreo"):
            performance_monitor.start_monitoring(interval=30)
            st.success("Monitoreo iniciado")
            st.rerun()
    
    with col2:
        if st.button("⏹️ Detener Monitoreo"):
            performance_monitor.stop_monitoring()
            st.info("Monitoreo detenido")
            st.rerun()
    
    with col3:
        monitoring_status = "🟢 Activo" if performance_monitor.monitoring_active else "🔴 Inactivo"
        st.metric("Estado del Monitoreo", monitoring_status)
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Métricas Actuales", 
        "📊 Historial", 
        "⚠️ Alertas", 
        "⚙️ Configuración"
    ])
    
    with tab1:
        show_current_metrics()
    
    with tab2:
        show_metrics_history()
    
    with tab3:
        show_performance_alerts()
    
    with tab4:
        show_performance_configuration()


def show_current_metrics():
    """Show current performance metrics"""
    
    st.header("Métricas Actuales del Sistema")
    
    # Get current metrics
    try:
        current_metrics = performance_monitor.get_current_metrics()
        
        if "error" in current_metrics:
            st.error(f"Error al obtener métricas: {current_metrics['error']}")
            return
        
        system_metrics = current_metrics.get("system", {})
        db_metrics = current_metrics.get("database", {})
        summary = current_metrics.get("summary", {})
        
        # System metrics
        st.subheader("🖥️ Métricas del Sistema")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            cpu_percent = system_metrics.get("cpu_percent", 0)
            cpu_color = "normal"
            if cpu_percent > 80:
                cpu_color = "inverse"
            elif cpu_percent > 60:
                cpu_color = "off"
            
            st.metric(
                "CPU Usage",
                f"{cpu_percent:.1f}%",
                delta=None,
                help="Uso actual del procesador"
            )
        
        with col2:
            memory_percent = system_metrics.get("memory_percent", 0)
            memory_used = system_metrics.get("memory_used_mb", 0)
            
            st.metric(
                "Memoria",
                f"{memory_percent:.1f}%",
                delta=f"{memory_used:.0f} MB",
                help="Uso actual de memoria RAM"
            )
        
        with col3:
            disk_percent = system_metrics.get("disk_usage_percent", 0)
            st.metric(
                "Disco",
                f"{disk_percent:.1f}%",
                delta=None,
                help="Uso del disco duro"
            )
        
        with col4:
            connections = system_metrics.get("active_connections", 0)
            st.metric(
                "Conexiones",
                connections,
                delta=None,
                help="Conexiones de red activas"
            )
        
        # Performance summary
        st.subheader("⚡ Resumen de Rendimiento")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_requests = summary.get("total_requests", 0)
            st.metric(
                "Total Requests",
                total_requests,
                delta=None
            )
        
        with col2:
            error_rate = summary.get("error_rate", 0)
            st.metric(
                "Error Rate",
                f"{error_rate:.2f}%",
                delta=None
            )
        
        with col3:
            avg_response = summary.get("avg_response_time", 0)
            st.metric(
                "Tiempo Respuesta",
                f"{avg_response:.0f}ms",
                delta=None
            )
        
        with col4:
            total_queries = summary.get("total_queries", 0)
            st.metric(
                "Total Queries",
                total_queries,
                delta=None
            )
        
        # Database metrics
        if db_metrics:
            st.subheader("🗄️ Métricas de Base de Datos")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_forms = db_metrics.get("total_forms", 0)
                st.metric("Total Formularios", total_forms)
            
            with col2:
                pending_forms = db_metrics.get("pending_forms", 0)
                st.metric("Formularios Pendientes", pending_forms)
            
            with col3:
                avg_query_time = db_metrics.get("avg_query_time_ms", 0)
                st.metric("Tiempo Promedio Query", f"{avg_query_time:.1f}ms")
            
            with col4:
                slow_queries = db_metrics.get("slow_queries", 0)
                st.metric("Queries Lentas", slow_queries)
        
        # Real-time charts
        st.subheader("📊 Gráficos en Tiempo Real")
        
        # Get recent history for charts
        history = performance_monitor.get_metrics_history(hours=1)
        system_history = history.get("system_metrics", [])
        
        if system_history:
            # Create DataFrame
            df = pd.DataFrame(system_history)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # CPU and Memory chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['cpu_percent'],
                mode='lines+markers',
                name='CPU %',
                line=dict(color='#ff6b6b')
            ))
            
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['memory_percent'],
                mode='lines+markers',
                name='Memoria %',
                line=dict(color='#4ecdc4')
            ))
            
            fig.update_layout(
                title="CPU y Memoria - Última Hora",
                xaxis_title="Tiempo",
                yaxis_title="Porcentaje (%)",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Response time chart
            if 'response_time_ms' in df.columns:
                response_df = df[df['response_time_ms'].notna()]
                
                if not response_df.empty:
                    fig2 = px.line(
                        response_df,
                        x='timestamp',
                        y='response_time_ms',
                        title='Tiempo de Respuesta - Última Hora',
                        labels={'response_time_ms': 'Tiempo (ms)', 'timestamp': 'Tiempo'}
                    )
                    fig2.update_layout(height=300)
                    st.plotly_chart(fig2, use_container_width=True)
        
        else:
            st.info("📊 No hay datos históricos disponibles. El monitoreo debe estar activo para generar gráficos.")
    
    except Exception as e:
        st.error(f"Error al mostrar métricas actuales: {e}")


def show_metrics_history():
    """Show historical performance metrics"""
    
    st.header("📊 Historial de Métricas")
    
    # Time period selector
    col1, col2 = st.columns([1, 3])
    
    with col1:
        hours = st.selectbox(
            "Período de tiempo:",
            [1, 6, 12, 24, 48, 72],
            index=3,
            format_func=lambda x: f"Últimas {x} horas"
        )
    
    with col2:
        st.info(f"Mostrando métricas de las últimas {hours} horas")
    
    # Get historical data
    try:
        history = performance_monitor.get_metrics_history(hours=hours)
        system_history = history.get("system_metrics", [])
        db_history = history.get("database_metrics", [])
        
        if not system_history:
            st.warning("📊 No hay datos históricos disponibles para el período seleccionado.")
            return
        
        # Create DataFrame
        df = pd.DataFrame(system_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Performance summary
        summary = performance_monitor.get_performance_summary()
        
        if "error" not in summary:
            st.subheader("📈 Resumen del Período")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "CPU Promedio",
                    f"{summary['averages']['cpu_percent']:.1f}%",
                    delta=f"Máx: {summary['peaks']['max_cpu_percent']:.1f}%"
                )
            
            with col2:
                st.metric(
                    "Memoria Promedio",
                    f"{summary['averages']['memory_percent']:.1f}%",
                    delta=f"Máx: {summary['peaks']['max_memory_percent']:.1f}%"
                )
            
            with col3:
                health_status = summary.get('health_status', 'unknown')
                health_emoji = {
                    'healthy': '🟢',
                    'warning': '🟡',
                    'critical': '🔴'
                }.get(health_status, '⚪')
                
                st.metric(
                    "Estado de Salud",
                    f"{health_emoji} {health_status.title()}",
                    delta=None
                )
        
        # Historical charts
        st.subheader("📊 Gráficos Históricos")
        
        # System metrics over time
        fig1 = go.Figure()
        
        fig1.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['cpu_percent'],
            mode='lines',
            name='CPU %',
            line=dict(color='#ff6b6b', width=2)
        ))
        
        fig1.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['memory_percent'],
            mode='lines',
            name='Memoria %',
            line=dict(color='#4ecdc4', width=2)
        ))
        
        fig1.update_layout(
            title=f"CPU y Memoria - Últimas {hours} horas",
            xaxis_title="Tiempo",
            yaxis_title="Porcentaje (%)",
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig1, use_container_width=True)
        
        # Response time and requests
        if 'response_time_ms' in df.columns and 'request_count' in df.columns:
            fig2 = go.Figure()
            
            # Filter out null response times
            response_df = df[df['response_time_ms'].notna()]
            
            if not response_df.empty:
                fig2.add_trace(go.Scatter(
                    x=response_df['timestamp'],
                    y=response_df['response_time_ms'],
                    mode='lines',
                    name='Tiempo Respuesta (ms)',
                    yaxis='y',
                    line=dict(color='#45b7d1')
                ))
            
            fig2.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['request_count'],
                mode='lines',
                name='Total Requests',
                yaxis='y2',
                line=dict(color='#96ceb4')
            ))
            
            fig2.update_layout(
                title=f"Rendimiento de Requests - Últimas {hours} horas",
                xaxis_title="Tiempo",
                yaxis=dict(title="Tiempo Respuesta (ms)", side="left"),
                yaxis2=dict(title="Total Requests", side="right", overlaying="y"),
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig2, use_container_width=True)
        
        # Database metrics
        if db_history:
            st.subheader("🗄️ Métricas de Base de Datos")
            
            db_df = pd.DataFrame(db_history)
            db_df['timestamp'] = pd.to_datetime(db_df['timestamp'])
            
            fig3 = go.Figure()
            
            fig3.add_trace(go.Scatter(
                x=db_df['timestamp'],
                y=db_df['avg_query_time_ms'],
                mode='lines+markers',
                name='Tiempo Promedio Query (ms)',
                line=dict(color='#f39c12')
            ))
            
            fig3.update_layout(
                title=f"Rendimiento de Base de Datos - Últimas {hours} horas",
                xaxis_title="Tiempo",
                yaxis_title="Tiempo (ms)",
                height=300
            )
            
            st.plotly_chart(fig3, use_container_width=True)
        
        # Data table
        with st.expander("📋 Ver Datos Detallados"):
            st.dataframe(
                df[['timestamp', 'cpu_percent', 'memory_percent', 'response_time_ms', 'request_count']].tail(50),
                use_container_width=True
            )
    
    except Exception as e:
        st.error(f"Error al mostrar historial de métricas: {e}")


def show_performance_alerts():
    """Show performance alerts and warnings"""
    
    st.header("⚠️ Alertas de Rendimiento")
    
    # Check for alert files
    metrics_dir = Path("metrics")
    alert_file = metrics_dir / "performance_alerts.jsonl"
    
    if not alert_file.exists():
        st.info("📊 No hay alertas de rendimiento registradas.")
        return
    
    try:
        # Read alerts from file
        alerts = []
        with open(alert_file, 'r') as f:
            for line in f:
                if line.strip():
                    alerts.append(json.loads(line))
        
        if not alerts:
            st.info("📊 No hay alertas de rendimiento registradas.")
            return
        
        # Show recent alerts
        st.subheader("🚨 Alertas Recientes")
        
        # Sort by timestamp (most recent first)
        alerts.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Show last 20 alerts
        recent_alerts = alerts[:20]
        
        for alert in recent_alerts:
            timestamp = datetime.fromisoformat(alert['timestamp'])
            alert_messages = alert['alerts']
            
            with st.expander(f"⚠️ {timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {len(alert_messages)} alertas"):
                for message in alert_messages:
                    st.warning(message)
        
        # Alert statistics
        st.subheader("📊 Estadísticas de Alertas")
        
        # Count alerts by type
        alert_types = {}
        for alert in alerts:
            for message in alert['alerts']:
                if 'CPU' in message:
                    alert_types['CPU'] = alert_types.get('CPU', 0) + 1
                elif 'memory' in message:
                    alert_types['Memory'] = alert_types.get('Memory', 0) + 1
                elif 'response time' in message:
                    alert_types['Response Time'] = alert_types.get('Response Time', 0) + 1
        
        if alert_types:
            col1, col2 = st.columns(2)
            
            with col1:
                # Alert type distribution
                fig = px.pie(
                    values=list(alert_types.values()),
                    names=list(alert_types.keys()),
                    title="Distribución de Tipos de Alerta"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Alert frequency over time
                alert_dates = [datetime.fromisoformat(a['timestamp']).date() for a in alerts]
                date_counts = {}
                for date in alert_dates:
                    date_counts[date] = date_counts.get(date, 0) + 1
                
                if date_counts:
                    dates = list(date_counts.keys())
                    counts = list(date_counts.values())
                    
                    fig2 = px.bar(
                        x=dates,
                        y=counts,
                        title="Alertas por Día",
                        labels={'x': 'Fecha', 'y': 'Número de Alertas'}
                    )
                    st.plotly_chart(fig2, use_container_width=True)
        
        # Clear alerts button
        if st.button("🗑️ Limpiar Alertas Antiguas"):
            # Keep only last 100 alerts
            if len(alerts) > 100:
                recent_alerts = alerts[:100]
                with open(alert_file, 'w') as f:
                    for alert in recent_alerts:
                        f.write(json.dumps(alert) + '\n')
                st.success(f"Se mantuvieron las últimas 100 alertas, se eliminaron {len(alerts) - 100}")
                st.rerun()
    
    except Exception as e:
        st.error(f"Error al mostrar alertas: {e}")


def show_performance_configuration():
    """Show performance monitoring configuration"""
    
    st.header("⚙️ Configuración de Monitoreo")
    
    # Current configuration
    st.subheader("📋 Configuración Actual")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Umbrales de Alerta:**")
        st.write(f"- CPU: {performance_monitor.cpu_threshold}%")
        st.write(f"- Memoria: {performance_monitor.memory_threshold}%")
        st.write(f"- Tiempo de respuesta: {performance_monitor.response_time_threshold}ms")
    
    with col2:
        st.write("**Configuración de Historial:**")
        st.write(f"- Máximo historial: {performance_monitor.max_history} puntos")
        st.write(f"- Requests recientes: 100 puntos")
        st.write(f"- Queries recientes: 100 puntos")
    
    # Configuration form
    st.subheader("🔧 Ajustar Configuración")
    
    with st.form("performance_config"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_cpu_threshold = st.slider(
                "Umbral de CPU (%)",
                min_value=50,
                max_value=95,
                value=int(performance_monitor.cpu_threshold),
                step=5
            )
            
            new_memory_threshold = st.slider(
                "Umbral de Memoria (%)",
                min_value=60,
                max_value=95,
                value=int(performance_monitor.memory_threshold),
                step=5
            )
        
        with col2:
            new_response_threshold = st.slider(
                "Umbral de Tiempo de Respuesta (ms)",
                min_value=1000,
                max_value=10000,
                value=int(performance_monitor.response_time_threshold),
                step=500
            )
            
            monitoring_interval = st.selectbox(
                "Intervalo de Monitoreo (segundos)",
                [15, 30, 60, 120, 300],
                index=1
            )
        
        if st.form_submit_button("💾 Guardar Configuración"):
            # Update thresholds
            performance_monitor.cpu_threshold = new_cpu_threshold
            performance_monitor.memory_threshold = new_memory_threshold
            performance_monitor.response_time_threshold = new_response_threshold
            
            st.success("✅ Configuración actualizada correctamente")
            
            # Restart monitoring with new interval if active
            if performance_monitor.monitoring_active:
                performance_monitor.stop_monitoring()
                performance_monitor.start_monitoring(interval=monitoring_interval)
                st.info(f"🔄 Monitoreo reiniciado con intervalo de {monitoring_interval} segundos")
    
    # Maintenance actions
    st.subheader("🧹 Mantenimiento")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Limpiar Métricas Antiguas"):
            deleted_count = performance_monitor.cleanup_old_metrics(days_to_keep=7)
            st.success(f"Se eliminaron {deleted_count} archivos de métricas antiguos")
    
    with col2:
        if st.button("🔄 Reiniciar Contadores"):
            performance_monitor.request_counter = 0
            performance_monitor.error_counter = 0
            performance_monitor.query_counter = 0
            st.success("Contadores reiniciados")
    
    with col3:
        if st.button("📊 Exportar Métricas"):
            # Create export data
            export_data = {
                "export_timestamp": datetime.utcnow().isoformat(),
                "current_metrics": performance_monitor.get_current_metrics(),
                "performance_summary": performance_monitor.get_performance_summary(),
                "configuration": {
                    "cpu_threshold": performance_monitor.cpu_threshold,
                    "memory_threshold": performance_monitor.memory_threshold,
                    "response_time_threshold": performance_monitor.response_time_threshold
                }
            }
            
            st.download_button(
                label="📥 Descargar Métricas JSON",
                data=json.dumps(export_data, indent=2, default=str),
                file_name=f"performance_metrics_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )


if __name__ == "__main__":
    show_performance_dashboard()