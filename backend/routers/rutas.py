from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.models.models import Ruta, Bus, Parada

router = APIRouter(
    prefix="/rutas",
    tags=["Rutas"]
)

@router.get("/")
def obtener_rutas(db: Session = Depends(get_db)):
    """Obtiene todas las rutas con sus paradas"""
    rutas = db.query(Ruta).all()
    
    resultado = []
    for ruta in rutas:
        # Obtener nombres desde las relaciones
        origen_nombre = ruta.parada_origen.nombre if ruta.parada_origen else "Sin origen"
        destino_nombre = ruta.parada_destino.nombre if ruta.parada_destino else "Sin destino"
        
        # Obtener paradas en orden
        paradas = []
        if ruta.paradas_orden:
            parada_ids = [int(id.strip()) for id in ruta.paradas_orden.split(',')]
            for parada_id in parada_ids:
                parada = db.query(Parada).filter(Parada.id == parada_id).first()
                if parada:
                    paradas.append({
                        "id": parada.id,
                        "nombre": parada.nombre,
                        "latitud": parada.latitud,
                        "longitud": parada.longitud
                    })
        
        # Obtener bus asignado
        bus = None
        if ruta.buses:
            bus_obj = ruta.buses[0]
            bus = {
                "id": bus_obj.id,
                "placa": bus_obj.placa,
                "modelo": bus_obj.modelo
            }
        
        resultado.append({
            "id": ruta.id,
            "nombre": ruta.nombre,
            "origen": origen_nombre,
            "destino": destino_nombre,
            "tiempo_estimado": ruta.tiempo_estimado,
            "paradas": paradas,
            "bus": bus,
            "id_origen": ruta.id_origen,
            "id_destino": ruta.id_destino,
            "paradas_orden": ruta.paradas_orden
        })
    
    return resultado

@router.get("/paradas/todas")
def obtener_todas_paradas(db: Session = Depends(get_db)):
    """Obtiene todas las paradas disponibles"""
    return db.query(Parada).all()

@router.get("/{ruta_id}")
def obtener_ruta(ruta_id: int, db: Session = Depends(get_db)):
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    
    # Obtener nombres desde las relaciones
    origen_nombre = ruta.parada_origen.nombre if ruta.parada_origen else "Sin origen"
    destino_nombre = ruta.parada_destino.nombre if ruta.parada_destino else "Sin destino"
    
    # Obtener paradas en orden
    paradas = []
    if ruta.paradas_orden:
        parada_ids = [int(id.strip()) for id in ruta.paradas_orden.split(',')]
        for parada_id in parada_ids:
            parada = db.query(Parada).filter(Parada.id == parada_id).first()
            if parada:
                paradas.append({
                    "id": parada.id,
                    "nombre": parada.nombre,
                    "latitud": parada.latitud,
                    "longitud": parada.longitud
                })
    
    return {
        "id": ruta.id,
        "nombre": ruta.nombre,
        "origen": origen_nombre,
        "destino": destino_nombre,
        "tiempo_estimado": ruta.tiempo_estimado,
        "id_origen": ruta.id_origen,
        "id_destino": ruta.id_destino,
        "paradas_orden": ruta.paradas_orden,
        "paradas": paradas
    }

@router.post("/")
def crear_ruta(
    nombre: str = Form(...),
    id_origen: int = Form(...),
    id_destino: int = Form(...),
    tiempo_estimado: int = Form(...),
    paradas_orden: str = Form(...),
    id_bus: int = Form(None),
    db: Session = Depends(get_db)
):
    # Validar que origen y destino existan
    parada_origen = db.query(Parada).filter(Parada.id == id_origen).first()
    parada_destino = db.query(Parada).filter(Parada.id == id_destino).first()
    
    if not parada_origen:
        raise HTTPException(status_code=404, detail="Parada de origen no encontrada")
    if not parada_destino:
        raise HTTPException(status_code=404, detail="Parada de destino no encontrada")
    
    # Validar paradas_orden
    parada_ids = [int(id.strip()) for id in paradas_orden.split(',')]
    
    if parada_ids[0] != id_origen:
        raise HTTPException(
            status_code=400,
            detail=f"La primera parada debe ser el origen ({parada_origen.nombre})"
        )
    
    if parada_ids[-1] != id_destino:
        raise HTTPException(
            status_code=400,
            detail=f"La última parada debe ser el destino ({parada_destino.nombre})"
        )
    
    nueva_ruta = Ruta(
        nombre=nombre,
        tiempo_estimado=tiempo_estimado,
        id_origen=id_origen,
        id_destino=id_destino,
        paradas_orden=paradas_orden
    )
    
    db.add(nueva_ruta)
    db.commit()
    db.refresh(nueva_ruta)
    
    # Asignar bus si se proporcionó
    if id_bus:
        bus = db.query(Bus).filter(Bus.id == id_bus).first()
        if bus:
            bus.id_ruta = nueva_ruta.id
            db.commit()
    
    return {
        "mensaje": "Ruta creada exitosamente",
        "ruta": nueva_ruta
    }

@router.put("/{ruta_id}")
def actualizar_ruta(
    ruta_id: int,
    nombre: str = Form(...),
    id_origen: int = Form(...),
    id_destino: int = Form(...),
    tiempo_estimado: int = Form(...),
    paradas_orden: str = Form(...),
    id_bus: int = Form(None),
    db: Session = Depends(get_db)
):
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    
    # Validar paradas
    parada_origen = db.query(Parada).filter(Parada.id == id_origen).first()
    parada_destino = db.query(Parada).filter(Parada.id == id_destino).first()
    
    if not parada_origen or not parada_destino:
        raise HTTPException(status_code=404, detail="Parada no encontrada")
    
    # Validar orden
    parada_ids = [int(id.strip()) for id in paradas_orden.split(',')]
    
    if parada_ids[0] != id_origen:
        raise HTTPException(
            status_code=400,
            detail=f"La primera parada debe ser el origen ({parada_origen.nombre})"
        )
    
    if parada_ids[-1] != id_destino:
        raise HTTPException(
            status_code=400,
            detail=f"La última parada debe ser el destino ({parada_destino.nombre})"
        )
    
    ruta.nombre = nombre
    ruta.tiempo_estimado = tiempo_estimado
    ruta.id_origen = id_origen
    ruta.id_destino = id_destino
    ruta.paradas_orden = paradas_orden
    
    # Actualizar bus asignado
    if id_bus:
        bus = db.query(Bus).filter(Bus.id == id_bus).first()
        if bus:
            # Desasignar ruta anterior del bus
            buses_antiguos = db.query(Bus).filter(Bus.id_ruta == ruta_id).all()
            for b in buses_antiguos:
                b.id_ruta = None
            
            bus.id_ruta = ruta_id
    
    db.commit()
    db.refresh(ruta)
    
    return {
        "mensaje": "Ruta actualizada exitosamente",
        "ruta": ruta
    }

@router.delete("/{ruta_id}")
def eliminar_ruta(ruta_id: int, db: Session = Depends(get_db)):
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    
    # Desasignar buses
    buses = db.query(Bus).filter(Bus.id_ruta == ruta_id).all()
    for bus in buses:
        bus.id_ruta = None
    
    db.delete(ruta)
    db.commit()
    return {"mensaje": "Ruta eliminada correctamente"}