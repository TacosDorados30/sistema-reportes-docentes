import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import streamlit as st
from datetime import datetime, timedelta

class InteractiveVisualizations:
    """Class for creating interactive visualizations with Plotly"""
    
    def __init__(self):
        self.color_palette = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'warning': '#ff9800',
            'danger': '#d62728',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40'
        }
        
        self.status_colors = {
            'PENDIENTE': '#ff9800',
            'APROBADO': '#4caf50',
            'RECHAZADO': '#f44336'
        }
    
    def create_enhanced_status_pie(self, metrics, show_percentages=True, hole_size=0.4):
        """Create enhanced pie chart for status distribution"""
        
        data = {
            'Estado': ['Pendientes', 'Aprobados', 'Rechazados'],
            'Cantidad': [
                metrics.formularios_pendientes,
                metrics.formularios_aprobados,
                metrics.formularios_rechazados
            ],
            'Colors': ['#ff9800', '#4caf50', '#f44336']
        }
        
        # Filter out zero values
        filtered_data = {k: [] for k in data.keys()}
        for i, cantidad in enumerate(data['Cantidad']):
            if cantidad > 0:
                for key in data.keys():
                    filtered_data[key].append(data[key][i])
        
        if not filtered_data['Estado']:
            return None
        
        fig = go.Figure(data=[go.Pie(
            labels=filtered_data['Estado'],
            values=filtered_data['Cantidad'],
            hole=hole_size,
            marker_colors=filtered_data['Colors'],
            textinfo='label+percent' if show_percentages else 'label+value',
            textposition='auto',
            hovertemplate='<b>%{label}</b><br>' +
                         'Cantidad: %{value}<br>' +
                         'Porcentaje: %{percent}<br>' +
                         '<extra></extra>',
            pull=[0.1 if estado == 'Pendientes' else 0 for estado in filtered_data['Estado']]
        )])
        
        fig.update_layout(
            title={
                'text': 'Distribución de Estados de Formularios',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': self.color_palette['dark']}
            },
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            margin=dict(t=60, b=60, l=60, r=60),
            height=400
        )
        
        return fig
    
    def create_activities_sunburst(self, metrics):
        """Create sunburst chart for academic activities hierarchy"""
        
        # Prepare hierarchical data
        activities = {
            'Capacitación': metrics.total_cursos,
            'Investigación': metrics.total_publicaciones,
            'Eventos': metrics.total_eventos,
            'Desarrollo': metrics.total_disenos_curriculares,
            'Movilidad': metrics.total_movilidades,
            'Reconocimientos': metrics.total_reconocimientos,
            'Certificaciones': metrics.total_certificaciones
        }
        
        # Filter out zero values
        activities = {k: v for k, v in activities.items() if v > 0}
        
        if not activities:
            return None
        
        # Create sunburst data
        labels = ['Actividades Académicas'] + list(activities.keys())
        parents = [''] + ['Actividades Académicas'] * len(activities)
        values = [sum(activities.values())] + list(activities.values())
        
        fig = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            hovertemplate='<b>%{label}</b><br>Cantidad: %{value}<br><extra></extra>',
            maxdepth=2
        ))
        
        fig.update_layout(
            title={
                'text': 'Distribución de Actividades Académicas',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            height=500,
            margin=dict(t=60, b=60, l=60, r=60)
        )
        
        return fig
    
    def create_timeline_chart(self, df, date_column='fecha_envio', status_column='estado'):
        """Create interactive timeline chart"""
        
        if df.empty or date_column not in df.columns:
            return None
        
        # Prepare data
        df_timeline = df.copy()
        df_timeline[date_column] = pd.to_datetime(df_timeline[date_column])
        df_timeline = df_timeline.sort_values(date_column)
        
        # Group by date and status
        timeline_data = df_timeline.groupby([
            df_timeline[date_column].dt.date,
            status_column
        ]).size().reset_index(name='count')
        
        timeline_data['date'] = pd.to_datetime(timeline_data[date_column])
        
        fig = px.scatter(
            timeline_data,
            x='date',
            y='count',
            color=status_column,
            size='count',
            color_discrete_map=self.status_colors,
            title='Línea de Tiempo de Envíos de Formularios',
            labels={
                'date': 'Fecha',
                'count': 'Número de Formularios',
                status_column: 'Estado'
            }
        )
        
        fig.update_traces(
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         'Fecha: %{x}<br>' +
                         'Cantidad: %{y}<br>' +
                         '<extra></extra>'
        )
        
        fig.update_layout(
            height=400,
            hovermode='x unified',
            xaxis_title="Fecha",
            yaxis_title="Número de Formularios"
        )
        
        return fig
    
    def create_heatmap_calendar(self, df, date_column='fecha_envio'):
        """Create calendar heatmap"""
        
        if df.empty or date_column not in df.columns:
            return None
        
        # Prepare data
        df_cal = df.copy()
        df_cal[date_column] = pd.to_datetime(df_cal[date_column])
        df_cal['date'] = df_cal[date_column].dt.date
        df_cal['weekday'] = df_cal[date_column].dt.day_name()
        df_cal['week'] = df_cal[date_column].dt.isocalendar().week
        df_cal['month'] = df_cal[date_column].dt.month_name()
        
        # Count submissions per day
        daily_counts = df_cal.groupby('date').size().reset_index(name='count')
        daily_counts['date'] = pd.to_datetime(daily_counts['date'])
        daily_counts['weekday'] = daily_counts['date'].dt.day_name()
        daily_counts['week'] = daily_counts['date'].dt.isocalendar().week
        
        # Create pivot table for heatmap
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weeks = sorted(daily_counts['week'].unique())
        
        heatmap_data = []
        for week in weeks:
            week_data = []
            for weekday in weekdays:
                count = daily_counts[
                    (daily_counts['week'] == week) & 
                    (daily_counts['weekday'] == weekday)
                ]['count'].sum()
                week_data.append(count)
            heatmap_data.append(week_data)
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=weekdays,
            y=[f'Semana {w}' for w in weeks],
            colorscale='Blues',
            hoverongaps=False,
            hovertemplate='<b>%{y}</b><br>%{x}: %{z} formularios<extra></extra>'
        ))
        
        fig.update_layout(
            title='Calendario de Actividad - Envíos por Día',
            xaxis_title='Día de la Semana',
            yaxis_title='Semana del Año',
            height=400
        )
        
        return fig
    
    def create_funnel_chart(self, metrics):
        """Create funnel chart for form processing flow"""
        
        total = metrics.total_formularios
        if total == 0:
            return None
        
        stages = [
            ('Formularios Enviados', total),
            ('En Revisión', metrics.formularios_pendientes),
            ('Procesados', metrics.formularios_aprobados + metrics.formularios_rechazados),
            ('Aprobados', metrics.formularios_aprobados)
        ]
        
        fig = go.Figure(go.Funnel(
            y=[stage[0] for stage in stages],
            x=[stage[1] for stage in stages],
            textinfo="value+percent initial",
            marker=dict(
                color=['#1f77b4', '#ff9800', '#2ca02c', '#4caf50'],
                line=dict(width=2, color='white')
            ),
            hovertemplate='<b>%{y}</b><br>Cantidad: %{x}<br>% del total: %{percentInitial}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Embudo de Procesamiento de Formularios',
            height=400,
            margin=dict(t=60, b=60, l=60, r=60)
        )
        
        return fig
    
    def create_gauge_chart(self, value, title, max_value=100, threshold_good=70, threshold_excellent=90):
        """Create gauge chart for KPIs"""
        
        # Determine color based on value
        if value >= threshold_excellent:
            color = '#4caf50'  # Green
        elif value >= threshold_good:
            color = '#ff9800'  # Orange
        else:
            color = '#f44336'  # Red
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title, 'font': {'size': 16}},
            delta={'reference': threshold_good},
            gauge={
                'axis': {'range': [None, max_value], 'tickwidth': 1},
                'bar': {'color': color, 'thickness': 0.3},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, threshold_good], 'color': '#ffebee'},
                    {'range': [threshold_good, threshold_excellent], 'color': '#fff3e0'},
                    {'range': [threshold_excellent, max_value], 'color': '#e8f5e8'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': threshold_excellent
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(t=40, b=40, l=40, r=40)
        )
        
        return fig
    
    def create_radar_chart(self, categories, values, title="Radar Chart"):
        """Create radar chart for multi-dimensional analysis"""
        
        if len(categories) != len(values):
            return None
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Métricas',
            line_color=self.color_palette['primary'],
            fillcolor=f"rgba(31, 119, 180, 0.3)"
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(values) * 1.1] if values else [0, 100],
                    tickfont=dict(size=10)
                ),
                angularaxis=dict(
                    tickfont=dict(size=12)
                )
            ),
            showlegend=False,
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center'
            },
            height=400
        )
        
        return fig
    
    def create_treemap(self, data_dict, title="Treemap"):
        """Create treemap visualization"""
        
        if not data_dict:
            return None
        
        # Filter out zero values
        filtered_data = {k: v for k, v in data_dict.items() if v > 0}
        
        if not filtered_data:
            return None
        
        labels = list(filtered_data.keys())
        values = list(filtered_data.values())
        
        fig = go.Figure(go.Treemap(
            labels=labels,
            values=values,
            parents=[""] * len(labels),
            textinfo="label+value+percent parent",
            hovertemplate='<b>%{label}</b><br>Valor: %{value}<br>Porcentaje: %{percentParent}<extra></extra>',
            marker=dict(
                colorscale='Blues',
                colorbar=dict(title="Cantidad")
            )
        ))
        
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center'
            },
            height=400,
            margin=dict(t=60, b=60, l=60, r=60)
        )
        
        return fig
    
    def create_waterfall_chart(self, categories, values, title="Waterfall Chart"):
        """Create waterfall chart for showing cumulative effects"""
        
        if len(categories) != len(values):
            return None
        
        # Calculate cumulative values
        cumulative = [0]
        for i, val in enumerate(values):
            cumulative.append(cumulative[-1] + val)
        
        fig = go.Figure(go.Waterfall(
            name="",
            orientation="v",
            measure=["relative"] * len(categories) + ["total"],
            x=categories + ["Total"],
            textposition="outside",
            text=[f"+{v}" if v > 0 else str(v) for v in values] + [str(cumulative[-1])],
            y=values + [cumulative[-1]],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            hovertemplate='<b>%{x}</b><br>Valor: %{y}<extra></extra>'
        ))
        
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center'
            },
            showlegend=False,
            height=400
        )
        
        return fig
    
    def create_animated_bar_race(self, df, date_column, category_column, value_column):
        """Create animated bar race chart"""
        
        if df.empty:
            return None
        
        # Prepare data for animation
        df_anim = df.copy()
        df_anim[date_column] = pd.to_datetime(df_anim[date_column])
        df_anim['period'] = df_anim[date_column].dt.to_period('M')
        
        # Group by period and category
        anim_data = df_anim.groupby(['period', category_column])[value_column].sum().reset_index()
        anim_data['period_str'] = anim_data['period'].astype(str)
        
        fig = px.bar(
            anim_data,
            x=value_column,
            y=category_column,
            animation_frame='period_str',
            orientation='h',
            title='Evolución Temporal por Categoría',
            labels={
                value_column: 'Cantidad',
                category_column: 'Categoría'
            }
        )
        
        fig.update_layout(
            height=500,
            xaxis_title="Cantidad",
            yaxis_title="Categoría"
        )
        
        return fig
    
    def create_correlation_heatmap(self, correlation_matrix, title="Matriz de Correlación"):
        """Create correlation heatmap"""
        
        if correlation_matrix.empty:
            return None
        
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.index,
            colorscale='RdBu',
            zmid=0,
            text=correlation_matrix.round(2).values,
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False,
            hovertemplate='<b>%{y} vs %{x}</b><br>Correlación: %{z:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center'
            },
            height=400,
            margin=dict(t=60, b=60, l=60, r=60)
        )
        
        return fig
    
    def create_box_plot(self, df, category_column, value_column, title="Box Plot"):
        """Create box plot for distribution analysis"""
        
        if df.empty:
            return None
        
        fig = px.box(
            df,
            x=category_column,
            y=value_column,
            title=title,
            color=category_column
        )
        
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>' +
                         'Q1: %{q1}<br>' +
                         'Mediana: %{median}<br>' +
                         'Q3: %{q3}<br>' +
                         'Min: %{lowerfence}<br>' +
                         'Max: %{upperfence}<br>' +
                         '<extra></extra>'
        )
        
        fig.update_layout(
            height=400,
            showlegend=False
        )
        
        return fig
    
    def create_3d_scatter(self, df, x_col, y_col, z_col, color_col=None, title="3D Scatter Plot"):
        """Create 3D scatter plot"""
        
        if df.empty:
            return None
        
        fig = px.scatter_3d(
            df,
            x=x_col,
            y=y_col,
            z=z_col,
            color=color_col,
            title=title,
            hover_data=df.columns
        )
        
        fig.update_layout(
            height=500,
            scene=dict(
                xaxis_title=x_col,
                yaxis_title=y_col,
                zaxis_title=z_col
            )
        )
        
        return fig
    
    def create_parallel_coordinates(self, df, dimensions, color_col=None, title="Parallel Coordinates"):
        """Create parallel coordinates plot"""
        
        if df.empty:
            return None
        
        fig = px.parallel_coordinates(
            df,
            dimensions=dimensions,
            color=color_col,
            title=title
        )
        
        fig.update_layout(height=400)
        
        return fig
    
    def create_sankey_diagram(self, source, target, value, labels, title="Sankey Diagram"):
        """Create Sankey diagram for flow visualization"""
        
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels,
                color="blue"
            ),
            link=dict(
                source=source,
                target=target,
                value=value,
                hovertemplate='%{source.label} → %{target.label}<br>Cantidad: %{value}<extra></extra>'
            )
        )])
        
        fig.update_layout(
            title_text=title,
            font_size=10,
            height=400
        )
        
        return fig