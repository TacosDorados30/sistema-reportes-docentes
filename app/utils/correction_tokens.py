"""
Sistema de tokens para corrección de formularios
Permite generar links únicos para que los maestros corrijan sus formularios
"""

import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.database.connection import SessionLocal
from app.database.crud import FormularioCRUD
from sqlalchemy import text


class CorrectionTokenManager:
    """Gestiona los tokens de corrección para formularios"""

    def __init__(self):
        self.token_length = 32
        self.token_expiry_hours = 72  # 3 días para hacer correcciones

    def generate_token(self) -> str:
        """Genera un token único y seguro"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(self.token_length))

    def create_correction_token(self, formulario_id: int) -> Optional[str]:
        """
        Crea un token de corrección para un formulario específico

        Args:
            formulario_id: ID del formulario original

        Returns:
            Token generado o None si hay error
        """
        db = SessionLocal()
        try:
            crud = FormularioCRUD(db)

            # Verificar que el formulario existe
            formulario = crud.get_formulario(formulario_id)
            if not formulario:
                return None

            # Generar token único
            token = self.generate_token()

            # Verificar que el token no existe (muy improbable pero por seguridad)
            while self._token_exists(token):
                token = self.generate_token()

            # Actualizar el formulario con el token
            db.execute(text("""
                UPDATE formularios_envio 
                SET token_correccion = :token 
                WHERE id = :formulario_id
            """), {"token": token, "formulario_id": formulario_id})

            db.commit()

            return token

        except Exception as e:
            print(f"Error creando token de corrección: {e}")
            db.rollback()
            return None
        finally:
            db.close()

    def get_formulario_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene los datos del formulario usando el token de corrección

        Args:
            token: Token de corrección

        Returns:
            Diccionario con los datos del formulario o None si no existe
        """
        db = SessionLocal()
        try:
            crud = FormularioCRUD(db)

            # Buscar formulario por token
            result = db.execute(text("""
                SELECT * FROM formularios_envio 
                WHERE token_correccion = :token
            """), {"token": token})

            formulario_row = result.fetchone()

            if not formulario_row:
                return None

            # Convertir a diccionario
            formulario_data = {
                'id': formulario_row.id,
                'nombre_completo': formulario_row.nombre_completo,
                'correo_institucional': formulario_row.correo_institucional,
                'año_academico': formulario_row.año_academico,
                'trimestre': formulario_row.trimestre,
                'version': formulario_row.version,
                'formulario_original_id': formulario_row.formulario_original_id
            }

            # Obtener el formulario completo con relaciones
            formulario_completo = crud.get_formulario(formulario_row.id)

            if formulario_completo:
                # Agregar actividades
                formulario_data['cursos_capacitacion'] = self._serialize_cursos(
                    formulario_completo.cursos_capacitacion)
                formulario_data['publicaciones'] = self._serialize_publicaciones(
                    formulario_completo.publicaciones)
                formulario_data['eventos_academicos'] = self._serialize_eventos(
                    formulario_completo.eventos_academicos)
                formulario_data['diseno_curricular'] = self._serialize_disenos(
                    formulario_completo.diseno_curricular)
                formulario_data['experiencias_movilidad'] = self._serialize_movilidades(
                    formulario_completo.movilidad)
                formulario_data['reconocimientos'] = self._serialize_reconocimientos(
                    formulario_completo.reconocimientos)
                formulario_data['certificaciones'] = self._serialize_certificaciones(
                    formulario_completo.certificaciones)

            return formulario_data

        except Exception as e:
            print(f"Error obteniendo formulario por token: {e}")
            return None
        finally:
            db.close()

    def invalidate_token(self, token: str) -> bool:
        """
        Invalida un token de corrección

        Args:
            token: Token a invalidar

        Returns:
            True si se invalidó correctamente
        """
        db = SessionLocal()
        try:
            result = db.execute(text("""
                UPDATE formularios_envio 
                SET token_correccion = NULL 
                WHERE token_correccion = :token
            """), {"token": token})

            db.commit()

            return result.rowcount > 0

        except Exception as e:
            print(f"Error invalidando token: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    def create_correction_url(self, formulario_id: int, base_url: str = "http://localhost:8501") -> Optional[str]:
        """
        Crea una URL completa para corrección de formulario

        Args:
            formulario_id: ID del formulario
            base_url: URL base del sistema

        Returns:
            URL completa para corrección o None si hay error
        """
        token = self.create_correction_token(formulario_id)

        if not token:
            return None

        return f"{base_url}/formulario?token={token}&mode=correction"

    def _token_exists(self, token: str) -> bool:
        """Verifica si un token ya existe en la base de datos"""
        db = SessionLocal()
        try:
            result = db.execute(text("""
                SELECT COUNT(*) FROM formularios_envio 
                WHERE token_correccion = :token
            """), {"token": token})

            count = result.fetchone()[0]
            return count > 0

        except:
            return False
        finally:
            db.close()

    def _serialize_cursos(self, cursos):
        """Serializa cursos de capacitación"""
        if not cursos:
            return []

        return [{
            'nombre_curso': curso.nombre_curso,
            'fecha': curso.fecha.isoformat() if curso.fecha else None,
            'horas': curso.horas
        } for curso in cursos]

    def _serialize_publicaciones(self, publicaciones):
        """Serializa publicaciones"""
        if not publicaciones:
            return []

        return [{
            'autores': pub.autores,
            'titulo': pub.titulo,
            'evento_revista': pub.evento_revista,
            'estatus': pub.estatus.value
        } for pub in publicaciones]

    def _serialize_eventos(self, eventos):
        """Serializa eventos académicos"""
        if not eventos:
            return []

        return [{
            'nombre_evento': evento.nombre_evento,
            'fecha': evento.fecha.isoformat() if evento.fecha else None,
            'tipo_participacion': evento.tipo_participacion.value
        } for evento in eventos]

    def _serialize_disenos(self, disenos):
        """Serializa diseños curriculares"""
        if not disenos:
            return []

        return [{
            'nombre_curso': diseno.nombre_curso,
            'descripcion': diseno.descripcion or ''
        } for diseno in disenos]

    def _serialize_movilidades(self, movilidades):
        """Serializa experiencias de movilidad"""
        if not movilidades:
            return []

        return [{
            'descripcion': mov.descripcion,
            'tipo': mov.tipo.value,
            'fecha': mov.fecha.isoformat() if mov.fecha else None
        } for mov in movilidades]

    def _serialize_reconocimientos(self, reconocimientos):
        """Serializa reconocimientos"""
        if not reconocimientos:
            return []

        return [{
            'nombre': rec.nombre,
            'tipo': rec.tipo.value,
            'fecha': rec.fecha.isoformat() if rec.fecha else None
        } for rec in reconocimientos]

    def _serialize_certificaciones(self, certificaciones):
        """Serializa certificaciones"""
        if not certificaciones:
            return []

        return [{
            'nombre': cert.nombre,
            'fecha_obtencion': cert.fecha_obtencion.isoformat() if cert.fecha_obtencion else None,
            'fecha_vencimiento': cert.fecha_vencimiento.isoformat() if cert.fecha_vencimiento else None,
            'vigente': cert.vigente
        } for cert in certificaciones]
