from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.models.models import Queja, Usuario
from typing import List

router = APIRouter(
    prefix="/quejas",
    tags=["Quejas"]
)

@router.get("/")
def obtener_todas_quejas(db: Session = Depends(get_db)):
    """Obtiene todas las quejas (para admin) con datos del usuario"""
    quejas = db.query(Queja).order_by(Queja.fecha.desc()).all()
    
    resultado = []
    for queja in quejas:
        usuario = db.query(Usuario).filter(Usuario.id == queja.id_usuario).first()
        
        resultado.append({
            "id": queja.id,
            "id_usuario": queja.id_usuario,
            "descripcion": queja.descripcion,
            "fecha": queja.fecha.isoformat() if queja.fecha else None,
            "leida": queja.leida,
            "usuario": {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "correo": usuario.correo
            } if usuario else None
        })
    
    return resultado

@router.get("/usuario/{usuario_id}")
def obtener_quejas_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Obtiene las quejas de un usuario específico"""
    quejas = db.query(Queja).filter(
        Queja.id_usuario == usuario_id
    ).order_by(Queja.fecha.desc()).all()
    
    resultado = []
    for queja in quejas:
        usuario = db.query(Usuario).filter(Usuario.id == queja.id_usuario).first()
        
        resultado.append({
            "id": queja.id,
            "id_usuario": queja.id_usuario,
            "descripcion": queja.descripcion,
            "fecha": queja.fecha.isoformat() if queja.fecha else None,
            "leida": queja.leida,
            "usuario": {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "correo": usuario.correo
            } if usuario else None
        })
    
    return resultado

@router.post("/")
def crear_queja(
    id_usuario: str = Form(...),
    descripcion: str = Form(...),
    db: Session = Depends(get_db)
):
    """Crea una nueva queja"""
    # Convertir id_usuario a int
    try:
        id_usuario_int = int(id_usuario)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de usuario inválido")
    
    # Verificar que el usuario existe
    usuario = db.query(Usuario).filter(Usuario.id == id_usuario_int).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Validar descripción
    if len(descripcion.strip()) < 10:
        raise HTTPException(status_code=400, detail="La descripción debe tener al menos 10 caracteres")
    
    if len(descripcion) > 300:
        raise HTTPException(status_code=400, detail="La descripción no puede exceder 300 caracteres")
    
    # Crear la queja
    nueva_queja = Queja(
        id_usuario=id_usuario_int,
        descripcion=descripcion.strip(),
        leida=False
    )
    
    db.add(nueva_queja)
    db.commit()
    db.refresh(nueva_queja)
    
    return {
        "id": nueva_queja.id,
        "mensaje": "Queja enviada exitosamente",
        "fecha": nueva_queja.fecha
    }

@router.put("/{queja_id}/marcar-leida")
def marcar_queja_leida(queja_id: int, db: Session = Depends(get_db)):
    """Marca una queja como leída (para admin)"""
    queja = db.query(Queja).filter(Queja.id == queja_id).first()
    if not queja:
        raise HTTPException(status_code=404, detail="Queja no encontrada")
    
    queja.leida = True
    db.commit()
    db.refresh(queja)
    
    return {"mensaje": "Queja marcada como leída"}

@router.delete("/{queja_id}")
def eliminar_queja(queja_id: int, db: Session = Depends(get_db)):
    """Elimina una queja (para admin)"""
    queja = db.query(Queja).filter(Queja.id == queja_id).first()
    if not queja:
        raise HTTPException(status_code=404, detail="Queja no encontrada")
    
    db.delete(queja)
    db.commit()
    
    return {"mensaje": "Queja eliminada correctamente"}