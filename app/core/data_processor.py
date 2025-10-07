import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date
from difflib import SequenceMatcher
from collections import Counter
import re
from sqlalchemy.orm import Session
from app.database.crud import FormularioCRUD
from app.models.database import EstadoFormularioEnum

class DataProcessor:
    """Main data processing engine for cleaning and normalizing form data"""
    
    def __init__(self, db: Session):
        self.db = db
        self.crud = FormularioCRUD(db)
    
    def clean_data(self, raw_data: List[Dict]) -> pd.DataFrame:
        """Clean and normalize raw form data"""
        if not raw_data:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(raw_data)
        
        # Clean text fields
        text_columns = ['nombre_completo', 'correo_institucional']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].apply(self._clean_text)
        
        # Normalize dates
        date_columns = ['fecha_envio', 'fecha_revision']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Normalize email addresses
        if 'correo_institucional' in df.columns:
            df['correo_institucional'] = df['correo_institucional'].apply(self._normalize_email)
        
        # Add derived columns
        df['year'] = df['fecha_envio'].dt.year if 'fecha_envio' in df.columns else None
        df['quarter'] = df['fecha_envio'].dt.quarter if 'fecha_envio' in df.columns else None
        df['month'] = df['fecha_envio'].dt.month if 'fecha_envio' in df.columns else None
        
        return df
    
    def detect_duplicates(self, df: pd.DataFrame, threshold: float = 0.8) -> pd.DataFrame:
        """Detect potential duplicate entries using fuzzy matching"""
        if df.empty or 'nombre_completo' not in df.columns:
            return df
        
        df = df.copy()
        df['is_duplicate'] = False
        df['duplicate_group'] = None
        
        names = df['nombre_completo'].tolist()
        emails = df['correo_institucional'].tolist() if 'correo_institucional' in df.columns else [None] * len(names)
        
        duplicate_groups = []
        processed_indices = set()
        
        for i, (name1, email1) in enumerate(zip(names, emails)):
            if i in processed_indices:
                continue
                
            current_group = [i]
            
            for j, (name2, email2) in enumerate(zip(names, emails)):
                if j <= i or j in processed_indices:
                    continue
                
                # Check name similarity
                name_similarity = self._calculate_similarity(name1, name2)
                
                # Check email similarity (if both exist)
                email_similarity = 0
                if email1 and email2:
                    email_similarity = self._calculate_similarity(email1, email2)
                
                # Consider duplicate if high name similarity or exact email match
                if name_similarity >= threshold or (email1 and email2 and email1.lower() == email2.lower()):
                    current_group.append(j)
                    processed_indices.add(j)
            
            if len(current_group) > 1:
                duplicate_groups.append(current_group)
                for idx in current_group:
                    df.loc[idx, 'is_duplicate'] = True
                    df.loc[idx, 'duplicate_group'] = len(duplicate_groups) - 1
            
            processed_indices.add(i)
        
        return df
    
    def calculate_metrics(self, df: pd.DataFrame, period: str = 'all') -> Dict[str, Any]:
        """Calculate comprehensive metrics from processed data"""
        if df.empty:
            return self._empty_metrics()
        
        # Filter by period if specified
        if period != 'all' and 'fecha_envio' in df.columns:
            df = self._filter_by_period(df, period)
        
        # Only include approved forms for metrics
        if 'estado' in df.columns:
            df = df[df['estado'] == 'APROBADO']
        
        metrics = {
            'total_formularios': len(df),
            'periodo': period,
            'fecha_calculo': datetime.now().isoformat(),
            'formularios_por_mes': self._calculate_monthly_distribution(df),
            'duplicados_detectados': len(df[df.get('is_duplicate', False)]) if 'is_duplicate' in df.columns else 0,
            'metricas_detalladas': self._calculate_detailed_metrics(df)
        }
        
        return metrics
    
    def generate_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive statistics for reporting"""
        if df.empty:
            return {}
        
        stats = {
            'resumen_general': self._generate_general_summary(df),
            'distribucion_temporal': self._generate_temporal_distribution(df),
            'analisis_contenido': self._generate_content_analysis(df),
            'tendencias': self._generate_trends(df),
            'calidad_datos': self._generate_data_quality_stats(df)
        }
        
        return stats
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text fields"""
        if pd.isna(text) or not isinstance(text, str):
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Normalize common abbreviations
        text = re.sub(r'\bDr\.\s*', 'Dr. ', text, flags=re.IGNORECASE)
        text = re.sub(r'\bDra\.\s*', 'Dra. ', text, flags=re.IGNORECASE)
        text = re.sub(r'\bMtro\.\s*', 'Mtro. ', text, flags=re.IGNORECASE)
        text = re.sub(r'\bMtra\.\s*', 'Mtra. ', text, flags=re.IGNORECASE)
        
        return text
    
    def _normalize_email(self, email: str) -> str:
        """Normalize email addresses"""
        if pd.isna(email) or not isinstance(email, str):
            return ""
        
        email = email.lower().strip()
        
        # Remove common typos
        email = re.sub(r'\.{2,}', '.', email)  # Multiple dots
        email = re.sub(r'@{2,}', '@', email)  # Multiple @
        
        return email
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        if not str1 or not str2:
            return 0.0
        
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def _filter_by_period(self, df: pd.DataFrame, period: str) -> pd.DataFrame:
        """Filter DataFrame by time period"""
        if 'fecha_envio' not in df.columns:
            return df
        
        current_year = datetime.now().year
        current_quarter = (datetime.now().month - 1) // 3 + 1
        
        if period == 'current_year':
            return df[df['year'] == current_year]
        elif period == 'current_quarter':
            return df[(df['year'] == current_year) & (df['quarter'] == current_quarter)]
        elif period == 'last_year':
            return df[df['year'] == current_year - 1]
        elif period.startswith('year_'):
            year = int(period.split('_')[1])
            return df[df['year'] == year]
        elif period.startswith('quarter_'):
            parts = period.split('_')
            year, quarter = int(parts[1]), int(parts[2])
            return df[(df['year'] == year) & (df['quarter'] == quarter)]
        
        return df
    
    def _calculate_monthly_distribution(self, df: pd.DataFrame) -> Dict[str, int]:
        """Calculate monthly distribution of forms"""
        if 'month' not in df.columns:
            return {}
        
        monthly_counts = df['month'].value_counts().to_dict()
        
        # Convert month numbers to names
        month_names = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }
        
        return {month_names.get(month, f'Mes {month}'): count 
                for month, count in monthly_counts.items()}
    
    def _calculate_detailed_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate detailed metrics from approved forms"""
        # Get detailed data from database for approved forms
        approved_data = self.crud.get_datos_por_periodo(datetime.now().year)
        
        return {
            'cursos': approved_data.get('cursos', {}),
            'publicaciones': approved_data.get('publicaciones', {}),
            'eventos': approved_data.get('eventos', {}),
            'disenos': approved_data.get('disenos', {}),
            'movilidades': approved_data.get('movilidades', {}),
            'reconocimientos': approved_data.get('reconocimientos', {}),
            'certificaciones': approved_data.get('certificaciones', {})
        }
    
    def _generate_general_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate general summary statistics"""
        return {
            'total_registros': len(df),
            'periodo_inicio': df['fecha_envio'].min().isoformat() if 'fecha_envio' in df.columns and not df.empty else None,
            'periodo_fin': df['fecha_envio'].max().isoformat() if 'fecha_envio' in df.columns and not df.empty else None,
            'estados_distribucion': df['estado'].value_counts().to_dict() if 'estado' in df.columns else {},
            'promedio_mensual': len(df) / 12 if len(df) > 0 else 0
        }
    
    def _generate_temporal_distribution(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate temporal distribution analysis"""
        if 'fecha_envio' not in df.columns or df.empty:
            return {}
        
        return {
            'por_año': df['year'].value_counts().to_dict() if 'year' in df.columns else {},
            'por_trimestre': df['quarter'].value_counts().to_dict() if 'quarter' in df.columns else {},
            'por_mes': self._calculate_monthly_distribution(df),
            'tendencia_mensual': self._calculate_monthly_trend(df)
        }
    
    def _generate_content_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate content analysis from form data"""
        # This would analyze the actual content of forms
        # For now, return basic analysis
        return {
            'dominios_email_mas_comunes': self._analyze_email_domains(df),
            'longitud_promedio_nombres': df['nombre_completo'].str.len().mean() if 'nombre_completo' in df.columns else 0,
            'patrones_nombres': self._analyze_name_patterns(df)
        }
    
    def _generate_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate trend analysis"""
        if df.empty or 'fecha_envio' not in df.columns:
            return {}
        
        # Calculate growth trends
        monthly_counts = df.groupby([df['fecha_envio'].dt.year, df['fecha_envio'].dt.month]).size()
        
        return {
            'crecimiento_mensual': self._calculate_growth_rate(monthly_counts),
            'estacionalidad': self._detect_seasonality(df),
            'proyeccion_anual': self._project_annual_volume(df)
        }
    
    def _generate_data_quality_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate data quality statistics"""
        if df.empty:
            return {}
        
        quality_stats = {}
        
        for column in df.columns:
            if column in ['nombre_completo', 'correo_institucional']:
                null_count = df[column].isnull().sum()
                empty_count = (df[column] == '').sum() if df[column].dtype == 'object' else 0
                
                quality_stats[column] = {
                    'completitud': (len(df) - null_count - empty_count) / len(df) * 100,
                    'valores_nulos': null_count,
                    'valores_vacios': empty_count
                }
        
        return quality_stats
    
    def _calculate_monthly_trend(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Calculate monthly trend data"""
        if 'fecha_envio' not in df.columns:
            return []
        
        monthly_data = df.groupby([df['fecha_envio'].dt.year, df['fecha_envio'].dt.month]).size().reset_index()
        monthly_data.columns = ['year', 'month', 'count']
        
        trend_data = []
        for _, row in monthly_data.iterrows():
            trend_data.append({
                'periodo': f"{row['year']}-{row['month']:02d}",
                'cantidad': row['count']
            })
        
        return sorted(trend_data, key=lambda x: x['periodo'])
    
    def _analyze_email_domains(self, df: pd.DataFrame) -> Dict[str, int]:
        """Analyze email domains"""
        if 'correo_institucional' not in df.columns:
            return {}
        
        domains = df['correo_institucional'].str.extract(r'@(.+)$')[0].dropna()
        return domains.value_counts().head(10).to_dict()
    
    def _analyze_name_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze name patterns"""
        if 'nombre_completo' not in df.columns:
            return {}
        
        names = df['nombre_completo'].dropna()
        
        return {
            'con_titulo': names.str.contains(r'^(Dr\.|Dra\.|Mtro\.|Mtra\.)', case=False).sum(),
            'palabras_promedio': names.str.split().str.len().mean(),
            'nombres_mas_largos': names.str.len().nlargest(5).index.tolist()
        }
    
    def _calculate_growth_rate(self, monthly_counts: pd.Series) -> float:
        """Calculate monthly growth rate"""
        if len(monthly_counts) < 2:
            return 0.0
        
        # Simple growth rate calculation
        recent_avg = monthly_counts.tail(3).mean()
        previous_avg = monthly_counts.head(3).mean() if len(monthly_counts) >= 6 else monthly_counts.head().mean()
        
        if previous_avg == 0:
            return 0.0
        
        return ((recent_avg - previous_avg) / previous_avg) * 100
    
    def _detect_seasonality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect seasonal patterns"""
        if 'month' not in df.columns:
            return {}
        
        monthly_avg = df.groupby('month').size().mean()
        monthly_counts = df['month'].value_counts()
        
        seasonal_months = {}
        for month, count in monthly_counts.items():
            if count > monthly_avg * 1.2:
                seasonal_months[month] = 'alto'
            elif count < monthly_avg * 0.8:
                seasonal_months[month] = 'bajo'
        
        return seasonal_months
    
    def _project_annual_volume(self, df: pd.DataFrame) -> int:
        """Project annual volume based on current trends"""
        if df.empty or 'fecha_envio' not in df.columns:
            return 0
        
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        current_year_data = df[df['year'] == current_year]
        
        if len(current_year_data) == 0:
            return 0
        
        monthly_avg = len(current_year_data) / current_month
        return int(monthly_avg * 12)
    
    def _empty_metrics(self) -> Dict[str, Any]:
        """Return empty metrics structure"""
        return {
            'total_formularios': 0,
            'periodo': 'all',
            'fecha_calculo': datetime.now().isoformat(),
            'formularios_por_mes': {},
            'duplicados_detectados': 0,
            'metricas_detalladas': {}
        }