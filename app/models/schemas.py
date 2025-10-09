from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, validator
from enum import Enum

# Enums for categorization
class EstadoFormulario(str, Enum):
    PENDIENTE = "PENDIENTE"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"

class EstatusPublicacion(str, Enum):
    ACEPTADO = "ACEPTADO"
    EN_REVISION = "EN_REVISION"
    PUBLICADO = "PUBLICADO"
    RECHAZADO = "RECHAZADO"

class TipoParticipacion(str, Enum):
    ORGANIZADOR = "ORGANIZADOR"
    PARTICIPANTE = "PARTICIPANTE"
    PONENTE = "PONENTE"

class TipoMovilidad(str, Enum):
    NACIONAL = "NACIONAL"
    INTERNACIONAL = "INTERNACIONAL"

class TipoReconocimiento(str, Enum):
    GRADO = "GRADO"
    PREMIO = "PREMIO"
    DISTINCION = "DISTINCION"

# Individual data models
class CursoCapacitacionBase(BaseModel):
    nombre_curso: str
    fecha: date
    horas: int
    
    @validator('horas')
    def validate_horas(cls, v):
        if v <= 0:
            raise ValueError('Las horas deben ser mayor a 0')
        return v

class CursoCapacitacion(CursoCapacitacionBase):
    id: Optional[int] = None
    formulario_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class PublicacionBase(BaseModel):
    autores: str
    titulo: str
    evento_revista: str
    estatus: EstatusPublicacion

class Publicacion(PublicacionBase):
    id: Optional[int] = None
    formulario_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class EventoAcademicoBase(BaseModel):
    nombre_evento: str
    fecha: date
    tipo_participacion: TipoParticipacion

class EventoAcademico(EventoAcademicoBase):
    id: Optional[int] = None
    formulario_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class DisenoCurricularBase(BaseModel):
    nombre_curso: str
    descripcion: Optional[str] = None

class DisenoCurricular(DisenoCurricularBase):
    id: Optional[int] = None
    formulario_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class ExperienciaMovilidadBase(BaseModel):
    descripcion: str
    tipo: TipoMovilidad
    fecha: date

class ExperienciaMovilidad(ExperienciaMovilidadBase):
    id: Optional[int] = None
    formulario_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class ReconocimientoBase(BaseModel):
    nombre: str
    tipo: TipoReconocimiento
    fecha: date

class Reconocimiento(ReconocimientoBase):
    id: Optional[int] = None
    formulario_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class CertificacionBase(BaseModel):
    nombre: str
    fecha_obtencion: date
    fecha_vencimiento: Optional[date] = None
    
    @validator('fecha_vencimiento')
    def validate_fecha_vencimiento(cls, v, values):
        if v and 'fecha_obtencion' in values and v <= values['fecha_obtencion']:
            raise ValueError('La fecha de vencimiento debe ser posterior a la fecha de obtención')
        return v

class Certificacion(CertificacionBase):
    id: Optional[int] = None
    formulario_id: Optional[int] = None
    vigente: bool = True
    
    class Config:
        from_attributes = True

# Main form data model
class FormDataBase(BaseModel):
    nombre_completo: str
    correo_institucional: EmailStr
    año_academico: int
    trimestre: str
    cursos_capacitacion: List[CursoCapacitacionBase] = []
    publicaciones: List[PublicacionBase] = []
    eventos_academicos: List[EventoAcademicoBase] = []
    diseno_curricular: List[DisenoCurricularBase] = []
    movilidad: List[ExperienciaMovilidadBase] = []
    reconocimientos: List[ReconocimientoBase] = []
    certificaciones: List[CertificacionBase] = []
    
    @validator('nombre_completo')
    def validate_nombre_completo(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('El nombre completo debe tener al menos 3 caracteres')
        return v.strip()

class FormData(FormDataBase):
    pass

class FormularioEnvioBase(BaseModel):
    nombre_completo: str
    correo_institucional: str
    estado: EstadoFormulario = EstadoFormulario.PENDIENTE
    fecha_envio: datetime
    fecha_revision: Optional[datetime] = None
    revisado_por: Optional[str] = None

class FormularioEnvio(FormularioEnvioBase):
    id: Optional[int] = None
    
    # Related data
    cursos_capacitacion: List[CursoCapacitacion] = []
    publicaciones: List[Publicacion] = []
    eventos_academicos: List[EventoAcademico] = []
    diseno_curricular: List[DisenoCurricular] = []
    movilidad: List[ExperienciaMovilidad] = []
    reconocimientos: List[Reconocimiento] = []
    certificaciones: List[Certificacion] = []
    
    class Config:
        from_attributes = True

# Response models
class FormularioEnvioResponse(BaseModel):
    success: bool
    message: str
    formulario_id: Optional[int] = None

class FormularioListResponse(BaseModel):
    formularios: List[FormularioEnvio]
    total: int
    page: int
    page_size: int

# Admin models
class AdminAction(BaseModel):
    formulario_id: int
    accion: str  # "aprobar" or "rechazar"
    comentario: Optional[str] = None

class MetricasResponse(BaseModel):
    total_formularios: int
    formularios_pendientes: int
    formularios_aprobados: int
    formularios_rechazados: int
    total_cursos: int
    total_horas_capacitacion: int
    total_publicaciones: int
    total_eventos: int
    total_disenos_curriculares: int
    total_movilidades: int
    total_reconocimientos: int
    total_certificaciones: int