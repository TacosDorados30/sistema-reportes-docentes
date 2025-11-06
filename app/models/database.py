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
    año_academico = Column(Integer, nullable=False)
    trimestre = Column(String(50), nullable=False)
    estado = Column(Enum(EstadoFormularioEnum),
                    default=EstadoFormularioEnum.PENDIENTE)
    fecha_envio = Column(DateTime, default=datetime.utcnow)
    fecha_revision = Column(DateTime, nullable=True)
    revisado_por = Column(String(255), nullable=True)

    # Campos para sistema de versiones
    formulario_original_id = Column(Integer, ForeignKey(
        "formularios_envio.id"), nullable=True)
    version = Column(Integer, default=1)
    token_correccion = Column(String(255), nullable=True, unique=True)
    es_version_activa = Column(Boolean, default=True)

    # Relationships
    cursos_capacitacion = relationship(
        "CursoCapacitacionDB", back_populates="formulario", cascade="all, delete-orphan")
    publicaciones = relationship(
        "PublicacionDB", back_populates="formulario", cascade="all, delete-orphan")
    eventos_academicos = relationship(
        "EventoAcademicoDB", back_populates="formulario", cascade="all, delete-orphan")
    diseno_curricular = relationship(
        "DisenoCurricularDB", back_populates="formulario", cascade="all, delete-orphan")
    movilidad = relationship(
        "ExperienciaMovilidadDB", back_populates="formulario", cascade="all, delete-orphan")
    reconocimientos = relationship(
        "ReconocimientoDB", back_populates="formulario", cascade="all, delete-orphan")
    certificaciones = relationship(
        "CertificacionDB", back_populates="formulario", cascade="all, delete-orphan")
    otras_actividades = relationship(
        "OtraActividadAcademicaDB", back_populates="formulario", cascade="all, delete-orphan")


class CursoCapacitacionDB(Base):
    __tablename__ = "cursos_capacitacion"

    id = Column(Integer, primary_key=True, index=True)
    formulario_id = Column(Integer, ForeignKey("formularios_envio.id"))
    nombre_curso = Column(String(500), nullable=False)
    fecha = Column(Date, nullable=False)
    horas = Column(Integer, nullable=False)

    formulario = relationship(
        "FormularioEnvioDB", back_populates="cursos_capacitacion")


class PublicacionDB(Base):
    __tablename__ = "publicaciones"

    id = Column(Integer, primary_key=True, index=True)
    formulario_id = Column(Integer, ForeignKey("formularios_envio.id"))
    autores = Column(Text, nullable=False)
    titulo = Column(Text, nullable=False)
    evento_revista = Column(String(500), nullable=False)
    estatus = Column(Enum(EstatusPublicacionEnum), nullable=False)

    formulario = relationship(
        "FormularioEnvioDB", back_populates="publicaciones")


class EventoAcademicoDB(Base):
    __tablename__ = "eventos_academicos"

    id = Column(Integer, primary_key=True, index=True)
    formulario_id = Column(Integer, ForeignKey("formularios_envio.id"))
    nombre_evento = Column(String(500), nullable=False)
    fecha = Column(Date, nullable=False)
    tipo_participacion = Column(Enum(TipoParticipacionEnum), nullable=False)

    formulario = relationship(
        "FormularioEnvioDB", back_populates="eventos_academicos")


class DisenoCurricularDB(Base):
    __tablename__ = "diseno_curricular"

    id = Column(Integer, primary_key=True, index=True)
    formulario_id = Column(Integer, ForeignKey("formularios_envio.id"))
    nombre_curso = Column(String(500), nullable=False)
    descripcion = Column(Text, nullable=True)

    formulario = relationship(
        "FormularioEnvioDB", back_populates="diseno_curricular")


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

    formulario = relationship(
        "FormularioEnvioDB", back_populates="reconocimientos")


class CertificacionDB(Base):
    __tablename__ = "certificaciones"

    id = Column(Integer, primary_key=True, index=True)
    formulario_id = Column(Integer, ForeignKey("formularios_envio.id"))
    nombre = Column(String(500), nullable=False)
    fecha_obtencion = Column(Date, nullable=False)

    formulario = relationship(
        "FormularioEnvioDB", back_populates="certificaciones")

# Authorized teachers table


class MaestroAutorizadoDB(Base):
    __tablename__ = "maestros_autorizados"

    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String(255), nullable=False)
    correo_institucional = Column(String(255), nullable=False, unique=True)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Email notifications tracking table


class NotificacionEmailDB(Base):
    __tablename__ = "notificaciones_email"

    id = Column(Integer, primary_key=True, index=True)
    maestro_id = Column(Integer, ForeignKey("maestros_autorizados.id"))
    # "RECORDATORIO", "URGENTE", "FINAL"
    tipo_notificacion = Column(String(100), nullable=False)
    asunto = Column(String(500), nullable=False)
    mensaje = Column(Text, nullable=False)
    fecha_envio = Column(DateTime, default=datetime.utcnow)
    # "ENVIADO", "ERROR", "PENDIENTE"
    estado = Column(String(50), default="ENVIADO")
    periodo_academico = Column(String(100), nullable=True)  # Ej: "2024-Q1"

    # Relationship
    maestro = relationship("MaestroAutorizadoDB")

# Other academic activities table (generic/flexible)


class OtraActividadAcademicaDB(Base):
    __tablename__ = "otras_actividades_academicas"

    id = Column(Integer, primary_key=True, index=True)
    formulario_id = Column(Integer, ForeignKey("formularios_envio.id"))
    # Ej: "ASESORIA Y TITULACION", "SOLICITUDES ATENDIDAS", etc.
    categoria = Column(String(255), nullable=False)
    # Título o nombre de la actividad
    titulo = Column(String(500), nullable=False)
    descripcion = Column(Text, nullable=True)  # Descripción detallada
    fecha = Column(Date, nullable=True)  # Fecha opcional
    # Para números (solicitudes atendidas, etc.)
    cantidad = Column(Integer, nullable=True)
    observaciones = Column(Text, nullable=True)  # Campo adicional para notas

    formulario = relationship(
        "FormularioEnvioDB", back_populates="otras_actividades")

# Audit log table


class AuditLogDB(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    formulario_id = Column(Integer, ForeignKey("formularios_envio.id"))
    # "APROBADO", "RECHAZADO", "CREADO"
    accion = Column(String(100), nullable=False)
    usuario = Column(String(255), nullable=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    comentario = Column(Text, nullable=True)

    formulario = relationship("FormularioEnvioDB")
