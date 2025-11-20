from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.models.models import UbicacionConductor, Conductor, Bus
from datetime import datetime

router = APIRouter(
    prefix="/ubicaciones",
    tags=["Ubicaciones"]
)


@router.get("/mi-ubicacion/{id_usuario}")
def obtener_mi_ubicacion(id_usuario: int, db: Session = Depends(get_db)):
    """Obtiene la ubicación actual del conductor por id_usuario"""
    
    # Buscar al conductor por id_usuario
    conductor = db.query(Conductor).filter(Conductor.id_usuario == id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    
    # Buscar la ubicación del conductor
    ubicacion = db.query(UbicacionConductor).filter(
        UbicacionConductor.id_conductor == conductor.id
    ).first()
    
    if not ubicacion:
        raise HTTPException(status_code=404, detail="No hay ubicación registrada")
    
    return {
        "id": ubicacion.id,
        "id_conductor": ubicacion.id_conductor,
        "latitud": ubicacion.latitud,
        "longitud": ubicacion.longitud,
        "activo": ubicacion.activo,
        "ultima_actualizacion": ubicacion.ultima_actualizacion
    }


@router.post("/activar")
def activar_ubicacion(
    id_usuario: int = Form(...),  # ← CAMBIADO: ahora recibe id_usuario
    latitud: float = Form(...),
    longitud: float = Form(...),
    db: Session = Depends(get_db)
):
    """Activa la ubicación en tiempo real del conductor"""
    
    # Buscar al conductor por id_usuario
    conductor = db.query(Conductor).filter(Conductor.id_usuario == id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    
    # Buscar si ya existe una ubicación registrada
    ubicacion = db.query(UbicacionConductor).filter(
        UbicacionConductor.id_conductor == conductor.id
    ).first()
    
    if ubicacion:
        # Actualizar ubicación existente
        ubicacion.latitud = latitud
        ubicacion.longitud = longitud
        ubicacion.activo = True
        ubicacion.ultima_actualizacion = datetime.utcnow()
    else:
        # Crear nueva ubicación
        ubicacion = UbicacionConductor(
            id_conductor=conductor.id,
            latitud=latitud,
            longitud=longitud,
            activo=True
        )
        db.add(ubicacion)
    
    db.commit()
    db.refresh(ubicacion)
    
    return {
        "mensaje": "Ubicación activada correctamente",
        "id": ubicacion.id,
        "latitud": ubicacion.latitud,
        "longitud": ubicacion.longitud,
        "activo": ubicacion.activo
    }


@router.post("/actualizar")
def actualizar_ubicacion(
    id_usuario: int = Form(...),  # ← CAMBIADO: ahora recibe id_usuario
    latitud: float = Form(...),
    longitud: float = Form(...),
    db: Session = Depends(get_db)
):
    """Actualiza la ubicación en tiempo real del conductor"""
    
    # Buscar al conductor por id_usuario
    conductor = db.query(Conductor).filter(Conductor.id_usuario == id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    
    # Buscar la ubicación del conductor
    ubicacion = db.query(UbicacionConductor).filter(
        UbicacionConductor.id_conductor == conductor.id
    ).first()
    
    if not ubicacion:
        raise HTTPException(status_code=404, detail="No hay ubicación registrada. Actívala primero.")
    
    # Actualizar solo si está activa
    if ubicacion.activo:
        ubicacion.latitud = latitud
        ubicacion.longitud = longitud
        ubicacion.ultima_actualizacion = datetime.utcnow()
        db.commit()
        db.refresh(ubicacion)
        
        return {
            "mensaje": "Ubicación actualizada correctamente",
            "latitud": ubicacion.latitud,
            "longitud": ubicacion.longitud,
            "ultima_actualizacion": ubicacion.ultima_actualizacion
        }
    else:
        raise HTTPException(status_code=400, detail="La ubicación no está activa")


@router.post("/desactivar/{id_usuario}")  # ← CAMBIADO: ahora recibe id_usuario
def desactivar_ubicacion(id_usuario: int, db: Session = Depends(get_db)):
    """Desactiva el compartir ubicación en tiempo real"""
    
    # Buscar al conductor por id_usuario
    conductor = db.query(Conductor).filter(Conductor.id_usuario == id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    
    # Buscar la ubicación del conductor
    ubicacion = db.query(UbicacionConductor).filter(
        UbicacionConductor.id_conductor == conductor.id
    ).first()
    
    if not ubicacion:
        raise HTTPException(status_code=404, detail="No hay ubicación registrada")
    
    # Desactivar
    ubicacion.activo = False
    db.commit()
    db.refresh(ubicacion)
    
    return {
        "mensaje": "Ubicación desactivada correctamente",
        "activo": ubicacion.activo
    }


@router.get("/conductor/{id_conductor}")
def obtener_ubicacion_conductor(id_conductor: int, db: Session = Depends(get_db)):
    """Obtiene la ubicación de un conductor específico (para pasajeros)"""
    
    # Verificar que el conductor existe
    conductor = db.query(Conductor).filter(Conductor.id == id_conductor).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    
    # Buscar la ubicación del conductor
    ubicacion = db.query(UbicacionConductor).filter(
        UbicacionConductor.id_conductor == id_conductor
    ).first()
    
    if not ubicacion or not ubicacion.activo:
        raise HTTPException(status_code=404, detail="Ubicación no disponible")
    
    return {
        "id_conductor": ubicacion.id_conductor,
        "latitud": ubicacion.latitud,
        "longitud": ubicacion.longitud,
        "ultima_actualizacion": ubicacion.ultima_actualizacion
    }


@router.get("/todos-activos")
def obtener_todas_ubicaciones_activas(db: Session = Depends(get_db)):
    """Obtiene todas las ubicaciones activas de conductores (para el mapa de pasajeros)"""
    
    ubicaciones = db.query(UbicacionConductor).filter(
        UbicacionConductor.activo == True
    ).all()
    
    resultado = []
    for ubicacion in ubicaciones:
        conductor = db.query(Conductor).filter(
            Conductor.id == ubicacion.id_conductor
        ).first()
        
        if conductor:
            resultado.append({
                "id_conductor": ubicacion.id_conductor,
                "nombre_conductor": conductor.nombre,
                "latitud": ubicacion.latitud,
                "longitud": ubicacion.longitud,
                "ultima_actualizacion": ubicacion.ultima_actualizacion
            })
    
    return resultado


@router.get("/buses-activos")
def obtener_buses_activos(db: Session = Depends(get_db)):
    """Obtiene todos los buses con ubicación activa junto con su información completa"""
    
    ubicaciones_activas = db.query(UbicacionConductor).filter(
        UbicacionConductor.activo == True
    ).all()
    
    resultado = []
    for ubicacion in ubicaciones_activas:
        # Obtener información del conductor
        conductor = db.query(Conductor).filter(
            Conductor.id == ubicacion.id_conductor
        ).first()
        
        if not conductor:
            continue
            
        # Obtener información del bus del conductor
        bus = db.query(Bus).filter(
            Bus.id_conductor == conductor.id
        ).first()
        
        if not bus:
            continue
        
        resultado.append({
            "ubicacion": {
                "latitud": ubicacion.latitud,
                "longitud": ubicacion.longitud,
                "ultima_actualizacion": ubicacion.ultima_actualizacion.isoformat()
            },
            "conductor": {
                "id": conductor.id,
                "nombre": conductor.nombre,
                "telefono": conductor.telefono
            },
            "bus": {
                "id": bus.id,
                "placa": bus.placa,
                "modelo": bus.modelo,
                "capacidad": bus.capacidad,
                "estado": bus.estado
            }
        })
    
    return resultado