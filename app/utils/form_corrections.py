"""
Sistema de correcciones que mantiene el ID original
Actualiza el formulario existente y guarda historial de versiones
"""

import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.database.connection import SessionLocal
from app.database.crud import FormularioCRUD
from app.models.database import FormularioEnvioDB
from app.models.form_history import FormularioHistoryDB
from app.utils.correction_tokens import CorrectionTokenManager
from sqlalchemy import text


class FormCorrectionManager:
    """Gestiona correcciones manteniendo el ID original"""
    
    def __init__(self):
        self.token_manager = CorrectionTokenManager()
    
    def create_correction_link(self, formulario_id: int, base_url: str = "http://localhost:8502") -> Optional[str]:
        """
        Crea un link de corrección para un formulario
        
        Args:
            formulario_id: ID del formulario a corregir
            base_url: URL base del sistema
            
        Returns:
            URL completa para corrección o None si hay error
        """
        token = self.token_manager.create_correction_token(formulario_id)
        
        if not token:
            return None
        
        return f"{base_url}/formulario?token={token}&mode=correction"
    
    def apply_correction(self, formulario_id: int, new_data: Dict[str, Any], corrected_by: str = "docente") -> bool:
        """
        Aplica una corrección manteniendo el ID original
        
        Args:
            formulario_id: ID del formulario a corregir
            new_data: Nuevos datos del formulario
            corrected_by: Quién hizo la corrección
            
        Returns:
            True si la corrección se aplicó correctamente
        """
        db = SessionLocal()
        try:
            crud = FormularioCRUD(db)
            
            # Obtener formulario actual
            current_form = crud.get_formulario(formulario_id)
            if not current_form:
                return False
            
            # Guardar versión actual en historial
            self._save_to_history(db, current_form, corrected_by)
            
            # Actualizar formulario con nuevos datos
            success = self._update_form_data(db, formulario_id, new_data)
            
            if success:
                db.commit()
                return True
            else:
                db.rollback()
                return False
                
        except Exception as e:
            print(f"Error aplicando corrección: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def get_form_history(self, formulario_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de versiones de un formulario
        
        Args:
            formulario_id: ID del formulario
            
        Returns:
            Lista de versiones históricas
        """
        db = SessionLocal()
        try:
            history = db.query(FormularioHistoryDB).filter(
                FormularioHistoryDB.formulario_id == formulario_id
            ).order_by(FormularioHistoryDB.version_numero.desc()).all()
            
            history_list = []
            for h in history:
                history_list.append({
                    'version': h.version_numero,
                    'fecha': h.fecha_creacion,
                    'modificado_por': h.modificado_por,
                    'motivo': h.motivo_cambio,
                    'estado': h.estado.value,
                    'datos': {
                        'nombre_completo': h.nombre_completo,
                        'correo_institucional': h.correo_institucional,
                        'año_academico': h.año_academico,
                        'trimestre': h.trimestre,
                        'actividades': h.actividades_json or {}
                    }
                })
            
            return history_list
            
        except Exception as e:
            print(f"Error obteniendo historial: {e}")
            return []
        finally:
            db.close()
    
    def compare_with_history(self, formulario_id: int, version_numero: int) -> Dict[str, Any]:
        """
        Compara la versión actual con una versión del historial
        
        Args:
            formulario_id: ID del formulario
            version_numero: Número de versión a comparar
            
        Returns:
            Diccionario con las diferencias
        """
        db = SessionLocal()
        try:
            # Obtener versión actual
            crud = FormularioCRUD(db)
            current_form = crud.get_formulario(formulario_id)
            
            # Obtener versión histórica
            history_version = db.query(FormularioHistoryDB).filter(
                FormularioHistoryDB.formulario_id == formulario_id,
                FormularioHistoryDB.version_numero == version_numero
            ).first()
            
            if not current_form or not history_version:
                return {}
            
            differences = {
                'datos_personales': {},
                'actividades': {},
                'metadata': {
                    'version_actual': 'Actual',
                    'version_comparada': version_numero,
                    'fecha_version': history_version.fecha_creacion
                }
            }
            
            # Comparar datos personales
            personal_fields = ['nombre_completo', 'correo_institucional', 'año_academico', 'trimestre']
            for field in personal_fields:
                current_val = getattr(current_form, field, None)
                history_val = getattr(history_version, field, None)
                
                if current_val != history_val:
                    differences['datos_personales'][field] = {
                        'actual': current_val,
                        'version_anterior': history_val
                    }
            
            # Comparar actividades (simplificado)
            current_activities = self._count_activities(current_form)
            history_activities = history_version.actividades_json or {}
            
            for activity_type in current_activities:
                current_count = current_activities[activity_type]
                history_count = history_activities.get(activity_type, 0)
                
                if current_count != history_count:
                    differences['actividades'][activity_type] = {
                        'actual': current_count,
                        'version_anterior': history_count
                    }
            
            return differences
            
        except Exception as e:
            print(f"Error comparando versiones: {e}")
            return {}
        finally:
            db.close()
    
    def _save_to_history(self, db, form: FormularioEnvioDB, modified_by: str):
        """Guarda la versión actual en el historial"""
        try:
            # Determinar número de versión
            last_version = db.query(FormularioHistoryDB).filter(
                FormularioHistoryDB.formulario_id == form.id
            ).order_by(FormularioHistoryDB.version_numero.desc()).first()
            
            version_number = (last_version.version_numero + 1) if last_version else 1
            
            # Serializar actividades
            activities = self._count_activities(form)
            
            # Crear registro de historial
            history_record = FormularioHistoryDB(
                formulario_id=form.id,
                version_numero=version_number,
                nombre_completo=form.nombre_completo,
                correo_institucional=form.correo_institucional,
                año_academico=form.año_academico,
                trimestre=form.trimestre,
                estado=form.estado,
                fecha_creacion=datetime.utcnow(),
                modificado_por=modified_by,
                motivo_cambio="Corrección aplicada por docente",
                actividades_json=activities
            )
            
            db.add(history_record)
            
        except Exception as e:
            print(f"Error guardando en historial: {e}")
            raise
    
    def _update_form_data(self, db, formulario_id: int, new_data: Dict[str, Any]) -> bool:
        """Actualiza los datos del formulario"""
        try:
            # Actualizar datos básicos
            db.execute(text("""
                UPDATE formularios_envio 
                SET nombre_completo = :nombre,
                    correo_institucional = :correo,
                    año_academico = :año,
                    trimestre = :trimestre,
                    estado = 'PENDIENTE',
                    fecha_revision = NULL,
                    revisado_por = NULL
                WHERE id = :id
            """), {
                'nombre': new_data['nombre_completo'],
                'correo': new_data['correo_institucional'],
                'año': new_data['año_academico'],
                'trimestre': new_data['trimestre'],
                'id': formulario_id
            })
            
            # Eliminar actividades existentes
            self._delete_existing_activities(db, formulario_id)
            
            # Insertar nuevas actividades
            self._insert_new_activities(db, formulario_id, new_data)
            
            return True
            
        except Exception as e:
            print(f"Error actualizando formulario: {e}")
            return False
    
    def _delete_existing_activities(self, db, formulario_id: int):
        """Elimina todas las actividades existentes del formulario"""
        tables = [
            'cursos_capacitacion',
            'publicaciones',
            'eventos_academicos',
            'diseno_curricular',
            'experiencias_movilidad',
            'reconocimientos',
            'certificaciones'
        ]
        
        for table in tables:
            db.execute(text(f"DELETE FROM {table} WHERE formulario_id = :id"), {'id': formulario_id})
    
    def _insert_new_activities(self, db, formulario_id: int, data: Dict[str, Any]):
        """Inserta las nuevas actividades del formulario"""
        # Usar el CRUD existente para insertar actividades
        crud = FormularioCRUD(db)
        
        # Insertar cada tipo de actividad
        if data.get('cursos_capacitacion'):
            for curso in data['cursos_capacitacion']:
                crud.add_curso_capacitacion({
                    'formulario_id': formulario_id,
                    **curso
                })
        
        if data.get('publicaciones'):
            for pub in data['publicaciones']:
                crud.add_publicacion({
                    'formulario_id': formulario_id,
                    **pub
                })
        
        if data.get('eventos_academicos'):
            for evento in data['eventos_academicos']:
                crud.add_evento_academico({
                    'formulario_id': formulario_id,
                    **evento
                })
        
        if data.get('diseno_curricular'):
            for diseno in data['diseno_curricular']:
                crud.add_diseno_curricular({
                    'formulario_id': formulario_id,
                    **diseno
                })
        
        if data.get('movilidad'):
            for mov in data['movilidad']:
                crud.add_movilidad({
                    'formulario_id': formulario_id,
                    **mov
                })
        
        if data.get('reconocimientos'):
            for rec in data['reconocimientos']:
                crud.add_reconocimiento({
                    'formulario_id': formulario_id,
                    **rec
                })
        
        if data.get('certificaciones'):
            for cert in data['certificaciones']:
                crud.add_certificacion({
                    'formulario_id': formulario_id,
                    **cert
                })
    
    def _count_activities(self, form: FormularioEnvioDB) -> Dict[str, int]:
        """Cuenta las actividades de un formulario"""
        try:
            return {
                'cursos_capacitacion': len(form.cursos_capacitacion or []),
                'publicaciones': len(form.publicaciones or []),
                'eventos_academicos': len(form.eventos_academicos or []),
                'diseno_curricular': len(form.diseno_curricular or []),
                'experiencias_movilidad': len(form.movilidad or []),
                'reconocimientos': len(form.reconocimientos or []),
                'certificaciones': len(form.certificaciones or [])
            }
        except:
            return {
                'cursos_capacitacion': 0,
                'publicaciones': 0,
                'eventos_academicos': 0,
                'diseno_curricular': 0,
                'experiencias_movilidad': 0,
                'reconocimientos': 0,
                'certificaciones': 0
            }