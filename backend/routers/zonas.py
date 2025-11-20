from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.models.models import Zona

router = APIRouter(
    prefix="/zonas",
    tags=["Zonas"]
)

# Obtener todas las zonas
@router.get("/")
def obtener_zonas(db: Session = Depends(get_db)):
    return db.query(Zona).all()

# Crear una zona
@router.post("/")
def crear_zona(
    nombre: str = Form(...),
    db: Session = Depends(get_db)
):
    existente = db.query(Zona).filter(Zona.nombre == nombre).first()
    if existente:
        raise HTTPException(status_code=400, detail="La zona ya existe")

    nueva_zona = Zona(nombre=nombre)
    db.add(nueva_zona)
    db.commit()
    db.refresh(nueva_zona)
    
    return {
        "id": nueva_zona.id,
        "nombre": nueva_zona.nombre,
        "mensaje": "Zona creada exitosamente"
    }

# Obtener una zona por ID
@router.get("/{zona_id}")
def obtener_zona(zona_id: int, db: Session = Depends(get_db)):
    zona = db.query(Zona).filter(Zona.id == zona_id).first()
    if not zona:
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    return zona

# Actualizar una zona
@router.put("/{zona_id}")
def actualizar_zona(
    zona_id: int,
    nombre: str = Form(...),
    db: Session = Depends(get_db)
):
    zona = db.query(Zona).filter(Zona.id == zona_id).first()
    if not zona:
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    
    # Verificar que el nuevo nombre no exista
    zona_existente = db.query(Zona).filter(
        Zona.nombre == nombre,
        Zona.id != zona_id
    ).first()
    if zona_existente:
        raise HTTPException(status_code=400, detail="Ya existe una zona con ese nombre")
    
    zona.nombre = nombre
    db.commit()
    db.refresh(zona)
    
    return {
        "id": zona.id,
        "nombre": zona.nombre,
        "mensaje": "Zona actualizada exitosamente"
    }

# Eliminar una zona
@router.delete("/{zona_id}")
def eliminar_zona(zona_id: int, db: Session = Depends(get_db)):
    zona = db.query(Zona).filter(Zona.id == zona_id).first()
    if not zona:
        raise HTTPException(status_code=404, detail="Zona no encontrada")

    db.delete(zona)
    db.commit()
    return {"mensaje": "Zona eliminada correctamente"}