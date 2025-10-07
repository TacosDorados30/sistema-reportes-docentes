import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Any

def create_status_pie_chart(metrics):
    """Create pie chart for form status distribution"""
    
    status_data = {
        'Estado': ['Pendientes', 'Aprobados', 'Rechazados'],
        'Cantidad': [
            metrics.formularios_pendientes,
            metrics.formularios_aprobados,
            metrics.formularios_rechazados
        ]
    }
    
    # Filter out zero values
    filtered_data = {
        'Estado': [],
        'Cantidad': []
    }
    
    for estado, cantidad in zip(status_data['Estado'], status_data['Cantidad']):
        if cantidad > 0:
            filtered_data['Estado'].append(estado)
            filtered_data['Cantidad'].append(cantidad)
    
    if not filtered_data['Estado']:
        return None
    
    fig = px.pie(
        values=filtered_data['Cantidad'],
        names=filtered_data['Estado'],
        title="Distribución por Estado",
        color_discrete_map={
            'Pendientes': '#ff9800',
            'Aprobados': '#4caf50',
            'Rechazados': '#f44336'
        },
        hole=0.3  # Donut chart
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Cantidad: %{value}<br>Porcentaje: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_activities_bar_chart(metrics):
    """Create bar chart for academic activities"""
    
    activities_data = {
        'Actividad': ['Cursos', 'Publicaciones', 'Eventos', 'Diseños', 'Movilidades', 'Reconocimientos', 'Certificaciones'],
        'Cantidad': [
            metrics.total_cursos,
            metrics.total_publicaciones,
            metrics.total_eventos,
            metrics.total_disenos_curriculares,
            metrics.total_movilidades,
            metrics.total_reconocimientos,
            metrics.total_certificaciones
        ]
    }
    
    # Create DataFrame and filter out zero values
    df = pd.DataFrame(activities_data)
    df = df[df['Cantidad'] > 0]
    
    if df.empty:
        return None
    
    fig = px.bar(
        df,
        x='Actividad',
        y='Cantidad',
        title="Actividades Académicas (Aprobadas)",
        color='Cantidad',
        color_continuous_scale='Blues',
        text='Cantidad'
    )
    
    fig.update_traces(
        texttemplate='%{text}',
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Cantidad: %{y}<extra></extra>'
    )
    
    fig.update_layout(
        showlegend=False,
        xaxis_title="Tipo de Actividad",
        yaxis_title="Cantidad",
        xaxis_tickangle=-45
    )
    
    return fig

def create_monthly_trend_chart(df):
    """Create line chart for monthly submission trends"""
    
    if df.empty or 'month' not in df.columns or 'year' not in df.columns:
        return None
    
    # Group by year and month
    monthly_counts = df.groupby(['year', 'month']).size().reset_index(name='count')
    monthly_counts['period'] = monthly_counts['year'].astype(str) + '-' + monthly_counts['month'].astype(str).str.zfill(2)
    
    # Sort by period
    monthly_counts = monthly_counts.sort_values('period')
    
    fig = px.line(
        monthly_counts,
        x='period',
        y='count',
        title='Tendencia de Envíos por Mes',
        markers=True,
        line_shape='spline'
    )
    
    fig.update_traces(
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8, color='#1f77b4'),
        hovertemplate='<b>%{x}</b><br>Formularios: %{y}<extra></extra>'
    )
    
    fig.update_layout(
        xaxis_title="Período (Año-Mes)",
        yaxis_title="Número de Formularios",
        xaxis_tickangle=-45,
        hovermode='x unified'
    )
    
    return fig

def create_status_timeline_chart(df):
    """Create stacked bar chart for status distribution over time"""
    
    if df.empty or 'month' not in df.columns or 'year' not in df.columns or 'estado' not in df.columns:
        return None
    
    # Group by year, month, and status
    status_time = df.groupby(['year', 'month', 'estado']).size().reset_index(name='count')
    status_time['period'] = status_time['year'].astype(str) + '-' + status_time['month'].astype(str).str.zfill(2)
    
    # Sort by period
    status_time = status_time.sort_values('period')
    
    fig = px.bar(
        status_time,
        x='period',
        y='count',
        color='estado',
        title='Distribución de Estados por Mes',
        color_discrete_map={
            'PENDIENTE': '#ff9800',
            'APROBADO': '#4caf50',
            'RECHAZADO': '#f44336'
        }
    )
    
    fig.update_layout(
        xaxis_title="Período (Año-Mes)",
        yaxis_title="Número de Formularios",
        xaxis_tickangle=-45,
        legend_title="Estado",
        hovermode='x unified'
    )
    
    return fig

