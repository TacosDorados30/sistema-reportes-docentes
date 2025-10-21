"""
Modelo para historial de formularios
Guarda versiones anteriores cuando se hacen correcciones
"""

from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, Text, ForeignKey, Enum, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.database import Base, EstadoFormularioEnum

class FormularioHistoryDB(Base):
    """Historial de versiones de formularios"""
    __tablename__ = "formularios_historial"
    
    id = Column(Integer, primary_key=True, index=True)
    formulario_id = Column(Integer, ForeignKey("formularios_envio.id"), nullable=False)
    version_numero = Column(Integer, nullable=False)
    
    # Datos del formulario en esa versión
    nombre_completo = Column(String(255), nullable=False)
    correo_institucional = Column(String(255), nullable=False)
    año_academico = Column(Integer, nullable=False)
    trimestre = Column(String(50), nullable=False)
    estado = Column(Enum(EstadoFormularioEnum), nullable=False)
    
    # Metadatos de la versión
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_modificacion = Column(DateTime, nullable=True)
    modificado_por = Column(String(255), nullable=True)
    motivo_cambio = Column(Text, nullable=True)
    
    # Actividades como JSON para simplicidad
    actividades_json = Column(JSON, nullable=True)
    
    # Relación con el formulario principal
    formulario = relationship("FormularioEnvioDB", foreign_keys=[formulario_id])
    
    def __repr__(self):
        return f"<FormularioHistory(id={self.id}, formulario_id={self.formulario_id}, version={self.version_numero})>"