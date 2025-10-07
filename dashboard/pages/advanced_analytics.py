import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.connection import SessionLocal
from app.database.crud import FormularioCRUD
from app.core.data_processor import DataProcessor
from app.core.metrics_calculator import MetricsCalculator
from dashboard.components.visualizations import InteractiveVisualizations

def show_advanced_analytics():
    """Show advanced analytics page with interactive visualizations"""
    
    st.title("📊 Análisis Avanzado")
    st.markdown("Visualizaciones interactivas y análisis profundo de los datos académicos.")
    
    # Initialize visualization class
    viz = InteractiveVisualizations()
    
    # Load data
    try:
        all_forms, metrics = load_analytics_data()
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return
    
    if not all_forms:
        st.info("No hay datos disponibles para análisis.")
        return
    
    # Sidebar controls
    st.sidebar.header("🎛️ Controles de Visualización")
    
    # Date range selector
    min_date = min([f.fecha_envio for f in all_forms if f.fecha_envio])
    max_date = max([f.fecha_envio for f in all_forms if f.fecha_envio])
    
    date_range = st.sidebar.date_input(
        "Rango de fechas:",
        value=(min_date.date(), max_date.date()),
        min_value=min_date.date(),
        max_value=max_date.date()
    )
    
    # Chart type selector
    chart_types = st.sidebar.multiselect(
        "Tipos de gráficos:",
        ["Sunburst", "Timeline", "Heatmap", "Funnel", "Gauge", "Radar", "Treemap"],
        default=["Sunburst", "Timeline", "Funnel"]
    )
    
    # Filter data by date range
    if len(date_range) == 2:
        filtered_forms = [
            f for f in all_forms 
            if f.fecha_envio and date_range[0] <= f.fecha_envio.date() <= date_range[1]
        ]
    else:
        filtered_forms = all_forms
    
    # Convert to DataFrame for analysis
    df = convert_forms_to_dataframe(filtered_forms)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.subheader("📈 Métricas Rápidas")
        st.metric("Total Formularios", len(filtered_forms))
        st.metric("Rango de Análisis", f"{len(date_range)} días" if len(date_range) == 2 else "Todos")
        
        if filtered_forms:
            approved_count = len([f for f in filtered_forms if f.estado.value == 'APROBADO'])
            approval_rate = (approved_count / len(filtered_forms)) * 100
            st.metric("Tasa de Aprobación", f"{approval_rate:.1f}%")
    
    with col1:
        st.subheader("🎯 Visualizaciones Interactivas")
        
        # Create tabs for different visualization categories
        tab1, tab2, tab3 = st.tabs(["📊 Distribuciones", "📈 Tendencias", "🔍 Análisis Profundo"])
        
        with tab1:
            show_distribution_charts(viz, metrics, df, chart_types)
        
        with tab2:
            show_trend_charts(viz, df, chart_types)
        
        with tab3:
            show_deep_analysis_charts(viz, df, filtered_forms, chart_types)

@st.cache_data(ttl=300)
def load_analytics_data():
    """Load data for analytics with caching"""
    db = SessionLocal()
    try:
        crud = FormularioCRUD(db)
        all_forms = crud.get_all_formularios(limit=1000)
        metrics = crud.get_metricas_generales()
        return all_forms, metrics
    finally:
        db.close()

def convert_forms_to_dataframe(forms):
    """Convert forms to DataFrame for analysis"""
    data = []
    for form in forms:
        data.append({
            'id': form.id,
            'nombre_completo': form.nombre_completo,
            'correo_institucional': form.correo_institucional,
            'estado': form.estado.value,
            'fecha_envio': form.fecha_envio,
            'fecha_revision': form.fecha_revision,
            'revisado_por': form.revisado_por,
            'total_cursos': len(form.cursos_capacitacion),
            'total_publicaciones': len(form.publicaciones),
            'total_eventos': len(form.eventos_academicos),
            'total_disenos': len(form.diseno_curricular),
            'total_movilidades': len(form.movilidad),
            'total_reconocimientos': len(form.reconocimientos),
            'total_certificaciones': len(form.certificaciones),
            'total_items': (
                len(form.cursos_capacitacion) + len(form.publicaciones) +
                len(form.eventos_academicos) + len(form.diseno_curricular) +
                len(form.movilidad) + len(form.reconocimientos) +
                len(form.certificaciones)
            )
        })
    
    return pd.DataFrame(data)de
