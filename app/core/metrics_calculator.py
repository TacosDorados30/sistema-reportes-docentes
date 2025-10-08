import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from collections import defaultdict
from sqlalchemy.orm import Session
from app.database.crud import FormularioCRUD

class MetricsCalculator:
    """Specialized class for calculating academic metrics and KPIs"""
    
    def __init__(self, db: Session):
        self.db = db
        self.crud = FormularioCRUD(db)
    
    def calcular_metricas_trimestrales(self, year: int, quarter: int) -> Dict[str, Any]:
        """Calcular métricas trimestrales"""
        try:
            # Obtener datos básicos
            stats = self.crud.get_estadisticas_generales()
            
            return {
                'año': year,
                'trimestre': quarter,
                'total_formularios': stats.get('total_formularios', 0),
                'aprobados': stats.get('aprobados', 0),
                'pendientes': stats.get('pendientes', 0),
                'rechazados': stats.get('rechazados', 0),
                'fecha_calculo': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'error': str(e),
                'año': year,
                'trimestre': quarter,
                'fecha_calculo': datetime.now().isoformat()
            }
    
    def calculate_quarterly_metrics(self, df: pd.DataFrame, quarter: int, year: int) -> Dict[str, Any]:
        """Calculate metrics for a specific quarter"""
        # Filter data for the specified quarter
        quarter_data = df[
            (df['year'] == year) & 
            (df['quarter'] == quarter) &
            (df['estado'] == 'APROBADO')
        ] if not df.empty else pd.DataFrame()
        
        # Get detailed data from database
        detailed_data = self.crud.get_datos_por_periodo(year, quarter)
        
        metrics = {
            'periodo': f"Q{quarter} {year}",
            'formularios_procesados': len(quarter_data),
            'resumen_actividades': self._calculate_activity_summary(detailed_data),
            'metricas_academicas': self._calculate_academic_metrics(detailed_data),
            'comparacion_anterior': self._compare_with_previous_quarter(quarter, year),
            'destacados': self._identify_highlights(detailed_data),
            'fecha_calculo': datetime.now().isoformat()
        }
        
        return metrics
    
    def calculate_annual_metrics(self, df: pd.DataFrame, year: int) -> Dict[str, Any]:
        """Calculate comprehensive annual metrics"""
        # Filter data for the specified year
        year_data = df[
            (df['year'] == year) & 
            (df['estado'] == 'APROBADO')
        ] if not df.empty else pd.DataFrame()
        
        # Get detailed data from database
        detailed_data = self.crud.get_datos_por_periodo(year)
        
        metrics = {
            'año': year,
            'formularios_procesados': len(year_data),
            'resumen_ejecutivo': self._generate_executive_summary(detailed_data),
            'metricas_por_trimestre': self._calculate_quarterly_breakdown(year),
            'logros_destacados': self._identify_annual_achievements(detailed_data),
            'areas_crecimiento': self._identify_growth_areas(detailed_data),
            'fecha_calculo': datetime.now().isoformat()
        }
        
        return metrics
    
    def compare_periods(self, current: Dict[str, Any], previous: Dict[str, Any]) -> Dict[str, Any]:
        """Compare metrics between two periods"""
        comparison = {
            'periodo_actual': current.get('periodo', 'N/A'),
            'periodo_anterior': previous.get('periodo', 'N/A'),
            'cambios_absolutos': {},
            'cambios_porcentuales': {},
            'tendencias': {},
            'interpretacion': {}
        }
        
        # Compare key metrics
        key_metrics = [
            'total_cursos', 'total_horas', 'total_publicaciones',
            'total_eventos', 'total_disenos', 'total_movilidades',
            'total_reconocimientos', 'total_certificaciones'
        ]
        
        for metric in key_metrics:
            current_val = self._extract_metric_value(current, metric)
            previous_val = self._extract_metric_value(previous, metric)
            
            if current_val is not None and previous_val is not None:
                absolute_change = current_val - previous_val
                percentage_change = (absolute_change / previous_val * 100) if previous_val != 0 else 0
                
                comparison['cambios_absolutos'][metric] = absolute_change
                comparison['cambios_porcentuales'][metric] = round(percentage_change, 2)
                comparison['tendencias'][metric] = self._classify_trend(percentage_change)
        
        # Generate interpretation
        comparison['interpretacion'] = self._interpret_comparison(comparison)
        
        return comparison
    
    def calculate_productivity_metrics(self, detailed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate productivity and efficiency metrics"""
        if not detailed_data:
            return {}
        
        cursos = detailed_data.get('cursos', {})
        publicaciones = detailed_data.get('publicaciones', {})
        eventos = detailed_data.get('eventos', {})
        
        total_docentes = detailed_data.get('formularios', 0)
        
        productivity = {
            'eficiencia_capacitacion': {
                'cursos_por_docente': cursos.get('total', 0) / max(total_docentes, 1),
                'horas_promedio_por_curso': cursos.get('total_horas', 0) / max(cursos.get('total', 1), 1),
                'horas_por_docente': cursos.get('total_horas', 0) / max(total_docentes, 1)
            },
            'productividad_investigacion': {
                'publicaciones_por_docente': publicaciones.get('total', 0) / max(total_docentes, 1),
                'tasa_aceptacion': self._calculate_acceptance_rate(publicaciones),
                'diversidad_publicaciones': len(publicaciones.get('por_estatus', {}))
            },
            'actividad_academica': {
                'eventos_por_docente': eventos.get('total', 0) / max(total_docentes, 1),
                'participacion_organizacion': self._calculate_organization_rate(eventos),
                'diversidad_participacion': len(eventos.get('por_tipo', {}))
            }
        }
        
        return productivity
    
    def generate_performance_indicators(self, detailed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate key performance indicators (KPIs)"""
        if not detailed_data:
            return {}
        
        kpis = {
            'indicadores_principales': {
                'indice_actividad_academica': self._calculate_academic_activity_index(detailed_data),
                'indice_productividad_investigacion': self._calculate_research_productivity_index(detailed_data),
                'indice_desarrollo_profesional': self._calculate_professional_development_index(detailed_data),
                'indice_impacto_institucional': self._calculate_institutional_impact_index(detailed_data)
            },
            'metas_cumplimiento': self._evaluate_goal_achievement(detailed_data),
            'areas_fortaleza': self._identify_strength_areas(detailed_data),
            'oportunidades_mejora': self._identify_improvement_opportunities(detailed_data),
            'recomendaciones': self._generate_recommendations(detailed_data)
        }
        
        return kpis
    
    def _calculate_activity_summary(self, detailed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate summary of all activities"""
        if not detailed_data:
            return {}
        
        return {
            'capacitacion': {
                'total_cursos': detailed_data.get('cursos', {}).get('total', 0),
                'total_horas': detailed_data.get('cursos', {}).get('total_horas', 0),
                'cursos_destacados': detailed_data.get('cursos', {}).get('nombres', [])[:5]
            },
            'investigacion': {
                'total_publicaciones': detailed_data.get('publicaciones', {}).get('total', 0),
                'por_estatus': detailed_data.get('publicaciones', {}).get('por_estatus', {}),
                'publicaciones_destacadas': detailed_data.get('publicaciones', {}).get('titulos', [])[:3]
            },
            'eventos_academicos': {
                'total_eventos': detailed_data.get('eventos', {}).get('total', 0),
                'por_tipo': detailed_data.get('eventos', {}).get('por_tipo', {}),
                'eventos_destacados': detailed_data.get('eventos', {}).get('nombres', [])[:5]
            },
            'desarrollo_curricular': {
                'total_disenos': detailed_data.get('disenos', {}).get('total', 0),
                'cursos_diseñados': detailed_data.get('disenos', {}).get('nombres', [])
            }
        }
    
    def _calculate_academic_metrics(self, detailed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate specific academic metrics"""
        if not detailed_data:
            return {}
        
        return {
            'impacto_capacitacion': self._calculate_training_impact(detailed_data.get('cursos', {})),
            'calidad_investigacion': self._calculate_research_quality(detailed_data.get('publicaciones', {})),
            'liderazgo_academico': self._calculate_academic_leadership(detailed_data.get('eventos', {})),
            'innovacion_curricular': self._calculate_curricular_innovation(detailed_data.get('disenos', {})),
            'movilidad_academica': self._calculate_academic_mobility(detailed_data.get('movilidades', {})),
            'reconocimiento_profesional': self._calculate_professional_recognition(detailed_data.get('reconocimientos', {}))
        }
    
    def _compare_with_previous_quarter(self, quarter: int, year: int) -> Dict[str, Any]:
        """Compare with previous quarter"""
        # Calculate previous quarter
        prev_quarter = quarter - 1 if quarter > 1 else 4
        prev_year = year if quarter > 1 else year - 1
        
        try:
            prev_data = self.crud.get_datos_por_periodo(prev_year, prev_quarter)
            current_data = self.crud.get_datos_por_periodo(year, quarter)
            
            return self._generate_period_comparison(current_data, prev_data, f"Q{prev_quarter} {prev_year}")
        except:
            return {"error": "No se pudieron obtener datos del período anterior"}
    
    def _identify_highlights(self, detailed_data: Dict[str, Any]) -> List[str]:
        """Identify key highlights from the data"""
        highlights = []
        
        if not detailed_data:
            return highlights
        
        # Check for significant achievements
        cursos = detailed_data.get('cursos', {})
        if cursos.get('total', 0) > 10:
            highlights.append(f"Se completaron {cursos['total']} cursos de capacitación")
        
        publicaciones = detailed_data.get('publicaciones', {})
        aceptadas = publicaciones.get('por_estatus', {}).get('ACEPTADO', 0)
        if aceptadas > 5:
            highlights.append(f"{aceptadas} publicaciones fueron aceptadas")
        
        eventos = detailed_data.get('eventos', {})
        organizados = eventos.get('por_tipo', {}).get('ORGANIZADOR', 0)
        if organizados > 3:
            highlights.append(f"Se organizaron {organizados} eventos académicos")
        
        movilidades = detailed_data.get('movilidades', {})
        internacionales = movilidades.get('por_tipo', {}).get('INTERNACIONAL', 0)
        if internacionales > 0:
            highlights.append(f"{internacionales} experiencias de movilidad internacional")
        
        return highlights
    
    def _generate_executive_summary(self, detailed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary for annual report"""
        if not detailed_data:
            return {}
        
        return {
            'logros_principales': self._identify_main_achievements(detailed_data),
            'numeros_clave': self._extract_key_numbers(detailed_data),
            'areas_impacto': self._identify_impact_areas(detailed_data),
            'crecimiento_anual': self._calculate_annual_growth(detailed_data)
        }
    
    def _calculate_quarterly_breakdown(self, year: int) -> Dict[str, Any]:
        """Calculate metrics breakdown by quarter"""
        quarterly_data = {}
        
        for quarter in range(1, 5):
            try:
                data = self.crud.get_datos_por_periodo(year, quarter)
                quarterly_data[f"Q{quarter}"] = {
                    'cursos': data.get('cursos', {}).get('total', 0),
                    'publicaciones': data.get('publicaciones', {}).get('total', 0),
                    'eventos': data.get('eventos', {}).get('total', 0),
                    'disenos': data.get('disenos', {}).get('total', 0)
                }
            except:
                quarterly_data[f"Q{quarter}"] = {
                    'cursos': 0, 'publicaciones': 0, 'eventos': 0, 'disenos': 0
                }
        
        return quarterly_data
    
    def _extract_metric_value(self, data: Dict[str, Any], metric: str) -> Optional[float]:
        """Extract metric value from nested data structure"""
        # Navigate through nested structure to find the metric
        if 'metricas_academicas' in data:
            for category in data['metricas_academicas'].values():
                if isinstance(category, dict) and metric in category:
                    return category[metric]
        
        if 'resumen_actividades' in data:
            for category in data['resumen_actividades'].values():
                if isinstance(category, dict):
                    if metric.replace('total_', '') in category:
                        return category[metric.replace('total_', '')]
        
        return None
    
    def _classify_trend(self, percentage_change: float) -> str:
        """Classify trend based on percentage change"""
        if percentage_change > 10:
            return "crecimiento_alto"
        elif percentage_change > 0:
            return "crecimiento_moderado"
        elif percentage_change > -10:
            return "estable"
        else:
            return "decrecimiento"
    
    def _interpret_comparison(self, comparison: Dict[str, Any]) -> Dict[str, str]:
        """Generate interpretation of comparison results"""
        interpretations = {}
        
        for metric, change in comparison['cambios_porcentuales'].items():
            if change > 20:
                interpretations[metric] = f"Crecimiento significativo del {change}%"
            elif change > 5:
                interpretations[metric] = f"Crecimiento moderado del {change}%"
            elif change > -5:
                interpretations[metric] = "Mantiene niveles similares"
            elif change > -20:
                interpretations[metric] = f"Disminución moderada del {abs(change)}%"
            else:
                interpretations[metric] = f"Disminución significativa del {abs(change)}%"
        
        return interpretations
    
    def _calculate_acceptance_rate(self, publicaciones: Dict[str, Any]) -> float:
        """Calculate publication acceptance rate"""
        por_estatus = publicaciones.get('por_estatus', {})
        aceptadas = por_estatus.get('ACEPTADO', 0) + por_estatus.get('PUBLICADO', 0)
        total = sum(por_estatus.values())
        
        return (aceptadas / max(total, 1)) * 100
    
    def _calculate_organization_rate(self, eventos: Dict[str, Any]) -> float:
        """Calculate event organization rate"""
        por_tipo = eventos.get('por_tipo', {})
        organizados = por_tipo.get('ORGANIZADOR', 0)
        total = sum(por_tipo.values())
        
        return (organizados / max(total, 1)) * 100
    
    def _calculate_academic_activity_index(self, detailed_data: Dict[str, Any]) -> float:
        """Calculate academic activity index (0-100)"""
        # Weighted combination of different activities
        weights = {
            'cursos': 0.2,
            'publicaciones': 0.3,
            'eventos': 0.2,
            'disenos': 0.15,
            'movilidades': 0.1,
            'reconocimientos': 0.05
        }
        
        scores = {}
        for activity, weight in weights.items():
            data = detailed_data.get(activity, {})
            total = data.get('total', 0)
            # Normalize to 0-100 scale (adjust thresholds as needed)
            normalized_score = min(total * 10, 100)  # Simple normalization
            scores[activity] = normalized_score * weight
        
        return sum(scores.values())
    
    def _calculate_research_productivity_index(self, detailed_data: Dict[str, Any]) -> float:
        """Calculate research productivity index"""
        publicaciones = detailed_data.get('publicaciones', {})
        total = publicaciones.get('total', 0)
        por_estatus = publicaciones.get('por_estatus', {})
        
        # Weight by publication status
        weighted_score = (
            por_estatus.get('PUBLICADO', 0) * 3 +
            por_estatus.get('ACEPTADO', 0) * 2 +
            por_estatus.get('EN_REVISION', 0) * 1
        )
        
        return min(weighted_score * 5, 100)  # Normalize to 0-100
    
    def _calculate_professional_development_index(self, detailed_data: Dict[str, Any]) -> float:
        """Calculate professional development index"""
        cursos = detailed_data.get('cursos', {})
        certificaciones = detailed_data.get('certificaciones', {})
        movilidades = detailed_data.get('movilidades', {})
        
        score = (
            cursos.get('total', 0) * 2 +
            certificaciones.get('vigentes', 0) * 3 +
            movilidades.get('total', 0) * 5
        )
        
        return min(score * 2, 100)  # Normalize to 0-100
    
    def _calculate_institutional_impact_index(self, detailed_data: Dict[str, Any]) -> float:
        """Calculate institutional impact index"""
        eventos = detailed_data.get('eventos', {})
        disenos = detailed_data.get('disenos', {})
        reconocimientos = detailed_data.get('reconocimientos', {})
        
        organizados = eventos.get('por_tipo', {}).get('ORGANIZADOR', 0)
        
        score = (
            organizados * 5 +
            disenos.get('total', 0) * 3 +
            reconocimientos.get('total', 0) * 4
        )
        
        return min(score * 3, 100)  # Normalize to 0-100
    
    def _evaluate_goal_achievement(self, detailed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate achievement against typical academic goals"""
        # Define typical goals (these could be configurable)
        goals = {
            'cursos_anuales': 12,
            'publicaciones_anuales': 3,
            'eventos_organizados': 2,
            'horas_capacitacion': 40
        }
        
        achievement = {}
        cursos = detailed_data.get('cursos', {})
        publicaciones = detailed_data.get('publicaciones', {})
        eventos = detailed_data.get('eventos', {})
        
        achievement['cursos'] = {
            'objetivo': goals['cursos_anuales'],
            'actual': cursos.get('total', 0),
            'porcentaje': (cursos.get('total', 0) / goals['cursos_anuales']) * 100
        }
        
        achievement['publicaciones'] = {
            'objetivo': goals['publicaciones_anuales'],
            'actual': publicaciones.get('total', 0),
            'porcentaje': (publicaciones.get('total', 0) / goals['publicaciones_anuales']) * 100
        }
        
        return achievement
    
    def _identify_strength_areas(self, detailed_data: Dict[str, Any]) -> List[str]:
        """Identify areas of strength"""
        strengths = []
        
        # Analyze each area and identify strengths
        cursos = detailed_data.get('cursos', {})
        if cursos.get('total', 0) > 15:
            strengths.append("Capacitación y desarrollo profesional")
        
        publicaciones = detailed_data.get('publicaciones', {})
        if publicaciones.get('total', 0) > 5:
            strengths.append("Productividad en investigación")
        
        eventos = detailed_data.get('eventos', {})
        organizados = eventos.get('por_tipo', {}).get('ORGANIZADOR', 0)
        if organizados > 2:
            strengths.append("Liderazgo en eventos académicos")
        
        return strengths
    
    def _identify_improvement_opportunities(self, detailed_data: Dict[str, Any]) -> List[str]:
        """Identify areas for improvement"""
        opportunities = []
        
        movilidades = detailed_data.get('movilidades', {})
        if movilidades.get('total', 0) < 2:
            opportunities.append("Incrementar experiencias de movilidad académica")
        
        certificaciones = detailed_data.get('certificaciones', {})
        if certificaciones.get('vigentes', 0) < 3:
            opportunities.append("Obtener más certificaciones profesionales")
        
        publicaciones = detailed_data.get('publicaciones', {})
        if publicaciones.get('total', 0) < 3:
            opportunities.append("Aumentar productividad en publicaciones")
        
        return opportunities
    
    def _generate_recommendations(self, detailed_data: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Based on the data analysis, generate specific recommendations
        cursos = detailed_data.get('cursos', {})
        if cursos.get('total_horas', 0) < 40:
            recommendations.append("Considerar participar en cursos de mayor duración para alcanzar 40 horas anuales")
        
        publicaciones = detailed_data.get('publicaciones', {})
        en_revision = publicaciones.get('por_estatus', {}).get('EN_REVISION', 0)
        if en_revision > 0:
            recommendations.append(f"Dar seguimiento a las {en_revision} publicaciones en revisión")
        
        eventos = detailed_data.get('eventos', {})
        if eventos.get('total', 0) < 5:
            recommendations.append("Incrementar participación en eventos académicos")
        
        return recommendations
    
    # Additional helper methods for complex calculations
    def _calculate_training_impact(self, cursos: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate training impact metrics"""
        return {
            'total_horas': cursos.get('total_horas', 0),
            'promedio_horas_por_curso': cursos.get('total_horas', 0) / max(cursos.get('total', 1), 1),
            'diversidad_temas': len(set(cursos.get('nombres', [])))
        }
    
    def _calculate_research_quality(self, publicaciones: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate research quality metrics"""
        por_estatus = publicaciones.get('por_estatus', {})
        total = sum(por_estatus.values())
        
        return {
            'tasa_aceptacion': (por_estatus.get('ACEPTADO', 0) + por_estatus.get('PUBLICADO', 0)) / max(total, 1) * 100,
            'productividad': total,
            'diversidad_venues': len(set(publicaciones.get('titulos', [])))
        }
    
    def _calculate_academic_leadership(self, eventos: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate academic leadership metrics"""
        por_tipo = eventos.get('por_tipo', {})
        total = sum(por_tipo.values())
        
        return {
            'eventos_organizados': por_tipo.get('ORGANIZADOR', 0),
            'tasa_liderazgo': por_tipo.get('ORGANIZADOR', 0) / max(total, 1) * 100,
            'participacion_total': total
        }
    
    def _calculate_curricular_innovation(self, disenos: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate curricular innovation metrics"""
        return {
            'cursos_diseñados': disenos.get('total', 0),
            'diversidad_cursos': len(set(disenos.get('nombres', [])))
        }
    
    def _calculate_academic_mobility(self, movilidades: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate academic mobility metrics"""
        por_tipo = movilidades.get('por_tipo', {})
        
        return {
            'total_experiencias': movilidades.get('total', 0),
            'internacionales': por_tipo.get('INTERNACIONAL', 0),
            'nacionales': por_tipo.get('NACIONAL', 0),
            'tasa_internacional': por_tipo.get('INTERNACIONAL', 0) / max(movilidades.get('total', 1), 1) * 100
        }
    
    def _calculate_professional_recognition(self, reconocimientos: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate professional recognition metrics"""
        por_tipo = reconocimientos.get('por_tipo', {})
        
        return {
            'total_reconocimientos': reconocimientos.get('total', 0),
            'premios': por_tipo.get('PREMIO', 0),
            'distinciones': por_tipo.get('DISTINCION', 0),
            'grados': por_tipo.get('GRADO', 0)
        }
    
    def _identify_main_achievements(self, detailed_data: Dict[str, Any]) -> List[str]:
        """Identify main achievements for executive summary"""
        achievements = []
        
        # Analyze data and identify significant achievements
        for category, data in detailed_data.items():
            if isinstance(data, dict) and data.get('total', 0) > 0:
                total = data['total']
                if category == 'cursos' and total > 20:
                    achievements.append(f"Completó {total} cursos de capacitación")
                elif category == 'publicaciones' and total > 5:
                    achievements.append(f"Produjo {total} publicaciones académicas")
                elif category == 'eventos' and total > 8:
                    achievements.append(f"Participó en {total} eventos académicos")
        
        return achievements[:5]  # Top 5 achievements
    
    def _extract_key_numbers(self, detailed_data: Dict[str, Any]) -> Dict[str, int]:
        """Extract key numbers for summary"""
        return {
            'total_cursos': detailed_data.get('cursos', {}).get('total', 0),
            'total_horas': detailed_data.get('cursos', {}).get('total_horas', 0),
            'total_publicaciones': detailed_data.get('publicaciones', {}).get('total', 0),
            'total_eventos': detailed_data.get('eventos', {}).get('total', 0),
            'total_disenos': detailed_data.get('disenos', {}).get('total', 0)
        }
    
    def _identify_impact_areas(self, detailed_data: Dict[str, Any]) -> List[str]:
        """Identify areas of impact"""
        impact_areas = []
        
        # Determine impact based on activity levels
        if detailed_data.get('cursos', {}).get('total', 0) > 10:
            impact_areas.append("Desarrollo profesional continuo")
        
        if detailed_data.get('publicaciones', {}).get('total', 0) > 3:
            impact_areas.append("Contribución a la investigación")
        
        if detailed_data.get('eventos', {}).get('por_tipo', {}).get('ORGANIZADOR', 0) > 1:
            impact_areas.append("Liderazgo académico")
        
        if detailed_data.get('disenos', {}).get('total', 0) > 2:
            impact_areas.append("Innovación curricular")
        
        return impact_areas
    
    def _calculate_annual_growth(self, detailed_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate annual growth rates"""
        # This would require historical data comparison
        # For now, return placeholder structure
        return {
            'cursos': 0.0,
            'publicaciones': 0.0,
            'eventos': 0.0,
            'disenos': 0.0
        }
    
    def _generate_period_comparison(self, current: Dict, previous: Dict, prev_period: str) -> Dict[str, Any]:
        """Generate comparison between two periods"""
        comparison = {
            'periodo_anterior': prev_period,
            'cambios': {},
            'tendencia_general': 'estable'
        }
        
        # Compare key metrics
        for key in ['cursos', 'publicaciones', 'eventos', 'disenos']:
            current_val = current.get(key, {}).get('total', 0)
            previous_val = previous.get(key, {}).get('total', 0)
            
            if previous_val > 0:
                change = ((current_val - previous_val) / previous_val) * 100
                comparison['cambios'][key] = round(change, 2)
        
        return comparison 
    def _identify_annual_achievements(self, detailed_data: Dict[str, Any]) -> List[str]:
        """Identify annual achievements"""
        return self._identify_main_achievements(detailed_data)
    
    def _identify_growth_areas(self, detailed_data: Dict[str, Any]) -> List[str]:
        """Identify growth areas"""
        return self._identify_improvement_opportunities(detailed_data)