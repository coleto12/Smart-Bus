from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.models.models import Usuario
from backend.core.security import hash_password, verify_password
from backend.core.dependiencies import get_current_user

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

# ✅ Ruta protegida - Obtener perfil actual
@router.get("/me")
def obtener_mi_perfil(current_user: Usuario = Depends(get_current_user)):
    """Obtiene el perfil del usuario actual (requiere JWT)"""
    return {
        "id": current_user.id,
        "nombre": current_user.nombre,
        "correo": current_user.correo,
        "rol": current_user.rol,
        "mensaje": "✅ JWT funciona correctamente!"
    }

# ✅ Obtener todos los usuarios (solo admin)
@router.get("/")
def obtener_usuarios(db: Session = Depends(get_db)):
    """Obtiene todos los usuarios"""
    usuarios = db.query(Usuario).all()
    # No devolver las contraseñas
    return [{
        "id": u.id,
        "nombre": u.nombre,
        "correo": u.correo,
        "rol": u.rol
    } for u in usuarios]

# ✅ Obtener un usuario por ID
@router.get("/{usuario_id}")
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "correo": usuario.correo,
        "rol": usuario.rol
    }

# ✅ Crear usuario
@router.post("/")
def crear_usuario(
    nombre: str = Form(...),
    correo: str = Form(...),
    contraseña: str = Form(...),
    rol: str = Form(...),
    db: Session = Depends(get_db)
):
    # Verificar si el correo ya existe
    existente = db.query(Usuario).filter(Usuario.correo == correo).first()
    if existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    
    # ✅ Validar rol (sin conductor)
    roles_validos = ["pasajero", "administrador"]
    if rol not in roles_validos:
        raise HTTPException(
            status_code=400, 
            detail="Rol inválido. Los conductores deben crearse desde el módulo de conductores"
        )
    
    nuevo = Usuario(
        nombre=nombre,
        correo=correo,
        contraseña=hash_password(contraseña),
        rol=rol
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    
    return {
        "id": nuevo.id,
        "nombre": nuevo.nombre,
        "correo": nuevo.correo,
        "rol": nuevo.rol,
        "mensaje": "Usuario creado exitosamente"
    }

# ✅ Actualizar usuario
@router.put("/{usuario_id}")
def actualizar_usuario(
    usuario_id: int,
    nombre: str = Form(...),
    correo: str = Form(...),
    rol: str = Form(...),
    contraseña: str = Form(None),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar si el nuevo correo ya existe (en otro usuario)
    correo_existente = db.query(Usuario).filter(
        Usuario.correo == correo,
        Usuario.id != usuario_id
    ).first()
    if correo_existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    
    # ✅ Validar rol
    # Si el usuario actual es conductor, no permitir cambiar su rol desde aquí
    if usuario.rol == "conductor":
        raise HTTPException(
            status_code=400,
            detail="Los conductores solo pueden editarse desde el módulo de conductores"
        )
    
    # Para usuarios no-conductores, solo permitir pasajero y administrador
    roles_validos = ["pasajero", "administrador"]
    if rol not in roles_validos:
        raise HTTPException(
            status_code=400,
            detail="Rol inválido. Los conductores deben gestionarse desde su módulo"
        )
    
    # Actualizar datos
    usuario.nombre = nombre
    usuario.correo = correo
    usuario.rol = rol
    
    # Actualizar contraseña solo si se proporciona
    if contraseña and contraseña.strip():
        usuario.contraseña = hash_password(contraseña)
    
    db.commit()
    db.refresh(usuario)
    
    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "correo": usuario.correo,
        "rol": usuario.rol,
        "mensaje": "Usuario actualizado exitosamente"
    }

# ✅ Eliminar usuario
@router.delete("/{usuario_id}")
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # ✅ No permitir eliminar conductores desde aquí
    if usuario.rol == "conductor":
        raise HTTPException(
            status_code=400,
            detail="Los conductores solo pueden eliminarse desde el módulo de conductores"
        )
    
    # Evitar eliminar al último administrador
    if usuario.rol == "administrador":
        admins = db.query(Usuario).filter(Usuario.rol == "administrador").count()
        if admins <= 1:
            raise HTTPException(
                status_code=400, 
                detail="No puedes eliminar al único administrador del sistema"
            )
    
    db.delete(usuario)
    db.commit()
    return {"mensaje": "Usuario eliminado correctamente"}