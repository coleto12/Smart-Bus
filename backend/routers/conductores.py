from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.models.models import Conductor, Usuario, Bus, Ruta
from backend.core.security import hash_password
from pydantic import BaseModel

router = APIRouter(
    prefix="/conductores",
    tags=["Conductores"]
)

# Modelo Pydantic para actualizar estado del bus
class EstadoBusUpdate(BaseModel):
    estado: bool

@router.get("/")
def obtener_conductores(db: Session = Depends(get_db)):
    """Obtiene todos los conductores con su información de usuario"""
    conductores = db.query(Conductor).all()
    return conductores

@router.get("/{conductor_id}")
def obtener_conductor(conductor_id: int, db: Session = Depends(get_db)):
    conductor = db.query(Conductor).filter(Conductor.id == conductor_id).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    return conductor

@router.post("/")
def crear_conductor(
    nombre: str = Form(...),
    correo: str = Form(...),
    contraseña: str = Form(...),
    licencia: str = Form(...),
    telefono: str = Form(...),
    db: Session = Depends(get_db)
):
    # Verificar si el correo ya existe
    usuario_existente = db.query(Usuario).filter(Usuario.correo == correo).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    
    # Verificar si la licencia ya existe
    conductor_existente = db.query(Conductor).filter(Conductor.licencia == licencia).first()
    if conductor_existente:
        raise HTTPException(status_code=400, detail="La licencia ya está registrada")
    
    # 1. Crear usuario con rol conductor
    nuevo_usuario = Usuario(
        nombre=nombre,
        correo=correo,
        contraseña=hash_password(contraseña),
        rol="conductor"
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    # 2. Crear conductor vinculado al usuario
    nuevo_conductor = Conductor(
        nombre=nombre,
        correo=correo,
        licencia=licencia,
        telefono=telefono,
        id_usuario=nuevo_usuario.id
    )
    db.add(nuevo_conductor)
    db.commit()
    db.refresh(nuevo_conductor)
    
    return {
        "id": nuevo_conductor.id,
        "nombre": nuevo_conductor.nombre,
        "correo": nuevo_conductor.correo,
        "licencia": nuevo_conductor.licencia,
        "telefono": nuevo_conductor.telefono,
        "mensaje": "Conductor creado exitosamente"
    }

@router.put("/{conductor_id}")
def actualizar_conductor(
    conductor_id: int,
    nombre: str = Form(...),
    correo: str = Form(...),
    licencia: str = Form(...),
    telefono: str = Form(...),
    db: Session = Depends(get_db)
):
    """Actualiza los datos de un conductor"""
    conductor = db.query(Conductor).filter(Conductor.id == conductor_id).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    
    # Actualizar conductor
    conductor.nombre = nombre
    conductor.correo = correo
    conductor.licencia = licencia
    conductor.telefono = telefono
    
    # Actualizar usuario asociado
    if conductor.usuario:
        conductor.usuario.nombre = nombre
        conductor.usuario.correo = correo
    
    db.commit()
    db.refresh(conductor)
    
    return {
        "mensaje": "Conductor actualizado exitosamente",
        "conductor": conductor
    }

@router.delete("/{conductor_id}")
def eliminar_conductor(conductor_id: int, db: Session = Depends(get_db)):
    conductor = db.query(Conductor).filter(Conductor.id == conductor_id).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    
    # Guardar id_usuario antes de eliminar el conductor
    id_usuario = conductor.id_usuario
    
    # Eliminar conductor
    db.delete(conductor)
    db.commit()
    
    # Eliminar usuario asociado
    if id_usuario:
        usuario = db.query(Usuario).filter(Usuario.id == id_usuario).first()
        if usuario:
            db.delete(usuario)
            db.commit()
    
    return {"mensaje": "Conductor y usuario eliminados correctamente"}


# ========================================
# ENDPOINTS PARA EL CONDUCTOR (MI BUS)
# ========================================

@router.get("/mi-bus/{id_usuario}")
def obtener_bus_conductor(id_usuario: int, db: Session = Depends(get_db)):
    """Obtiene el bus asignado a un conductor específico"""
    
    # 1. Buscar el conductor por id_usuario
    conductor = db.query(Conductor).filter(Conductor.id_usuario == id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    
    # 2. Buscar el bus asignado a este conductor
    bus = db.query(Bus).filter(Bus.id_conductor == conductor.id).first()
    if not bus:
        raise HTTPException(status_code=404, detail="No tienes un bus asignado actualmente")
    
    # 3. Obtener información de la ruta si existe
    ruta_info = None
    if bus.id_ruta:
        ruta = db.query(Ruta).filter(Ruta.id == bus.id_ruta).first()
        if ruta:
            origen_nombre = ruta.parada_origen.nombre if ruta.parada_origen else "Sin origen"
            destino_nombre = ruta.parada_destino.nombre if ruta.parada_destino else "Sin destino"
            
            ruta_info = {
                "id": ruta.id,
                "nombre": ruta.nombre,
                "origen": origen_nombre,
                "destino": destino_nombre,
                "tiempo_estimado": ruta.tiempo_estimado
            }
    
    return {
        "id": bus.id,
        "placa": bus.placa,
        "modelo": bus.modelo,
        "capacidad": bus.capacidad,
        "estado": bus.estado,
        "hora_inicio": str(bus.hora_inicio) if bus.hora_inicio else None,
        "hora_llegada": str(bus.hora_llegada) if bus.hora_llegada else None,
        "conductor": {
            "id": conductor.id,
            "nombre": conductor.nombre,
            "licencia": conductor.licencia,
            "telefono": conductor.telefono
        },
        "ruta": ruta_info
    }

@router.put("/mi-bus/{id_usuario}/estado")
def actualizar_estado_bus(
    id_usuario: int, 
    estado_update: EstadoBusUpdate,
    db: Session = Depends(get_db)
):
    """Permite al conductor actualizar solo el estado de su bus"""
    
    # 1. Verificar que el conductor existe
    conductor = db.query(Conductor).filter(Conductor.id_usuario == id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    
    # 2. Obtener el bus del conductor
    bus = db.query(Bus).filter(Bus.id_conductor == conductor.id).first()
    if not bus:
        raise HTTPException(status_code=404, detail="No tienes un bus asignado")
    
    # 3. Actualizar solo el estado
    bus.estado = estado_update.estado
    db.commit()
    db.refresh(bus)
    
    estado_texto = "ACTIVO" if bus.estado else "INACTIVO"
    
    return {
        "mensaje": f"Estado del bus actualizado a {estado_texto}",
        "bus": {
            "id": bus.id,
            "placa": bus.placa,
            "estado": bus.estado
        }
    }