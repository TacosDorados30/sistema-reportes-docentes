from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, extract
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from app.models.database import (
    FormularioEnvioDB, CursoCapacitacionDB, PublicacionDB, EventoAcademicoDB,
    DisenoCurricularDB, ExperienciaMovilidadDB, ReconocimientoDB, CertificacionDB,
    AuditLogDB, EstadoFormularioEnum
)
from app.models.schemas import (
    FormData, FormularioEnvio, EstadoFormulario, MetricasResponse
)

class FormularioCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def create_formulario(self, form_data: FormData) -> FormularioEnvioDB:
        """Create a new form submission"""
        # Create main form record
        db_formulario = FormularioEnvioDB(
            nombre_completo=form_data.nombre_completo,
            correo_institucional=form_data.correo_institucional,
            año_academico=form_data.año_academico,
            trimestre=form_data.trimestre,
            fecha_envio=datetime.utcnow()
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
                        fecha_obtencion=datetime.fromisoformat(cert_data["fecha_obtencion"]).date() if cert_data.get("fecha_obtencion") else None,
                        fecha_vencimiento=datetime.fromisoformat(cert_data["fecha_vencimiento"]).date() if cert_data.get("fecha_vencimiento") else None,
                        vigente=cert_data.get("vigente", True)
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
        """Get forms by status with pagination"""
        return self.db.query(FormularioEnvioDB).filter(
            FormularioEnvioDB.estado == estado
        ).offset(skip).limit(limit).all()
    
    def get_all_formularios(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[FormularioEnvioDB]:
        """Get all forms with pagination"""
        return self.db.query(FormularioEnvioDB).offset(skip).limit(limit).all()
    
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
        """Get general metrics for dashboard"""
        # Count forms by status
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
        
        # Count approved data only
        approved_forms_query = self.db.query(FormularioEnvioDB.id).filter(
            FormularioEnvioDB.estado == EstadoFormularioEnum.APROBADO
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
            total_certificaciones=total_certificaciones
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
            # Check if certification is still valid
            vigente = True
            if cert.fecha_vencimiento:
                vigente = cert.fecha_vencimiento > date.today()
            
            db_cert = CertificacionDB(
                formulario_id=formulario_id,
                nombre=cert.nombre,
                fecha_obtencion=cert.fecha_obtencion,
                fecha_vencimiento=cert.fecha_vencimiento,
                vigente=vigente
            )
            self.db.add(db_cert)
    
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
        vigentes = sum(1 for c in certificaciones if c.vigente)
        
        return {
            'total': len(certificaciones),
            'vigentes': vigentes,
            'nombres': nombres
        }    
    
def export_to_excel(self) -> bytes:
        """Export data to Excel format"""
        try:
            import pandas as pd
            from io import BytesIO
            
            # Get all approved forms
            approved_forms = self.get_formularios_by_estado(EstadoFormularioEnum.APROBADO)
            
            # Create Excel file
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Main forms sheet
                forms_data = []
                for form in approved_forms:
                    forms_data.append({
                        'ID': form.id,
                        'Nombre': form.nombre_completo,
                        'Email': form.correo_institucional,
                        'Año Académico': getattr(form, 'año_academico', ''),
                        'Trimestre': getattr(form, 'trimestre', ''),
                        'Estado': form.estado.value,
                        'Fecha Envío': form.fecha_envio.strftime('%Y-%m-%d') if form.fecha_envio else '',
                        'Fecha Revisión': form.fecha_revision.strftime('%Y-%m-%d') if form.fecha_revision else '',
                        'Revisado Por': form.revisado_por or ''
                    })
                
                if forms_data:
                    forms_df = pd.DataFrame(forms_data)
                    forms_df.to_excel(writer, sheet_name='Formularios', index=False)
                
                # Courses sheet
                courses_data = []
                for form in approved_forms:
                    for curso in form.cursos_capacitacion or []:
                        courses_data.append({
                            'Formulario ID': form.id,
                            'Docente': form.nombre_completo,
                            'Curso': curso.nombre_curso,
                            'Fecha': curso.fecha.strftime('%Y-%m-%d') if curso.fecha else '',
                            'Horas': curso.horas
                        })
                
                if courses_data:
                    courses_df = pd.DataFrame(courses_data)
                    courses_df.to_excel(writer, sheet_name='Cursos', index=False)
                
                # Publications sheet
                pubs_data = []
                for form in approved_forms:
                    for pub in form.publicaciones or []:
                        pubs_data.append({
                            'Formulario ID': form.id,
                            'Docente': form.nombre_completo,
                            'Autores': pub.autores,
                            'Título': pub.titulo,
                            'Evento/Revista': pub.evento_revista,
                            'Estatus': pub.estatus.value if hasattr(pub.estatus, 'value') else str(pub.estatus)
                        })
                
                if pubs_data:
                    pubs_df = pd.DataFrame(pubs_data)
                    pubs_df.to_excel(writer, sheet_name='Publicaciones', index=False)
            
            output.seek(0)
            return output.getvalue()
            
        except Exception as e:
            print(f"Error exporting to Excel: {e}")
            return b""
    
    def export_to_csv(self) -> str:
        """Export data to CSV format"""
        try:
            import pandas as pd
            from io import StringIO
            
            # Get all approved forms
            approved_forms = self.get_formularios_by_estado(EstadoFormularioEnum.APROBADO)
            
            # Create comprehensive data
            all_data = []
            for form in approved_forms:
                base_data = {
                    'formulario_id': form.id,
                    'nombre_completo': form.nombre_completo,
                    'correo_institucional': form.correo_institucional,
                    'año_academico': getattr(form, 'año_academico', ''),
                    'trimestre': getattr(form, 'trimestre', ''),
                    'estado': form.estado.value,
                    'fecha_envio': form.fecha_envio.strftime('%Y-%m-%d') if form.fecha_envio else '',
                    'fecha_revision': form.fecha_revision.strftime('%Y-%m-%d') if form.fecha_revision else '',
                    'revisado_por': form.revisado_por or ''
                }
                
                # Add activity counts
                base_data.update({
                    'total_cursos': len(form.cursos_capacitacion or []),
                    'total_publicaciones': len(form.publicaciones or []),
                    'total_eventos': len(form.eventos_academicos or []),
                    'total_disenos': len(form.diseno_curricular or []),
                    'total_movilidades': len(form.movilidad or []),
                    'total_reconocimientos': len(form.reconocimientos or []),
                    'total_certificaciones': len(form.certificaciones or [])
                })
                
                all_data.append(base_data)
            
            if all_data:
                df = pd.DataFrame(all_data)
                output = StringIO()
                df.to_csv(output, index=False, encoding='utf-8')
                return output.getvalue()
            else:
                return "No data available"
            
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return ""