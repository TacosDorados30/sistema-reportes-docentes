import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

class InteractiveFilters:
    """Class for creating interactive filters and controls"""
    
    def __init__(self):
        self.filter_state = {}
    
    def date_range_filter(self, 
                         key: str = "date_range",
                         label: str = "Rango de fechas:",
                         min_date: Optional[datetime] = None,
                         max_date: Optional[datetime] = None,
                         default_days_back: int = 30) -> Tuple[datetime, datetime]:
        """Create date range filter"""
        
        if min_date is None:
            min_date = datetime.now() - timedelta(days=365)
        if max_date is None:
            max_date = datetime.now()
        
        default_start = max_date - timedelta(days=default_days_back)
        
        date_range = st.date_input(
            label,
            value=(default_start.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date(),
            key=key
        )
        
        if len(date_range) == 2:
            return datetime.combine(date_range[0], datetime.min.time()), \
                   datetime.combine(date_range[1], datetime.max.time())
        else:
            return default_start, max_date
    
    def status_filter(self, 
                     key: str = "status_filter",
                     label: str = "Filtrar por estado:",
                     options: List[str] = None) -> List[str]:
        """Create status filter"""
        
        if options is None:
            options = ["TODOS", "PENDIENTE", "APROBADO", "RECHAZADO"]
        
        selected = st.multiselect(
            label,
            options=options,
            default=["TODOS"] if "TODOS" in options else options,
            key=key
        )
        
        if "TODOS" in selected:
            return [opt for opt in options if opt != "TODOS"]
        
        return selected
    
    def numeric_range_filter(self,
                           key: str,
                           label: str,
                           min_value: float = 0.0,
                           max_value: float = 100.0,
                           step: float = 1.0,
                           default_range: Optional[Tuple[float, float]] = None) -> Tuple[float, float]:
        """Create numeric range filter"""
        
        if default_range is None:
            default_range = (min_value, max_value)
        
        range_values = st.slider(
            label,
            min_value=min_value,
            max_value=max_value,
            value=default_range,
            step=step,
            key=key
        )
        
        return range_values
    
    def category_filter(self,
                       key: str,
                       label: str,
                       options: List[str],
                       default_all: bool = True) -> List[str]:
        """Create category filter"""
        
        default_selection = options if default_all else []
        
        selected = st.multiselect(
            label,
            options=options,
            default=default_selection,
            key=key
        )
        
        return selected if selected else options
    
    def search_filter(self,
                     key: str = "search",
                     label: str = "Buscar:",
                     placeholder: str = "Ingrese términos de búsqueda...") -> str:
        """Create search filter"""
        
        search_term = st.text_input(
            label,
            placeholder=placeholder,
            key=key
        )
        
        return search_term.strip().lower()
    
    def sort_filter(self,
                   key: str = "sort",
                   label: str = "Ordenar por:",
                   options: Dict[str, str] = None,
                   ascending: bool = True) -> Tuple[str, bool]:
        """Create sort filter"""
        
        if options is None:
            options = {
                "fecha_envio": "Fecha de envío",
                "nombre_completo": "Nombre",
                "total_items": "Total de items"
            }
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            sort_by = st.selectbox(
                label,
                options=list(options.keys()),
                format_func=lambda x: options[x],
                key=key
            )
        
        with col2:
            sort_order = st.selectbox(
                "Orden:",
                options=["Ascendente", "Descendente"],
                index=0 if ascending else 1,
                key=f"{key}_order"
            )
        
        return sort_by, sort_order == "Ascendente"
    
    def pagination_filter(self,
                         total_items: int,
                         key: str = "pagination",
                         items_per_page: int = 20) -> Tuple[int, int]:
        """Create pagination filter"""
        
        if total_items <= items_per_page:
            return 0, total_items
        
        total_pages = (total_items - 1) // items_per_page + 1
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            current_page = st.number_input(
                f"Página (1-{total_pages}):",
                min_value=1,
                max_value=total_pages,
                value=1,
                key=key
            )
        
        start_idx = (current_page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        
        st.write(f"Mostrando {start_idx + 1}-{end_idx} de {total_items} elementos")
        
        return start_idx, end_idx
    
    def advanced_filters_expander(self,
                                 df: pd.DataFrame,
                                 key_prefix: str = "advanced") -> Dict[str, Any]:
        """Create advanced filters in an expander"""
        
        filters = {}
        
        with st.expander("🔧 Filtros Avanzados"):
            
            # Numeric columns for range filters
            numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
            
            if len(numeric_columns) > 0:
                st.subheader("Filtros Numéricos")
                
                for col in numeric_columns:
                    if col in ['id']:  # Skip ID columns
                        continue
                    
                    min_val = float(df[col].min())
                    max_val = float(df[col].max())
                    
                    if min_val != max_val:  # Only show if there's variation
                        range_filter = self.numeric_range_filter(
                            key=f"{key_prefix}_{col}",
                            label=f"{col.replace('_', ' ').title()}:",
                            min_value=min_val,
                            max_value=max_val,
                            default_range=(min_val, max_val)
                        )
                        filters[col] = range_filter
            
            # Categorical columns for category filters
            categorical_columns = df.select_dtypes(include=['object']).columns
            
            if len(categorical_columns) > 0:
                st.subheader("Filtros Categóricos")
                
                for col in categorical_columns:
                    if col in ['id', 'nombre_completo', 'correo_institucional']:
                        continue
                    
                    unique_values = df[col].dropna().unique().tolist()
                    
                    if len(unique_values) > 1 and len(unique_values) <= 20:  # Reasonable number of categories
                        category_filter = self.category_filter(
                            key=f"{key_prefix}_{col}",
                            label=f"{col.replace('_', ' ').title()}:",
                            options=unique_values
                        )
                        filters[col] = category_filter
            
            # Text search
            search_term = self.search_filter(
                key=f"{key_prefix}_search",
                label="Búsqueda en texto:"
            )
            if search_term:
                filters['search'] = search_term
        
        return filters
    
    def apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters to DataFrame"""
        
        filtered_df = df.copy()
        
        for filter_name, filter_value in filters.items():
            
            if filter_name == 'search' and filter_value:
                # Apply text search across string columns
                text_columns = filtered_df.select_dtypes(include=['object']).columns
                search_mask = pd.Series([False] * len(filtered_df))
                
                for col in text_columns:
                    search_mask |= filtered_df[col].astype(str).str.lower().str.contains(
                        filter_value, na=False, regex=False
                    )
                
                filtered_df = filtered_df[search_mask]
            
            elif filter_name in filtered_df.columns:
                if isinstance(filter_value, tuple) and len(filter_value) == 2:
                    # Numeric range filter
                    min_val, max_val = filter_value
                    filtered_df = filtered_df[
                        (filtered_df[filter_name] >= min_val) & 
                        (filtered_df[filter_name] <= max_val)
                    ]
                
                elif isinstance(filter_value, list):
                    # Category filter
                    filtered_df = filtered_df[filtered_df[filter_name].isin(filter_value)]
        
        return filtered_df
    
    def create_filter_summary(self, filters: Dict[str, Any]) -> str:
        """Create a summary of applied filters"""
        
        if not filters:
            return "Sin filtros aplicados"
        
        summary_parts = []
        
        for filter_name, filter_value in filters.items():
            if filter_name == 'search' and filter_value:
                summary_parts.append(f"Búsqueda: '{filter_value}'")
            
            elif isinstance(filter_value, tuple) and len(filter_value) == 2:
                min_val, max_val = filter_value
                summary_parts.append(f"{filter_name}: {min_val}-{max_val}")
            
            elif isinstance(filter_value, list) and filter_value:
                if len(filter_value) <= 3:
                    summary_parts.append(f"{filter_name}: {', '.join(map(str, filter_value))}")
                else:
                    summary_parts.append(f"{filter_name}: {len(filter_value)} elementos")
        
        return " | ".join(summary_parts) if summary_parts else "Sin filtros aplicados"
    
    def reset_filters_button(self, key: str = "reset_filters") -> bool:
        """Create reset filters button"""
        
        return st.button("🔄 Resetear Filtros", key=key)
    
    def export_filtered_data_button(self, 
                                   df: pd.DataFrame,
                                   filename: str = "filtered_data",
                                   key: str = "export_filtered") -> None:
        """Create export button for filtered data"""
        
        if df.empty:
            st.warning("No hay datos para exportar")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV export
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name=f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key=f"{key}_csv"
            )
        
        with col2:
            # JSON export
            json_data = df.to_json(orient='records', indent=2)
            st.download_button(
                label="📥 Descargar JSON",
                data=json_data,
                file_name=f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                key=f"{key}_json"
            )
    
    def create_comparison_filter(self,
                               key: str = "comparison",
                               label: str = "Comparar períodos:") -> Dict[str, Any]:
        """Create comparison filter for time periods"""
        
        comparison_enabled = st.checkbox("Habilitar comparación", key=f"{key}_enabled")
        
        if not comparison_enabled:
            return {"enabled": False}
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Período Actual:**")
            current_start = st.date_input("Desde:", key=f"{key}_current_start")
            current_end = st.date_input("Hasta:", key=f"{key}_current_end")
        
        with col2:
            st.write("**Período de Comparación:**")
            comparison_start = st.date_input("Desde:", key=f"{key}_comparison_start")
            comparison_end = st.date_input("Hasta:", key=f"{key}_comparison_end")
        
        return {
            "enabled": True,
            "current": (current_start, current_end),
            "comparison": (comparison_start, comparison_end)
        }