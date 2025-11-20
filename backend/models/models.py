from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float, Time  # ← Agregar Time aquí
from sqlalchemy.orm import relationship
from datetime import datetime  # ← Solo datetime, NO time

from backend.database.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    correo = Column(String, unique=True, index=True, nullable=False)
    contraseña = Column(String, nullable=False)
    rol = Column(String, nullable=False)

    quejas = relationship("Queja", back_populates="usuario")



class Ruta(Base):
    __tablename__ = "rutas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    tiempo_estimado = Column(Integer, nullable=False)
    id_origen = Column(Integer, ForeignKey("paradas.id"))
    id_destino = Column(Integer, ForeignKey("paradas.id"))
    paradas_orden = Column(String(500))

    buses = relationship("Bus", back_populates="ruta")
    parada_origen = relationship("Parada", foreign_keys=[id_origen])
    parada_destino = relationship("Parada", foreign_keys=[id_destino])


class Conductor(Base):
    __tablename__ = "conductores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    licencia = Column(String(100), unique=True, nullable=False)
    telefono = Column(String(20), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    usuario = relationship("Usuario", backref="conductor")
    buses = relationship("Bus", back_populates="conductor")


class Bus(Base):
    __tablename__ = "buses"

    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String(20), unique=True, nullable=False)
    modelo = Column(String(100), nullable=False)
    capacidad = Column(Integer, nullable=False)
    estado = Column(Boolean, default=True)
    hora_inicio = Column(Time, nullable=True)  # ← Time con mayúscula (de sqlalchemy)
    hora_llegada = Column(Time, nullable=True)  # ← Time con mayúscula (de sqlalchemy)

    id_conductor = Column(Integer, ForeignKey("conductores.id"))
    id_ruta = Column(Integer, ForeignKey("rutas.id"))

    conductor = relationship("Conductor", back_populates="buses")
    ruta = relationship("Ruta", back_populates="buses")

    
class Queja(Base):
    __tablename__ = "quejas"

    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"))
    descripcion = Column(String(300), nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    leida = Column(Boolean, default=False)

    usuario = relationship("Usuario", back_populates="quejas")


class Parada(Base):
    __tablename__ = "paradas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)

class IncidenteCarretera(Base):
    __tablename__ = "incidentes_carretera"

    id = Column(Integer, primary_key=True, index=True)
    tipo_incidente = Column(String(50), nullable=False)  # "reten_policia", "accidente_vial", "mucho_trafico"
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    descripcion = Column(String(300), nullable=True)  # Opcional: para dar más detalles
    fecha_reporte = Column(DateTime, default=datetime.utcnow)
    activo = Column(Boolean, default=True)  # Para poder marcar incidentes como resueltos
    id_usuario = Column(Integer, ForeignKey("usuarios.id"))  # Quién reportó el incidente
    
    usuario = relationship("Usuario", backref="incidentes")

class UbicacionConductor(Base):
    __tablename__ = "ubicaciones_conductores"

    id = Column(Integer, primary_key=True, index=True)
    id_conductor = Column(Integer, ForeignKey("conductores.id"), unique=True, nullable=False)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    activo = Column(Boolean, default=True)  # Si está compartiendo ubicación
    ultima_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    conductor = relationship("Conductor", backref="ubicacion_actual")