def create_productivity_radar_chart(productivity_metrics):
    """Create radar chart for productivity metrics"""
    
    if not productivity_metrics:
        return None
    
    # Extract metrics for radar chart
    categories = []
    values = []
    
    if 'eficiencia_capacitacion' in productivity_metrics:
        cap = productivity_metrics['eficiencia_capacitacion']
        categories.extend(['Cursos por Docente', 'Horas por Docente'])
        values.extend([
            min(cap.get('cursos_por_docente', 0) * 10, 100),  # Scale to 0-100
            min(cap.get('horas_por_docente', 0) / 2, 100)     # Scale to 0-100
        ])
    
    if 'productividad_investigacion' in productivity_metrics:
        inv = productivity_metrics['productividad_investigacion']
        categories.extend(['Publicaciones por Docente', 'Tasa de Aceptación'])
        values.extend([
            min(inv.get('publicaciones_por_docente', 0) * 20, 100),  # Scale to 0-100
            inv.get('tasa_aceptacion', 0)
        ])
    
    if 'actividad_academica' in productivity_metrics:
        act = productivity_metrics['actividad_academica']
        categories.extend(['Eventos por Docente', 'Tasa de Liderazgo'])
        values.extend([
            min(act.get('eventos_por_docente', 0) * 15, 100),  # Scale to 0-100
            act.get('tasa_liderazgo', 0)
        ])
    
    if not categories:
        return None
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Productividad',
        line_color='#1f77b4',
        fillcolor='rgba(31, 119, 180, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        title="Índices de Productividad Académica"
    )
    
    return fig

def create_comparison_chart(current_data, previous_data, period_name):
    """Create comparison chart between two periods"""
    
    if not current_data or not previous_data:
        return None
    
    # Extract comparable metrics
    metrics = ['cursos', 'publicaciones', 'eventos', 'disenos']
    current_values = []
    previous_values = []
    metric_names = []
    
    for metric in metrics:
        current_val = current_data.get(metric, {}).get('total', 0)
        previous_val = previous_data.get(metric, {}).get('total', 0)
        
        if current_val > 0 or previous_val > 0:
            current_values.append(current_val)
            previous_values.append(previous_val)
            metric_names.append(metric.capitalize())
    
    if not metric_names:
        return None
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Período Actual',
        x=metric_names,
        y=current_values,
        marker_color='#1f77b4',
        text=current_values,
        textposition='outside'
    ))
    
    fig.add_trace(go.Bar(
        name='Período Anterior',
        x=metric_names,
        y=previous_values,
        marker_color='#ff7f0e',
        text=previous_values,
        textposition='outside'
    ))
    
    fig.update_layout(
        title=f'Comparación con {period_name}',
        xaxis_title='Actividades',
        yaxis_title='Cantidad',
        barmode='group',
        hovermode='x unified'
    )
    
    return fig

def create_heatmap_chart(data_by_month):
    """Create heatmap for activity distribution by month"""
    
    if not data_by_month:
        return None
    
    # Prepare data for heatmap
    months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
              'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    
    activities = ['Cursos', 'Publicaciones', 'Eventos', 'Diseños']
    
    # Create matrix
    z_data = []
    for activity in activities:
        row = []
        for month in range(1, 13):
            value = data_by_month.get(month, {}).get(activity.lower(), 0)
            row.append(value)
        z_data.append(row)
    
    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=months,
        y=activities,
        colorscale='Blues',
        hoverongaps=False,
        hovertemplate='<b>%{y}</b><br>%{x}: %{z}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Distribución de Actividades por Mes',
        xaxis_title='Mes',
        yaxis_title='Tipo de Actividad'
    )
    
    return fig

def create_kpi_gauge_chart(kpi_value, kpi_name, max_value=100):
    """Create gauge chart for KPI visualization"""
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=kpi_value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': kpi_name},
        delta={'reference': max_value * 0.7},  # Reference point at 70%
        gauge={
            'axis': {'range': [None, max_value]},
            'bar': {'color': "#1f77b4"},
            'steps': [
                {'range': [0, max_value * 0.5], 'color': "lightgray"},
                {'range': [max_value * 0.5, max_value * 0.8], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_value * 0.9
            }
        }
    ))
    
    fig.update_layout(height=300)
    
    return fig

def create_funnel_chart(funnel_data):
    """Create funnel chart for process flow visualization"""
    
    if not funnel_data:
        return None
    
    fig = go.Figure(go.Funnel(
        y=list(funnel_data.keys()),
        x=list(funnel_data.values()),
        textinfo="value+percent initial",
        marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    ))
    
    fig.update_layout(
        title="Flujo de Procesamiento de Formularios"
    )
    
    return fig