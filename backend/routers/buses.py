from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.models.models import Bus, Conductor, Ruta, Parada
from datetime import time

router = APIRouter(
    prefix="/buses",
    tags=["Buses"]
)

@router.get("/")
def obtener_buses(db: Session = Depends(get_db)):
    buses = db.query(Bus).all()
    resultado = []
    
    for bus in buses:
        resultado.append({
            "id": bus.id,
            "placa": bus.placa,
            "modelo": bus.modelo,
            "capacidad": bus.capacidad,
            "estado": bus.estado,
            "hora_inicio": str(bus.hora_inicio) if bus.hora_inicio else None,
            "hora_llegada": str(bus.hora_llegada) if bus.hora_llegada else None,
            "id_conductor": bus.id_conductor,
            "id_ruta": bus.id_ruta
        })
    
    return resultado

@router.get("/activos")
def obtener_buses_activos(db: Session = Depends(get_db)):
    """Obtiene solo los buses que están activos (estado=True)"""
    buses = db.query(Bus).filter(Bus.estado == True).all()
    resultado = []
    
    for bus in buses:
        # Obtener conductor
        conductor = None
        if bus.id_conductor:
            conductor_obj = db.query(Conductor).filter(Conductor.id == bus.id_conductor).first()
            if conductor_obj:
                conductor = {
                    "id": conductor_obj.id,
                    "nombre": conductor_obj.nombre,
                    "licencia": conductor_obj.licencia
                }
        
        # Obtener ruta
        ruta = None
        if bus.id_ruta:
            ruta_obj = db.query(Ruta).filter(Ruta.id == bus.id_ruta).first()
            if ruta_obj:
                origen_nombre = ruta_obj.parada_origen.nombre if ruta_obj.parada_origen else "Sin origen"
                destino_nombre = ruta_obj.parada_destino.nombre if ruta_obj.parada_destino else "Sin destino"
                
                ruta = {
                    "id": ruta_obj.id,
                    "nombre": ruta_obj.nombre,
                    "origen": origen_nombre,
                    "destino": destino_nombre
                }
        
        resultado.append({
            "id": bus.id,
            "placa": bus.placa,
            "modelo": bus.modelo,
            "capacidad": bus.capacidad,
            "estado": bus.estado,
            "hora_inicio": str(bus.hora_inicio) if bus.hora_inicio else None,
            "hora_llegada": str(bus.hora_llegada) if bus.hora_llegada else None,
            "conductor": conductor,
            "ruta": ruta
        })
    
    return resultado

@router.get("/{bus_id}")
def obtener_bus(bus_id: int, db: Session = Depends(get_db)):
    bus = db.query(Bus).filter(Bus.id == bus_id).first()
    if not bus:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    
    return {
        "id": bus.id,
        "placa": bus.placa,
        "modelo": bus.modelo,
        "capacidad": bus.capacidad,
        "estado": bus.estado,
        "hora_inicio": str(bus.hora_inicio) if bus.hora_inicio else None,
        "hora_llegada": str(bus.hora_llegada) if bus.hora_llegada else None,
        "id_conductor": bus.id_conductor,
        "id_ruta": bus.id_ruta
    }

@router.post("/")
def crear_bus(
    placa: str = Form(...),
    modelo: str = Form(...),
    capacidad: int = Form(...),
    hora_inicio: str = Form(None),
    hora_llegada: str = Form(None),
    id_conductor: int = Form(None),
    id_ruta: int = Form(None),
    db: Session = Depends(get_db)
):
    # Validar placa única
    bus_existente = db.query(Bus).filter(Bus.placa == placa).first()
    if bus_existente:
        raise HTTPException(status_code=400, detail="La placa ya está registrada")
    
    # Convertir strings de hora a objetos time
    hora_inicio_obj = None
    hora_llegada_obj = None
    
    if hora_inicio:
        try:
            h, m = map(int, hora_inicio.split(':'))
            hora_inicio_obj = time(h, m)
        except:
            raise HTTPException(status_code=400, detail="Formato de hora inicio inválido (usa HH:MM)")
    
    if hora_llegada:
        try:
            h, m = map(int, hora_llegada.split(':'))
            hora_llegada_obj = time(h, m)
        except:
            raise HTTPException(status_code=400, detail="Formato de hora llegada inválido (usa HH:MM)")
    
    nuevo_bus = Bus(
        placa=placa,
        modelo=modelo,
        capacidad=capacidad,
        estado=True,
        hora_inicio=hora_inicio_obj,
        hora_llegada=hora_llegada_obj,
        id_conductor=id_conductor,
        id_ruta=id_ruta
    )
    
    db.add(nuevo_bus)
    db.commit()
    db.refresh(nuevo_bus)
    
    return {
        "mensaje": "Bus creado exitosamente",
        "bus": nuevo_bus
    }

@router.put("/{bus_id}")
def actualizar_bus(
    bus_id: int,
    placa: str = Form(...),
    modelo: str = Form(...),
    capacidad: int = Form(...),
    estado: bool = Form(...),
    hora_inicio: str = Form(None),
    hora_llegada: str = Form(None),
    id_conductor: int = Form(None),
    id_ruta: int = Form(None),
    db: Session = Depends(get_db)
):
    bus = db.query(Bus).filter(Bus.id == bus_id).first()
    if not bus:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    
    # Validar placa única (excepto el mismo bus)
    bus_existente = db.query(Bus).filter(Bus.placa == placa, Bus.id != bus_id).first()
    if bus_existente:
        raise HTTPException(status_code=400, detail="La placa ya está registrada")
    
    # Convertir strings de hora a objetos time
    hora_inicio_obj = None
    hora_llegada_obj = None
    
    if hora_inicio:
        try:
            h, m = map(int, hora_inicio.split(':'))
            hora_inicio_obj = time(h, m)
        except:
            raise HTTPException(status_code=400, detail="Formato de hora inicio inválido (usa HH:MM)")
    
    if hora_llegada:
        try:
            h, m = map(int, hora_llegada.split(':'))
            hora_llegada_obj = time(h, m)
        except:
            raise HTTPException(status_code=400, detail="Formato de hora llegada inválido (usa HH:MM)")
    
    bus.placa = placa
    bus.modelo = modelo
    bus.capacidad = capacidad
    bus.estado = estado
    bus.hora_inicio = hora_inicio_obj
    bus.hora_llegada = hora_llegada_obj
    bus.id_conductor = id_conductor
    bus.id_ruta = id_ruta
    
    db.commit()
    db.refresh(bus)
    
    return {
        "mensaje": "Bus actualizado exitosamente",
        "bus": bus
    }

@router.delete("/{bus_id}")
def eliminar_bus(bus_id: int, db: Session = Depends(get_db)):
    bus = db.query(Bus).filter(Bus.id == bus_id).first()
    if not bus:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    
    db.delete(bus)
    db.commit()
    return {"mensaje": "Bus eliminado correctamente"}