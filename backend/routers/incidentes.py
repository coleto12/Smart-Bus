from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.models.models import IncidenteCarretera, Usuario
from datetime import datetime, timedelta

router = APIRouter(
    prefix="/incidentes",
    tags=["Incidentes"]
)

# Tipos de incidentes válidos
TIPOS_VALIDOS = ["reten_policia", "accidente_vial", "mucho_trafico"]

def limpiar_incidentes_antiguos(db: Session):
    """Elimina incidentes con más de 1 hora de antigüedad"""
    hora_limite = datetime.utcnow() - timedelta(hours=1)
    
    incidentes_antiguos = db.query(IncidenteCarretera).filter(
        IncidenteCarretera.fecha_reporte < hora_limite
    ).all()
    
    cantidad_eliminados = len(incidentes_antiguos)
    
    for incidente in incidentes_antiguos:
        db.delete(incidente)
    
    if cantidad_eliminados > 0:
        db.commit()
        print(f"✅ Limpieza automática: {cantidad_eliminados} incidente(s) antiguo(s) eliminado(s)")
    
    return cantidad_eliminados

@router.get("/")
def obtener_incidentes(activos_solo: bool = True, db: Session = Depends(get_db)):
    """Obtiene todos los incidentes o solo los activos"""
    # Limpiar incidentes antiguos antes de devolver la lista
    limpiar_incidentes_antiguos(db)
    
    if activos_solo:
        incidentes = db.query(IncidenteCarretera).filter(IncidenteCarretera.activo == True).all()
    else:
        incidentes = db.query(IncidenteCarretera).all()
    
    resultado = []
    for incidente in incidentes:
        # Obtener información del usuario que reportó
        usuario = None
        if incidente.id_usuario:
            usuario_obj = db.query(Usuario).filter(Usuario.id == incidente.id_usuario).first()
            if usuario_obj:
                usuario = {
                    "id": usuario_obj.id,
                    "nombre": usuario_obj.nombre
                }
        
        resultado.append({
            "id": incidente.id,
            "tipo_incidente": incidente.tipo_incidente,
            "latitud": incidente.latitud,
            "longitud": incidente.longitud,
            "descripcion": incidente.descripcion,
            "fecha_reporte": incidente.fecha_reporte.isoformat() if incidente.fecha_reporte else None,
            "activo": incidente.activo,
            "usuario": usuario
        })
    
    return resultado

@router.get("/{incidente_id}")
def obtener_incidente(incidente_id: int, db: Session = Depends(get_db)):
    """Obtiene un incidente específico"""
    incidente = db.query(IncidenteCarretera).filter(IncidenteCarretera.id == incidente_id).first()
    if not incidente:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    
    return {
        "id": incidente.id,
        "tipo_incidente": incidente.tipo_incidente,
        "latitud": incidente.latitud,
        "longitud": incidente.longitud,
        "descripcion": incidente.descripcion,
        "fecha_reporte": incidente.fecha_reporte.isoformat() if incidente.fecha_reporte else None,
        "activo": incidente.activo,
        "id_usuario": incidente.id_usuario
    }

@router.post("/")
def crear_incidente(
    tipo_incidente: str = Form(...),
    latitud: float = Form(...),
    longitud: float = Form(...),
    descripcion: str = Form(None),
    id_usuario: int = Form(None),
    db: Session = Depends(get_db)
):
    """Crea un nuevo incidente"""
    # Validar tipo de incidente
    if tipo_incidente not in TIPOS_VALIDOS:
        raise HTTPException(
            status_code=400, 
            detail=f"Tipo de incidente inválido. Debe ser uno de: {', '.join(TIPOS_VALIDOS)}"
        )
    
    # Validar coordenadas (Colombia aproximadamente)
    if not (-4.5 <= latitud <= 13.5):
        raise HTTPException(status_code=400, detail="Latitud fuera del rango de Colombia")
    
    if not (-79.0 <= longitud <= -66.8):
        raise HTTPException(status_code=400, detail="Longitud fuera del rango de Colombia")
    
    nuevo_incidente = IncidenteCarretera(
        tipo_incidente=tipo_incidente,
        latitud=latitud,
        longitud=longitud,
        descripcion=descripcion,
        id_usuario=id_usuario,
        activo=True
    )
    
    db.add(nuevo_incidente)
    db.commit()
    db.refresh(nuevo_incidente)
    
    return {
        "mensaje": "Incidente reportado exitosamente",
        "incidente": {
            "id": nuevo_incidente.id,
            "tipo_incidente": nuevo_incidente.tipo_incidente,
            "latitud": nuevo_incidente.latitud,
            "longitud": nuevo_incidente.longitud
        }
    }

@router.put("/{incidente_id}")
def actualizar_incidente(
    incidente_id: int,
    tipo_incidente: str = Form(...),
    latitud: float = Form(...),
    longitud: float = Form(...),
    descripcion: str = Form(None),
    activo: bool = Form(True),
    db: Session = Depends(get_db)
):
    """Actualiza un incidente existente"""
    incidente = db.query(IncidenteCarretera).filter(IncidenteCarretera.id == incidente_id).first()
    if not incidente:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    
    # Validar tipo de incidente
    if tipo_incidente not in TIPOS_VALIDOS:
        raise HTTPException(
            status_code=400, 
            detail=f"Tipo de incidente inválido. Debe ser uno de: {', '.join(TIPOS_VALIDOS)}"
        )
    
    incidente.tipo_incidente = tipo_incidente
    incidente.latitud = latitud
    incidente.longitud = longitud
    incidente.descripcion = descripcion
    incidente.activo = activo
    
    db.commit()
    db.refresh(incidente)
    
    return {
        "mensaje": "Incidente actualizado exitosamente",
        "incidente": incidente
    }

@router.patch("/{incidente_id}/resolver")
def resolver_incidente(incidente_id: int, db: Session = Depends(get_db)):
    """Marca un incidente como resuelto (inactivo)"""
    incidente = db.query(IncidenteCarretera).filter(IncidenteCarretera.id == incidente_id).first()
    if not incidente:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    
    incidente.activo = False
    db.commit()
    
    return {"mensaje": "Incidente marcado como resuelto"}

@router.delete("/{incidente_id}")
def eliminar_incidente(incidente_id: int, db: Session = Depends(get_db)):
    """Elimina un incidente"""
    incidente = db.query(IncidenteCarretera).filter(IncidenteCarretera.id == incidente_id).first()
    if not incidente:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    
    db.delete(incidente)
    db.commit()
    return {"mensaje": "Incidente eliminado correctamente"}

@router.get("/tipos/lista")
def obtener_tipos_incidentes():
    """Obtiene la lista de tipos de incidentes válidos"""
    return {
        "tipos": [
            {"value": "reten_policia", "label": "Retén de Policía", "emoji": "🚔"},
            {"value": "accidente_vial", "label": "Accidente Vial", "emoji": "🚗💥"},
            {"value": "mucho_trafico", "label": "Mucho Tráfico", "emoji": "🚦"}
        ]
    }