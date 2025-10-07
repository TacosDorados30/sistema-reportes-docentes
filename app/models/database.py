from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

# Enums for database
class EstadoFormularioEnum(enum.Enum):
    PENDIENTE = "PENDIENTE"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"

class EstatusPublicacionEnum(enum.Enum):
    ACEPTADO = "ACEPTADO"
    EN_REVISION = "EN_REVISION"
    PUBLICADO = "PUBLICADO"
    RECHAZADO = "RECHAZADO"

class TipoParticipacionEnum(enum.Enum):
    ORGANIZADOR = "ORGANIZADOR"
    PARTICIPANTE = "PARTICIPANTE"
    PONENTE = "PONENTE"

class TipoMovilidadEnum(enum.Enum):
    NACIONAL = "NACIONAL"
    INTERNACIONAL = "INTERNACIONAL"

class TipoReconocimientoEnum(enum.Enum):
    GRADO = "GRADO"
    PREMIO = "PREMIO"
    DISTINCION = "DISTINCION"

# Main form table
class FormularioEnvioDB(Base):
    __tablename__ = "formularios_envio"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String(255), nullable=False)
    correo_institucional = Column(String(255), nullable=False)
    estado = Column(Enum(EstadoFormularioEnum), default=EstadoFormularioEnum.PENDIENTE)
    fecha_envio = Column(DateTime, default=datetime.utcnow)
    fecha_revision = Column(DateTime, nullable=True)
    revisado_por = Column(String(255), nullable=True)
    
    # Relationships
    cursos_capacitacion = relationship("CursoCapacitacionDB", back_populates="formulario", cascade="all, delete-orphan")
    publicaciones = relationship("PublicacionDB", back_populates="formulario", cascade="all, delete-orphan")
    eventos_academicos = relationship("EventoAcademicoDB", back_populates="formulario", cascade="all, delete-orphan")
    diseno_curricular = relationship("DisenoCurricularDB", back_populates="formulario", cascade="all, delete-orphan")
    movilidad = relationship("ExperienciaMovilidadDB", back_populates="formulario", cascade="all, delete-orphan")
    reconocimientos = relationship("ReconocimientoDB", back_populates="formulario", cascade="all, delete-orphan")
    certificaciones = relationship("CertificacionDB", back_populates="formulario", cascade="all, delete-orphan")

class CursoCapacitacionDB(Base):
    __tablename__ = "cursos_capacitacion"
    
    id = Column(Integer, primary_key=True, index=True)
    formulario_id = Column(Integer, ForeignKey("formularios_envio.id"))
    nombre_curso = Column(String(500), nullable=False)
    fecha = Column(Date, nullable=False)
    horas = Column(Integer, nullable=False)
    
    formulario = relationship("FormularioEnvioDB", back_populates="cursos_capacitacion")

class PublicacionDB(Base):
    __tablename__ = "publicaciones"
    
    id = Column(Integer, primary_key=True, index=True)
    formulario_id = Column(Integer, ForeignKey("formularios_envio.id"))
    autores = Column(Text, nullable=False)
    titulo = Column(Text, nullable=False)
    evento_revista = Column(String(500), nullable=False)
    estatus = Column(Enum(EstatusPublicacionEnum), nullable=False)
    
    formulario = relationship("FormularioEnvioDB", back_populates="publicaciones")

class EventoAcademicoDB(Base):
    __tablename__ = "eventos_academicos"
    
    id = Column(Integer, primary_key=True, index=True)
    formulario_id = Column(Integer, ForeignKey("formularios_envio.id"))
    nombre_evento = Column(String(500), nullable=False)
    fecha = Column(Date, nullable=False)
    tipo_participacion = Column(Enum(TipoParticipacionEnum), nullable=False)
    
    formulario = relationship("FormularioEnvioDB", back_populates="eventos_academicos")

class DisenoCurricularDB(Base):
    __tablename__ = "diseno_curricular"
    
    id = Column(Integer, primary_key=True, index=True)
    formulario_id = Column(Integer, ForeignKey("formularios_envio.id"))
    nombre_curso = Column(String(500), nullable=False)
    descripcion = Column(Text, nullable=True)
    
    formulario = relationship("FormularioEnvioDB", back_populates="diseno_curricular")

class ExperienciaMovilidadDB(Base):
    __tablename__ = "experiencias_movilidad"
    
    id = Column(Integer, primary_key=True, index=True)
    formulario_id = Column(Integer, ForeignKey("formularios_envio.id"))
    descripcion = Column(Text, nullable=False)
    tipo = Column(Enum(TipoMovilidadEnum), nullable=False)
    fecha = Column(Date, nullable=False)
    
    formulario = relationship("FormularioEnvioDB", back_populates="movilidad")

class ReconocimientoDB(Base):
    __tablename__ = "reconocimientos"
    
    id = Column(Integer, primary_key=True, index=True)
    formulario_id = Column(Integer, ForeignKey("formularios_envio.id"))
    nombre = Column(String(500), nullable=False)
    tipo = Column(Enum(TipoReconocimientoEnum), nullable=False)
    fecha = Column(Date, nullable=False)
    
    formulario = relationship("FormularioEnvioDB", back_populates="reconocimientos")

class CertificacionDB(Base):
    __tablename__ = "certificaciones"
    
    id = Column(Integer, primary_key=True, index=True)
    formulario_id = Column(Integer, ForeignKey("formularios_envio.id"))
    nombre = Column(String(500), nullable=False)
    fecha_obtencion = Column(Date, nullable=False)
    fecha_vencimiento = Column(Date, nullable=True)
    vigente = Column(Boolean, default=True)
    
    formulario = relationship("FormularioEnvioDB", back_populates="certificaciones")

# Audit log table
class AuditLogDB(Base):
    __tablename__ = "audit_log"
    
    id = Column(Integer, primary_key=True, index=True)
    formulario_id = Column(Integer, ForeignKey("formularios_envio.id"))
    accion = Column(String(100), nullable=False)  # "APROBADO", "RECHAZADO", "CREADO"
    usuario = Column(String(255), nullable=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    comentario = Column(Text, nullable=True)
    
    formulario = relationship("FormularioEnvioDB")