f show_distribution_charts(viz, metrics, df, chart_types):
    """Show distribution-based charts"""
    
    if "Sunburst" in chart_types:
        st.subheader("🌅 Distribución Jerárquica de Actividades")
        sunburst_fig = viz.create_activities_sunburst(metrics)
        if sunburst_fig:
            st.plotly_chart(sunburst_fig, use_container_width=True)
        else:
            st.info("No hay datos suficientes para el gráfico sunburst.")
    
    if "Treemap" in chart_types and not df.empty:
        st.subheader("🗺️ Mapa de Árbol - Actividades por Formulario")
        
        # Create treemap data
        activity_totals = {
            'Cursos': df['total_cursos'].sum(),
            'Publicaciones': df['total_publicaciones'].sum(),
            'Eventos': df['total_eventos'].sum(),
            'Diseños': df['total_disenos'].sum(),
            'Movilidades': df['total_movilidades'].sum(),
            'Reconocimientos': df['total_reconocimientos'].sum(),
            'Certificaciones': df['total_certificaciones'].sum()
        }
        
        treemap_fig = viz.create_treemap(activity_totals, "Distribución de Actividades Académicas")
        if treemap_fig:
            st.plotly_chart(treemap_fig, use_container_width=True)
    
    if "Funnel" in chart_types:
        st.subheader("🔽 Embudo de Procesamiento")
        funnel_fig = viz.create_funnel_chart(metrics)
        if funnel_fig:
            st.plotly_chart(funnel_fig, use_container_width=True)
        else:
            st.info("No hay datos suficientes para el gráfico de embudo.")

def show_trend_charts(viz, df, chart_types):
    """Show trend-based charts"""
    
    if df.empty:
        st.info("No hay datos disponibles para análisis de tendencias.")
        return
    
    if "Timeline" in chart_types:
        st.subheader("⏰ Línea de Tiempo de Envíos")
        timeline_fig = viz.create_timeline_chart(df)
        if timeline_fig:
            st.plotly_chart(timeline_fig, use_container_width=True)
        else:
            st.info("No hay datos suficientes para la línea de tiempo.")
    
    if "Heatmap" in chart_types:
        st.subheader("🔥 Mapa de Calor - Actividad por Día")
        heatmap_fig = viz.create_heatmap_calendar(df)
        if heatmap_fig:
            st.plotly_chart(heatmap_fig, use_container_width=True)
        else:
            st.info("No hay datos suficientes para el mapa de calor.")
    
    # Monthly trend analysis
    if 'fecha_envio' in df.columns:
        st.subheader("📈 Análisis de Tendencias Mensuales")
        
        df_monthly = df.copy()
        df_monthly['fecha_envio'] = pd.to_datetime(df_monthly['fecha_envio'])
        df_monthly['month_year'] = df_monthly['fecha_envio'].dt.to_period('M')
        
        monthly_stats = df_monthly.groupby('month_year').agg({
            'id': 'count',
            'total_items': 'mean',
            'estado': lambda x: (x == 'APROBADO').sum()
        }).reset_index()
        
        monthly_stats.columns = ['Período', 'Total_Formularios', 'Promedio_Items', 'Aprobados']
        monthly_stats['Período'] = monthly_stats['Período'].astype(str)
        
        col1, col2 = st.columns(2)
        
        with col1:
            import plotly.express as px
            fig_monthly = px.line(
                monthly_stats,
                x='Período',
                y='Total_Formularios',
                title='Formularios por Mes',
                markers=True
            )
            st.plotly_chart(fig_monthly, use_container_width=True)
        
        with col2:
            fig_approval = px.bar(
                monthly_stats,
                x='Período',
                y='Aprobados',
                title='Formularios Aprobados por Mes',
                color='Aprobados',
                color_continuous_scale='Greens'
            )
            st.plotly_chart(fig_approval, use_container_width=True)

