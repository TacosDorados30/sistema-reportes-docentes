from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, extract
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from app.models.database import (
    FormularioEnvioDB, CursoCapacitacionDB, PublicacionDB, EventoAcademicoDB,
    DisenoCurricularDB, ExperienciaMovilidadDB, ReconocimientoDB, CertificacionDB,
    OtraActividadAcademicaDB, AuditLogDB, EstadoFormularioEnum, MaestroAutorizadoDB
)
from app.models.schemas import (
    FormData, FormularioEnvio, EstadoFormulario, MetricasResponse
)

class FormularioCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def create_formulario(self, form_data: FormData, original_id: Optional[int] = None, version: int = 1) -> FormularioEnvioDB:
        """Create a new form submission with version support"""
        # Create main form record
        db_formulario = FormularioEnvioDB(
            nombre_completo=form_data.nombre_completo,
            correo_institucional=form_data.correo_institucional,
            año_academico=form_data.año_academico,
            trimestre=form_data.trimestre,
            fecha_envio=datetime.utcnow(),
            formulario_original_id=original_id,
            version=version,
            es_version_activa=True
        )
        
        self.db.add(db_formulario)
        self.db.flush()  # Get the ID without committing
        
        # Add related records
        self._add_cursos_capacitacion(db_formulario.id, form_data.cursos_capacitacion)
        self._add_publicaciones(db_formulario.id, form_data.publicaciones)
        self._add_eventos_academicos(db_formulario.id, form_data.eventos_academicos)
        self._add_diseno_curricular(db_formulario.id, form_data.diseno_curricular)
        self._add_movilidad(db_formulario.id, form_data.movilidad)
        self._add_reconocimientos(db_formulario.id, form_data.reconocimientos)
        self._add_certificaciones(db_formulario.id, form_data.certificaciones)
        self._add_otras_actividades(db_formulario.id, form_data.otras_actividades)
        
        # Add audit log
        self._add_audit_log(db_formulario.id, "CREADO", None, "Formulario enviado por docente")
        
        self.db.commit()
        self.db.refresh(db_formulario)
        return db_formulario
    
    def create_formulario_completo(self, form_dict: Dict[str, Any]) -> Optional[FormularioEnvioDB]:
        """Create a complete form from dictionary data (for imports)"""
        try:
            # Create main form record
            db_formulario = FormularioEnvioDB(
                nombre_completo=form_dict.get("nombre_completo"),
                correo_institucional=form_dict.get("correo_institucional"),
                año_academico=form_dict.get("año_academico"),
                trimestre=form_dict.get("trimestre"),
                estado=EstadoFormularioEnum(form_dict.get("estado", "PENDIENTE")),
                fecha_envio=form_dict.get("fecha_envio", datetime.utcnow()),
                fecha_revision=form_dict.get("fecha_revision"),
                revisado_por=form_dict.get("revisado_por")
            )
            
            self.db.add(db_formulario)
            self.db.flush()  # Get the ID without committing
            
            # Add related records from dictionary data
            if form_dict.get("cursos_capacitacion"):
                for curso_data in form_dict["cursos_capacitacion"]:
                    curso = CursoCapacitacionDB(
                        formulario_id=db_formulario.id,
                        nombre_curso=curso_data.get("nombre_curso"),
                        fecha=datetime.fromisoformat(curso_data["fecha"]).date() if curso_data.get("fecha") else None,
                        horas=curso_data.get("horas", 0)
                    )
                    self.db.add(curso)
            
            if form_dict.get("publicaciones"):
                for pub_data in form_dict["publicaciones"]:
                    from app.models.database import EstatusPublicacionEnum
                    pub = PublicacionDB(
                        formulario_id=db_formulario.id,
                        autores=pub_data.get("autores"),
                        titulo=pub_data.get("titulo"),
                        evento_revista=pub_data.get("evento_revista"),
                        estatus=EstatusPublicacionEnum(pub_data.get("estatus", "EN_REVISION"))
                    )
                    self.db.add(pub)
            
            if form_dict.get("eventos_academicos"):
                for evento_data in form_dict["eventos_academicos"]:
                    from app.models.database import TipoParticipacionEnum
                    evento = EventoAcademicoDB(
                        formulario_id=db_formulario.id,
                        nombre_evento=evento_data.get("nombre_evento"),
                        fecha=datetime.fromisoformat(evento_data["fecha"]).date() if evento_data.get("fecha") else None,
                        tipo_participacion=TipoParticipacionEnum(evento_data.get("tipo_participacion", "PARTICIPANTE"))
                    )
                    self.db.add(evento)
            
            if form_dict.get("diseno_curricular"):
                for diseno_data in form_dict["diseno_curricular"]:
                    diseno = DisenoCurricularDB(
                        formulario_id=db_formulario.id,
                        nombre_curso=diseno_data.get("nombre_curso"),
                        descripcion=diseno_data.get("descripcion")
                    )
                    self.db.add(diseno)
            
            if form_dict.get("movilidad"):
                for mov_data in form_dict["movilidad"]:
                    from app.models.database import TipoMovilidadEnum
                    mov = ExperienciaMovilidadDB(
                        formulario_id=db_formulario.id,
                        descripcion=mov_data.get("descripcion"),
                        tipo=TipoMovilidadEnum(mov_data.get("tipo", "NACIONAL")),
                        fecha=datetime.fromisoformat(mov_data["fecha"]).date() if mov_data.get("fecha") else None
                    )
                    self.db.add(mov)
            
            if form_dict.get("reconocimientos"):
                for rec_data in form_dict["reconocimientos"]:
                    from app.models.database import TipoReconocimientoEnum
                    rec = ReconocimientoDB(
                        formulario_id=db_formulario.id,
                        nombre=rec_data.get("nombre"),
                        tipo=TipoReconocimientoEnum(rec_data.get("tipo", "DISTINCION")),
                        fecha=datetime.fromisoformat(rec_data["fecha"]).date() if rec_data.get("fecha") else None
                    )
                    self.db.add(rec)
            
            if form_dict.get("certificaciones"):
                for cert_data in form_dict["certificaciones"]:
                    cert = CertificacionDB(
                        formulario_id=db_formulario.id,
                        nombre=cert_data.get("nombre"),
                        fecha_obtencion=datetime.fromisoformat(cert_data["fecha_obtencion"]).date() if cert_data.get("fecha_obtencion") else None
                    )
                    self.db.add(cert)
            
            # Add audit log
            self._add_audit_log(db_formulario.id, "IMPORTADO", None, "Formulario importado desde backup")
            
            self.db.commit()
            self.db.refresh(db_formulario)
            return db_formulario
            
        except Exception as e:
            self.db.rollback()
            print(f"Error creating complete form: {e}")
            return None
    
    def get_formulario(self, formulario_id: int) -> Optional[FormularioEnvioDB]:
        """Get a form by ID with all related data"""
        return self.db.query(FormularioEnvioDB).filter(
            FormularioEnvioDB.id == formulario_id
        ).first()
    
    def get_formularios_pendientes(self, skip: int = 0, limit: int = 100) -> List[FormularioEnvioDB]:
        """Get pending forms"""
        return self.db.query(FormularioEnvioDB).filter(
            FormularioEnvioDB.estado == EstadoFormularioEnum.PENDIENTE
        ).offset(skip).limit(limit).all()
    
    def get_estadisticas_generales(self) -> Dict[str, Any]:
        """Get general statistics"""
        total_formularios = self.db.query(FormularioEnvioDB).count()
        pendientes = self.db.query(FormularioEnvioDB).filter(
            FormularioEnvioDB.estado == EstadoFormularioEnum.PENDIENTE
        ).count()
        aprobados = self.db.query(FormularioEnvioDB).filter(
            FormularioEnvioDB.estado == EstadoFormularioEnum.APROBADO
        ).count()
        rechazados = self.db.query(FormularioEnvioDB).filter(
            FormularioEnvioDB.estado == EstadoFormularioEnum.RECHAZADO
        ).count()
        
        return {
            "total_formularios": total_formularios,
            "pendientes": pendientes,
            "aprobados": aprobados,
            "rechazados": rechazados
        }
    
    def get_formularios_by_estado(
        self, 
        estado: EstadoFormularioEnum, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[FormularioEnvioDB]:
        """Get forms by status with pagination - only active versions"""
        return self.db.query(FormularioEnvioDB).filter(
            and_(
                FormularioEnvioDB.estado == estado,
                FormularioEnvioDB.es_version_activa == True
            )
        ).offset(skip).limit(limit).all()
    
    def get_all_formularios(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[FormularioEnvioDB]:
        """Get all forms with pagination - only active versions"""
        return self.db.query(FormularioEnvioDB).filter(
            FormularioEnvioDB.es_version_activa == True
        ).offset(skip).limit(limit).all()
    
    def aprobar_formulario(self, formulario_id: int, usuario: str = "admin") -> bool:
        """Approve a form submission"""
        formulario = self.get_formulario(formulario_id)
        if not formulario:
            return False
        
        formulario.estado = EstadoFormularioEnum.APROBADO
        formulario.fecha_revision = datetime.utcnow()
        formulario.revisado_por = usuario
        
        self._add_audit_log(formulario_id, "APROBADO", usuario, "Formulario aprobado")
        
        self.db.commit()
        return True
    
    def rechazar_formulario(self, formulario_id: int, usuario: str = "admin", comentario: str = None) -> bool:
        """Reject a form submission"""
        formulario = self.get_formulario(formulario_id)
        if not formulario:
            return False
        
        formulario.estado = EstadoFormularioEnum.RECHAZADO
        formulario.fecha_revision = datetime.utcnow()
        formulario.revisado_por = usuario
        
        self._add_audit_log(formulario_id, "RECHAZADO", usuario, comentario or "Formulario rechazado")
        
        self.db.commit()
        return True
    
    def get_metricas_generales(self) -> MetricasResponse:
        """Get general metrics for dashboard - only active versions"""
        # Count forms by status (only active versions)
        total_formularios = self.db.query(FormularioEnvioDB).filter(
            FormularioEnvioDB.es_version_activa == True
        ).count()
        
        pendientes = self.db.query(FormularioEnvioDB).filter(
            and_(
                FormularioEnvioDB.estado == EstadoFormularioEnum.PENDIENTE,
                FormularioEnvioDB.es_version_activa == True
            )
        ).count()
        
        aprobados = self.db.query(FormularioEnvioDB).filter(
            and_(
                FormularioEnvioDB.estado == EstadoFormularioEnum.APROBADO,
                FormularioEnvioDB.es_version_activa == True
            )
        ).count()
        
        rechazados = self.db.query(FormularioEnvioDB).filter(
            and_(
                FormularioEnvioDB.estado == EstadoFormularioEnum.RECHAZADO,
                FormularioEnvioDB.es_version_activa == True
            )
        ).count()
        
        # Count approved data only (from active versions)
        approved_forms_query = self.db.query(FormularioEnvioDB.id).filter(
            and_(
                FormularioEnvioDB.estado == EstadoFormularioEnum.APROBADO,
                FormularioEnvioDB.es_version_activa == True
            )
        )
        
        total_cursos = self.db.query(CursoCapacitacionDB).filter(
            CursoCapacitacionDB.formulario_id.in_(approved_forms_query)
        ).count()
        
        total_horas = self.db.query(func.sum(CursoCapacitacionDB.horas)).filter(
            CursoCapacitacionDB.formulario_id.in_(approved_forms_query)
        ).scalar() or 0
        
        total_publicaciones = self.db.query(PublicacionDB).filter(
            PublicacionDB.formulario_id.in_(approved_forms_query)
        ).count()
        
        total_eventos = self.db.query(EventoAcademicoDB).filter(
            EventoAcademicoDB.formulario_id.in_(approved_forms_query)
        ).count()
        
        total_disenos = self.db.query(DisenoCurricularDB).filter(
            DisenoCurricularDB.formulario_id.in_(approved_forms_query)
        ).count()
        
        total_movilidades = self.db.query(ExperienciaMovilidadDB).filter(
            ExperienciaMovilidadDB.formulario_id.in_(approved_forms_query)
        ).count()
        
        total_reconocimientos = self.db.query(ReconocimientoDB).filter(
            ReconocimientoDB.formulario_id.in_(approved_forms_query)
        ).count()
        
        total_certificaciones = self.db.query(CertificacionDB).filter(
            CertificacionDB.formulario_id.in_(approved_forms_query)
        ).count()
        
        total_otras_actividades = self.db.query(OtraActividadAcademicaDB).filter(
            OtraActividadAcademicaDB.formulario_id.in_(approved_forms_query)
        ).count()
        
        return MetricasResponse(
            total_formularios=total_formularios,
            formularios_pendientes=pendientes,
            formularios_aprobados=aprobados,
            formularios_rechazados=rechazados,
            total_cursos=total_cursos,
            total_horas_capacitacion=total_horas,
            total_publicaciones=total_publicaciones,
            total_eventos=total_eventos,
            total_disenos_curriculares=total_disenos,
            total_movilidades=total_movilidades,
            total_reconocimientos=total_reconocimientos,
            total_certificaciones=total_certificaciones,
            total_otras_actividades=total_otras_actividades
        )
    
    def get_datos_por_periodo(self, year: int, quarter: Optional[int] = None) -> Dict[str, Any]:
        """Get data for a specific period (year and optionally quarter)"""
        # Base query for approved forms
        query = self.db.query(FormularioEnvioDB).filter(
            FormularioEnvioDB.estado == EstadoFormularioEnum.APROBADO
        )
        
        # Filter by year
        query = query.filter(extract('year', FormularioEnvioDB.fecha_envio) == year)
        
        # Filter by quarter if specified
        if quarter:
            start_month = (quarter - 1) * 3 + 1
            end_month = quarter * 3
            query = query.filter(
                and_(
                    extract('month', FormularioEnvioDB.fecha_envio) >= start_month,
                    extract('month', FormularioEnvioDB.fecha_envio) <= end_month
                )
            )
        
        formularios = query.all()
        formulario_ids = [f.id for f in formularios]
        
        if not formulario_ids:
            return {}
        
        # Get detailed data for the period
        data = {
            'formularios': len(formularios),
            'cursos': self._get_cursos_data(formulario_ids),
            'publicaciones': self._get_publicaciones_data(formulario_ids),
            'eventos': self._get_eventos_data(formulario_ids),
            'disenos': self._get_disenos_data(formulario_ids),
            'movilidades': self._get_movilidades_data(formulario_ids),
            'reconocimientos': self._get_reconocimientos_data(formulario_ids),
            'certificaciones': self._get_certificaciones_data(formulario_ids)
        }
        
        return data
    
    # Helper methods
    def _add_cursos_capacitacion(self, formulario_id: int, cursos: List):
        for curso in cursos:
            db_curso = CursoCapacitacionDB(
                formulario_id=formulario_id,
                nombre_curso=curso.nombre_curso,
                fecha=curso.fecha,
                horas=curso.horas
            )
            self.db.add(db_curso)
    
    def _add_publicaciones(self, formulario_id: int, publicaciones: List):
        for pub in publicaciones:
            db_pub = PublicacionDB(
                formulario_id=formulario_id,
                autores=pub.autores,
                titulo=pub.titulo,
                evento_revista=pub.evento_revista,
                estatus=pub.estatus
            )
            self.db.add(db_pub)
    
    def _add_eventos_academicos(self, formulario_id: int, eventos: List):
        for evento in eventos:
            db_evento = EventoAcademicoDB(
                formulario_id=formulario_id,
                nombre_evento=evento.nombre_evento,
                fecha=evento.fecha,
                tipo_participacion=evento.tipo_participacion
            )
            self.db.add(db_evento)
    
    def _add_diseno_curricular(self, formulario_id: int, disenos: List):
        for diseno in disenos:
            db_diseno = DisenoCurricularDB(
                formulario_id=formulario_id,
                nombre_curso=diseno.nombre_curso,
                descripcion=diseno.descripcion
            )
            self.db.add(db_diseno)
    
    def _add_movilidad(self, formulario_id: int, movilidades: List):
        for mov in movilidades:
            db_mov = ExperienciaMovilidadDB(
                formulario_id=formulario_id,
                descripcion=mov.descripcion,
                tipo=mov.tipo,
                fecha=mov.fecha
            )
            self.db.add(db_mov)
    
    def _add_reconocimientos(self, formulario_id: int, reconocimientos: List):
        for rec in reconocimientos:
            db_rec = ReconocimientoDB(
                formulario_id=formulario_id,
                nombre=rec.nombre,
                tipo=rec.tipo,
                fecha=rec.fecha
            )
            self.db.add(db_rec)
    
    def _add_certificaciones(self, formulario_id: int, certificaciones: List):
        for cert in certificaciones:
            db_cert = CertificacionDB(
                formulario_id=formulario_id,
                nombre=cert.nombre,
                fecha_obtencion=cert.fecha_obtencion
            )
            self.db.add(db_cert)
    
    def _add_otras_actividades(self, formulario_id: int, otras_actividades: List):
        for actividad in otras_actividades:
            db_actividad = OtraActividadAcademicaDB(
                formulario_id=formulario_id,
                categoria=actividad.categoria,
                titulo=actividad.titulo,
                descripcion=actividad.descripcion,
                fecha=actividad.fecha,
                cantidad=actividad.cantidad,
                observaciones=actividad.observaciones
            )
            self.db.add(db_actividad)
    
    def _add_audit_log(self, formulario_id: int, accion: str, usuario: str, comentario: str):
        audit = AuditLogDB(
            formulario_id=formulario_id,
            accion=accion,
            usuario=usuario,
            comentario=comentario
        )
        self.db.add(audit)
    
    def _get_cursos_data(self, formulario_ids: List[int]) -> Dict:
        cursos = self.db.query(CursoCapacitacionDB).filter(
            CursoCapacitacionDB.formulario_id.in_(formulario_ids)
        ).all()
        
        total_horas = sum(c.horas for c in cursos)
        nombres = [c.nombre_curso for c in cursos]
        
        return {
            'total': len(cursos),
            'total_horas': total_horas,
            'nombres': nombres
        }
    
    def _get_publicaciones_data(self, formulario_ids: List[int]) -> Dict:
        publicaciones = self.db.query(PublicacionDB).filter(
            PublicacionDB.formulario_id.in_(formulario_ids)
        ).all()
        
        por_estatus = {}
        titulos = []
        
        for pub in publicaciones:
            estatus = pub.estatus.value
            por_estatus[estatus] = por_estatus.get(estatus, 0) + 1
            titulos.append(pub.titulo)
        
        return {
            'total': len(publicaciones),
            'por_estatus': por_estatus,
            'titulos': titulos
        }
    
    def _get_eventos_data(self, formulario_ids: List[int]) -> Dict:
        eventos = self.db.query(EventoAcademicoDB).filter(
            EventoAcademicoDB.formulario_id.in_(formulario_ids)
        ).all()
        
        nombres = [e.nombre_evento for e in eventos]
        por_tipo = {}
        
        for evento in eventos:
            tipo = evento.tipo_participacion.value
            por_tipo[tipo] = por_tipo.get(tipo, 0) + 1
        
        return {
            'total': len(eventos),
            'nombres': nombres,
            'por_tipo': por_tipo
        }
    
    def _get_disenos_data(self, formulario_ids: List[int]) -> Dict:
        disenos = self.db.query(DisenoCurricularDB).filter(
            DisenoCurricularDB.formulario_id.in_(formulario_ids)
        ).all()
        
        nombres = [d.nombre_curso for d in disenos]
        
        return {
            'total': len(disenos),
            'nombres': nombres
        }
    
    def _get_movilidades_data(self, formulario_ids: List[int]) -> Dict:
        movilidades = self.db.query(ExperienciaMovilidadDB).filter(
            ExperienciaMovilidadDB.formulario_id.in_(formulario_ids)
        ).all()
        
        por_tipo = {}
        descripciones = []
        
        for mov in movilidades:
            tipo = mov.tipo.value
            por_tipo[tipo] = por_tipo.get(tipo, 0) + 1
            descripciones.append(mov.descripcion)
        
        return {
            'total': len(movilidades),
            'por_tipo': por_tipo,
            'descripciones': descripciones
        }
    
    def _get_reconocimientos_data(self, formulario_ids: List[int]) -> Dict:
        reconocimientos = self.db.query(ReconocimientoDB).filter(
            ReconocimientoDB.formulario_id.in_(formulario_ids)
        ).all()
        
        nombres = [r.nombre for r in reconocimientos]
        por_tipo = {}
        
        for rec in reconocimientos:
            tipo = rec.tipo.value
            por_tipo[tipo] = por_tipo.get(tipo, 0) + 1
        
        return {
            'total': len(reconocimientos),
            'nombres': nombres,
            'por_tipo': por_tipo
        }
    
    def _get_certificaciones_data(self, formulario_ids: List[int]) -> Dict:
        certificaciones = self.db.query(CertificacionDB).filter(
            CertificacionDB.formulario_id.in_(formulario_ids)
        ).all()
        
        nombres = [c.nombre for c in certificaciones]
        
        return {
            'total': len(certificaciones),
            'nombres': nombres
        }    
    # Métodos para sistema de versiones
    
    def create_formulario_version(self, original_id: int, form_data: FormData) -> Optional[FormularioEnvioDB]:
        """
        Crea una nueva versión de un formulario existente
        
        Args:
            original_id: ID del formulario original
            form_data: Datos del nuevo formulario
            
        Returns:
            Nueva versión del formulario o None si hay error
        """
        try:
            # Obtener el formulario original
            original_form = self.get_formulario(original_id)
            if not original_form:
                return None
            
            # Determinar el número de versión
            # Si el formulario original ya es una versión, usar su original_id
            base_id = original_form.formulario_original_id or original_id
            
            # Contar versiones existentes
            version_count = self.db.query(FormularioEnvioDB).filter(
                or_(
                    FormularioEnvioDB.id == base_id,
                    FormularioEnvioDB.formulario_original_id == base_id
                )
            ).count()
            
            new_version = version_count + 1
            
            # Marcar versiones anteriores como inactivas
            self.db.query(FormularioEnvioDB).filter(
                or_(
                    FormularioEnvioDB.id == base_id,
                    FormularioEnvioDB.formulario_original_id == base_id
                )
            ).update({"es_version_activa": False})
            
            # Crear nueva versión
            nueva_version = self.create_formulario(
                form_data=form_data,
                original_id=base_id,
                version=new_version
            )
            
            return nueva_version
            
        except Exception as e:
            print(f"Error creando versión de formulario: {e}")
            self.db.rollback()
            return None
    
    def get_formulario_versions(self, formulario_id: int) -> List[FormularioEnvioDB]:
        """
        Obtiene todas las versiones de un formulario
        
        Args:
            formulario_id: ID del formulario (puede ser original o versión)
            
        Returns:
            Lista de todas las versiones ordenadas por versión
        """
        try:
            # Obtener el formulario para determinar el ID base
            formulario = self.get_formulario(formulario_id)
            if not formulario:
                return []
            
            base_id = formulario.formulario_original_id or formulario_id
            
            # Obtener todas las versiones
            versions = self.db.query(FormularioEnvioDB).filter(
                or_(
                    FormularioEnvioDB.id == base_id,
                    FormularioEnvioDB.formulario_original_id == base_id
                )
            ).order_by(FormularioEnvioDB.version).all()
            
            return versions
            
        except Exception as e:
            print(f"Error obteniendo versiones: {e}")
            return []
    
    def get_active_version(self, formulario_id: int) -> Optional[FormularioEnvioDB]:
        """
        Obtiene la versión activa de un formulario
        
        Args:
            formulario_id: ID del formulario (puede ser original o versión)
            
        Returns:
            Versión activa del formulario o None
        """
        try:
            # Obtener el formulario para determinar el ID base
            formulario = self.get_formulario(formulario_id)
            if not formulario:
                return None
            
            base_id = formulario.formulario_original_id or formulario_id
            
            # Obtener la versión activa
            active_version = self.db.query(FormularioEnvioDB).filter(
                and_(
                    or_(
                        FormularioEnvioDB.id == base_id,
                        FormularioEnvioDB.formulario_original_id == base_id
                    ),
                    FormularioEnvioDB.es_version_activa == True
                )
            ).first()
            
            return active_version
            
        except Exception as e:
            print(f"Error obteniendo versión activa: {e}")
            return None
    
    def compare_versions(self, version1_id: int, version2_id: int) -> Dict[str, Any]:
        """
        Compara dos versiones de un formulario
        
        Args:
            version1_id: ID de la primera versión
            version2_id: ID de la segunda versión
            
        Returns:
            Diccionario con las diferencias encontradas
        """
        try:
            v1 = self.get_formulario(version1_id)
            v2 = self.get_formulario(version2_id)
            
            if not v1 or not v2:
                return {}
            
            differences = {
                'datos_personales': {},
                'actividades': {}
            }
            
            # Comparar datos personales
            personal_fields = ['nombre_completo', 'correo_institucional', 'año_academico', 'trimestre']
            for field in personal_fields:
                val1 = getattr(v1, field, None)
                val2 = getattr(v2, field, None)
                if val1 != val2:
                    differences['datos_personales'][field] = {
                        'version_1': val1,
                        'version_2': val2
                    }
            
            # Comparar actividades (simplificado - solo contar)
            activity_fields = [
                'cursos_capacitacion', 'publicaciones', 'eventos_academicos',
                'diseno_curricular', 'experiencias_movilidad', 'reconocimientos', 'certificaciones'
            ]
            
            for field in activity_fields:
                list1 = getattr(v1, field, []) or []
                list2 = getattr(v2, field, []) or []
                if len(list1) != len(list2):
                    differences['actividades'][field] = {
                        'version_1_count': len(list1),
                        'version_2_count': len(list2)
                    }
            
            return differences
            
        except Exception as e:
            print(f"Error comparando versiones: {e}")
            return {} 
   
    def update_formulario_completo(self, formulario_id: int, form_data: FormData) -> Optional[int]:
        """
        Actualiza un formulario existente con nuevos datos
        
        Args:
            formulario_id: ID del formulario a actualizar
            form_data: Nuevos datos del formulario
            
        Returns:
            ID del formulario actualizado o None si hay error
        """
        try:
            # Obtener el formulario existente
            formulario = self.get_formulario(formulario_id)
            if not formulario:
                return None
            
            # Actualizar datos básicos
            formulario.nombre_completo = form_data.nombre_completo
            formulario.correo_institucional = form_data.correo_institucional
            formulario.año_academico = form_data.año_academico
            formulario.trimestre = form_data.trimestre
            
            # Resetear estado a PENDIENTE para nueva revisión
            formulario.estado = EstadoFormularioEnum.PENDIENTE
            formulario.fecha_revision = None
            formulario.revisado_por = None
            
            # Eliminar todas las actividades existentes
            self.db.query(CursoCapacitacionDB).filter(CursoCapacitacionDB.formulario_id == formulario_id).delete()
            self.db.query(PublicacionDB).filter(PublicacionDB.formulario_id == formulario_id).delete()
            self.db.query(EventoAcademicoDB).filter(EventoAcademicoDB.formulario_id == formulario_id).delete()
            self.db.query(DisenoCurricularDB).filter(DisenoCurricularDB.formulario_id == formulario_id).delete()
            self.db.query(ExperienciaMovilidadDB).filter(ExperienciaMovilidadDB.formulario_id == formulario_id).delete()
            self.db.query(ReconocimientoDB).filter(ReconocimientoDB.formulario_id == formulario_id).delete()
            self.db.query(CertificacionDB).filter(CertificacionDB.formulario_id == formulario_id).delete()
            
            # Agregar las nuevas actividades
            self._add_cursos_capacitacion(formulario_id, form_data.cursos_capacitacion)
            self._add_publicaciones(formulario_id, form_data.publicaciones)
            self._add_eventos_academicos(formulario_id, form_data.eventos_academicos)
            self._add_diseno_curricular(formulario_id, form_data.diseno_curricular)
            self._add_movilidad(formulario_id, form_data.movilidad)
            self._add_reconocimientos(formulario_id, form_data.reconocimientos)
            self._add_certificaciones(formulario_id, form_data.certificaciones)
            
            # Agregar log de auditoría
            self._add_audit_log(formulario_id, "ACTUALIZADO", None, "Formulario actualizado por corrección")
            
            self.db.commit()
            
            return formulario_id
            
        except Exception as e:
            print(f"Error actualizando formulario: {e}")
            self.db.rollback()
            return None    
def update_formulario_completo(self, formulario_id: int, form_data: FormData) -> Optional[int]:
        """
        Actualiza un formulario existente con nuevos datos (para correcciones)
        
        Args:
            formulario_id: ID del formulario a actualizar
            form_data: Nuevos datos del formulario
            
        Returns:
            ID del formulario actualizado o None si hay error
        """
        try:
            # Obtener el formulario existente
            formulario = self.get_formulario(formulario_id)
            if not formulario:
                return None
            
            # Actualizar datos básicos
            formulario.nombre_completo = form_data.nombre_completo
            formulario.correo_institucional = form_data.correo_institucional
            formulario.año_academico = form_data.año_academico
            formulario.trimestre = form_data.trimestre
            formulario.fecha_envio = datetime.utcnow()  # Actualizar fecha de envío
            formulario.estado = EstadoFormularioEnum.PENDIENTE  # Volver a pendiente
            formulario.fecha_revision = None  # Limpiar fecha de revisión
            formulario.revisado_por = None  # Limpiar revisor
            
            # Eliminar todas las actividades existentes
            self.db.query(CursoCapacitacionDB).filter(CursoCapacitacionDB.formulario_id == formulario_id).delete()
            self.db.query(PublicacionDB).filter(PublicacionDB.formulario_id == formulario_id).delete()
            self.db.query(EventoAcademicoDB).filter(EventoAcademicoDB.formulario_id == formulario_id).delete()
            self.db.query(DisenoCurricularDB).filter(DisenoCurricularDB.formulario_id == formulario_id).delete()
            self.db.query(ExperienciaMovilidadDB).filter(ExperienciaMovilidadDB.formulario_id == formulario_id).delete()
            self.db.query(ReconocimientoDB).filter(ReconocimientoDB.formulario_id == formulario_id).delete()
            self.db.query(CertificacionDB).filter(CertificacionDB.formulario_id == formulario_id).delete()
            
            # Agregar las nuevas actividades
            self._add_cursos_capacitacion(formulario_id, form_data.cursos_capacitacion)
            self._add_publicaciones(formulario_id, form_data.publicaciones)
            self._add_eventos_academicos(formulario_id, form_data.eventos_academicos)
            self._add_diseno_curricular(formulario_id, form_data.diseno_curricular)
            self._add_movilidad(formulario_id, form_data.movilidad)
            self._add_reconocimientos(formulario_id, form_data.reconocimientos)
            self._add_certificaciones(formulario_id, form_data.certificaciones)
            
            # Agregar log de auditoría
            self._add_audit_log(formulario_id, "ACTUALIZADO", None, "Formulario actualizado por corrección")
            
            self.db.commit()
            
            return formulario_id
            
        except Exception as e:
            print(f"Error actualizando formulario: {e}")
            self.db.rollback()
            return None


class MaestroAutorizadoCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_maestros(self) -> List[MaestroAutorizadoDB]:
        """Obtiene todos los maestros autorizados activos"""
        return self.db.query(MaestroAutorizadoDB).filter(
            MaestroAutorizadoDB.activo == True
        ).order_by(MaestroAutorizadoDB.nombre_completo).all()
    
    def get_maestro_by_email(self, email: str) -> Optional[MaestroAutorizadoDB]:
        """Obtiene un maestro por su email"""
        return self.db.query(MaestroAutorizadoDB).filter(
            and_(
                MaestroAutorizadoDB.correo_institucional == email,
                MaestroAutorizadoDB.activo == True
            )
        ).first()
    
    def get_maestro_by_id(self, maestro_id: int) -> Optional[MaestroAutorizadoDB]:
        """Obtiene un maestro por su ID"""
        return self.db.query(MaestroAutorizadoDB).filter(
            MaestroAutorizadoDB.id == maestro_id
        ).first()
    
    def create_maestro(self, nombre_completo: str, correo_institucional: str) -> Optional[MaestroAutorizadoDB]:
        """Crea un nuevo maestro autorizado"""
        try:
            # Verificar si ya existe
            existing = self.get_maestro_by_email(correo_institucional)
            if existing:
                return None  # Ya existe
            
            maestro = MaestroAutorizadoDB(
                nombre_completo=nombre_completo,
                correo_institucional=correo_institucional,
                activo=True
            )
            
            self.db.add(maestro)
            self.db.commit()
            self.db.refresh(maestro)
            
            return maestro
            
        except Exception as e:
            print(f"Error creando maestro: {e}")
            self.db.rollback()
            return None
    
    def update_maestro(self, maestro_id: int, nombre_completo: str, correo_institucional: str) -> bool:
        """Actualiza un maestro existente"""
        try:
            maestro = self.get_maestro_by_id(maestro_id)
            if not maestro:
                return False
            
            # Verificar si el nuevo email ya existe en otro maestro
            if maestro.correo_institucional != correo_institucional:
                existing = self.get_maestro_by_email(correo_institucional)
                if existing and existing.id != maestro_id:
                    return False  # Email ya existe en otro maestro
            
            maestro.nombre_completo = nombre_completo
            maestro.correo_institucional = correo_institucional
            maestro.fecha_actualizacion = datetime.utcnow()
            
            self.db.commit()
            return True
            
        except Exception as e:
            print(f"Error actualizando maestro: {e}")
            self.db.rollback()
            return False
    
    def delete_maestro(self, maestro_id: int) -> bool:
        """Desactiva un maestro (soft delete)"""
        try:
            maestro = self.get_maestro_by_id(maestro_id)
            if not maestro:
                return False
            
            maestro.activo = False
            maestro.fecha_actualizacion = datetime.utcnow()
            
            self.db.commit()
            return True
            
        except Exception as e:
            print(f"Error desactivando maestro: {e}")
            self.db.rollback()
            return False
    
    def is_maestro_autorizado(self, email: str) -> bool:
        """Verifica si un email está autorizado"""
        maestro = self.get_maestro_by_email(email)
        return maestro is not None
    
    def get_maestros_options(self) -> Dict[str, str]:
        """Obtiene opciones para selectbox (nombre -> email)"""
        maestros = self.get_all_maestros()
        return {maestro.nombre_completo: maestro.correo_institucional for maestro in maestros}