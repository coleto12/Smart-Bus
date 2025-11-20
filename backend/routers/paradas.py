from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.models.models import Parada

router = APIRouter(
    prefix="/paradas",
    tags=["Paradas"]
)

@router.get("/")
def obtener_paradas(db: Session = Depends(get_db)):
    """Obtiene todas las paradas"""
    return db.query(Parada).all()

@router.get("/{parada_id}")
def obtener_parada(parada_id: int, db: Session = Depends(get_db)):
    parada = db.query(Parada).filter(Parada.id == parada_id).first()
    if not parada:
        raise HTTPException(status_code=404, detail="Parada no encontrada")
    return parada

@router.post("/")
def crear_parada(
    nombre: str = Form(...),
    latitud: float = Form(...),
    longitud: float = Form(...),
    db: Session = Depends(get_db)
):
    # Verificar si ya existe una parada con el mismo nombre
    existente = db.query(Parada).filter(Parada.nombre == nombre).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe una parada con ese nombre")
    
    # Validar coordenadas
    if not (-90 <= latitud <= 90):
        raise HTTPException(status_code=400, detail="Latitud debe estar entre -90 y 90")
    if not (-180 <= longitud <= 180):
        raise HTTPException(status_code=400, detail="Longitud debe estar entre -180 y 180")
    
    nueva_parada = Parada(
        nombre=nombre,
        latitud=latitud,
        longitud=longitud
    )
    db.add(nueva_parada)
    db.commit()
    db.refresh(nueva_parada)
    
    return {
        "id": nueva_parada.id,
        "nombre": nueva_parada.nombre,
        "latitud": nueva_parada.latitud,
        "longitud": nueva_parada.longitud,
        "mensaje": "Parada creada exitosamente"
    }

@router.put("/{parada_id}")
def actualizar_parada(
    parada_id: int,
    nombre: str = Form(...),
    latitud: float = Form(...),
    longitud: float = Form(...),
    db: Session = Depends(get_db)
):
    parada = db.query(Parada).filter(Parada.id == parada_id).first()
    if not parada:
        raise HTTPException(status_code=404, detail="Parada no encontrada")
    
    # Verificar que el nuevo nombre no exista en otra parada
    nombre_existente = db.query(Parada).filter(
        Parada.nombre == nombre,
        Parada.id != parada_id
    ).first()
    if nombre_existente:
        raise HTTPException(status_code=400, detail="Ya existe una parada con ese nombre")
    
    # Validar coordenadas
    if not (-90 <= latitud <= 90):
        raise HTTPException(status_code=400, detail="Latitud debe estar entre -90 y 90")
    if not (-180 <= longitud <= 180):
        raise HTTPException(status_code=400, detail="Longitud debe estar entre -180 y 180")
    
    parada.nombre = nombre
    parada.latitud = latitud
    parada.longitud = longitud
    
    db.commit()
    db.refresh(parada)
    
    return {
        "mensaje": "Parada actualizada exitosamente",
        "parada": parada
    }

@router.delete("/{parada_id}")
def eliminar_parada(parada_id: int, db: Session = Depends(get_db)):
    parada = db.query(Parada).filter(Parada.id == parada_id).first()
    if not parada:
        raise HTTPException(status_code=404, detail="Parada no encontrada")
    
    db.delete(parada)
    db.commit()
    return {"mensaje": "Parada eliminada correctamente"}