def show_deep_analysis_charts(viz, df, forms, chart_types):
    """Show deep analysis charts"""
    
    if df.empty:
        st.info("No hay datos disponibles para análisis profundo.")
        return
    
    if "Gauge" in chart_types:
        st.subheader("⚡ Indicadores de Rendimiento (KPIs)")
        
        # Calculate KPIs
        total_forms = len(df)
        approved_forms = len(df[df['estado'] == 'APROBADO'])
        approval_rate = (approved_forms / total_forms * 100) if total_forms > 0 else 0
        
        avg_items_per_form = df['total_items'].mean() if not df.empty else 0
        productivity_score = min(avg_items_per_form * 10, 100)  # Scale to 0-100
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            gauge_approval = viz.create_gauge_chart(
                approval_rate,
                "Tasa de Aprobación (%)",
                max_value=100,
                threshold_good=70,
                threshold_excellent=90
            )
            st.plotly_chart(gauge_approval, use_container_width=True)
        
        with col2:
            gauge_productivity = viz.create_gauge_chart(
                productivity_score,
                "Índice de Productividad",
                max_value=100,
                threshold_good=60,
                threshold_excellent=80
            )
            st.plotly_chart(gauge_productivity, use_container_width=True)
        
        with col3:
            # Activity diversity score
            activity_columns = ['total_cursos', 'total_publicaciones', 'total_eventos', 
                              'total_disenos', 'total_movilidades', 'total_reconocimientos']
            diversity_score = 0
            if not df.empty:
                for col in activity_columns:
                    if col in df.columns and df[col].sum() > 0:
                        diversity_score += 1
                diversity_score = (diversity_score / len(activity_columns)) * 100
            
            gauge_diversity = viz.create_gauge_chart(
                diversity_score,
                "Diversidad de Actividades (%)",
                max_value=100,
                threshold_good=50,
                threshold_excellent=75
            )
            st.plotly_chart(gauge_diversity, use_container_width=True)
    
    if "Radar" in chart_types and not df.empty:
        st.subheader("🎯 Análisis Multidimensional")
        
        # Calculate average values for radar chart
        activity_columns = ['total_cursos', 'total_publicaciones', 'total_eventos', 
                          'total_disenos', 'total_movilidades', 'total_reconocimientos']
        
        radar_categories = []
        radar_values = []
        
        for col in activity_columns:
            if col in df.columns:
                avg_value = df[col].mean()
                radar_categories.append(col.replace('total_', '').title())
                radar_values.append(min(avg_value * 20, 100))  # Scale to 0-100
        
        if radar_categories and radar_values:
            radar_fig = viz.create_radar_chart(
                radar_categories,
                radar_values,
                "Perfil de Actividades Académicas Promedio"
            )
            st.plotly_chart(radar_fig, use_container_width=True)
    
    # Correlation analysis
    if not df.empty and len(df) > 1:
        st.subheader("🔗 Análisis de Correlaciones")
        
        # Select numeric columns for correlation
        numeric_columns = ['total_cursos', 'total_publicaciones', 'total_eventos', 
                          'total_disenos', 'total_movilidades', 'total_reconocimientos', 
                          'total_certificaciones', 'total_items']
        
        available_columns = [col for col in numeric_columns if col in df.columns]
        
        if len(available_columns) > 1:
            correlation_matrix = df[available_columns].corr()
            
            corr_fig = viz.create_correlation_heatmap(
                correlation_matrix,
                "Matriz de Correlación entre Actividades"
            )
            st.plotly_chart(corr_fig, use_container_width=True)
            
            # Show insights
            st.subheader("💡 Insights de Correlación")
            
            # Find strongest correlations
            corr_pairs = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    corr_value = correlation_matrix.iloc[i, j]
                    if abs(corr_value) > 0.3:  # Only show significant correlations
                        corr_pairs.append({
                            'var1': correlation_matrix.columns[i],
                            'var2': correlation_matrix.columns[j],
                            'correlation': corr_value
                        })
            
            if corr_pairs:
                corr_df = pd.DataFrame(corr_pairs)
                corr_df = corr_df.sort_values('correlation', key=abs, ascending=False)
                
                for _, row in corr_df.head(3).iterrows():
                    correlation_strength = "fuerte" if abs(row['correlation']) > 0.7 else "moderada"
                    correlation_type = "positiva" if row['correlation'] > 0 else "negativa"
                    
                    st.write(f"• **{row['var1']}** y **{row['var2']}**: "
                           f"Correlación {correlation_strength} {correlation_type} "
                           f"({row['correlation']:.3f})")
            else:
                st.info("No se encontraron correlaciones significativas entre las variables.")

if __name__ == "__main__":
    show_advanced_analytics()