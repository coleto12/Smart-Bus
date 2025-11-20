from fastapi import APIRouter, Depends, HTTPException, Form, status
from sqlalchemy.orm import Session
from datetime import timedelta
from backend.database.database import get_db
from backend.models.models import Usuario
from backend.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)

@router.post("/register")
def register(
    nombre: str = Form(...),
    correo: str = Form(...),
    contraseña: str = Form(...),
    rol: str = Form(...),
    db: Session = Depends(get_db)
):
    print(f"📝 Intento de registro: {correo}")
    
    try:
        # ✅ VALIDACIÓN DE SEGURIDAD: Solo permitir registro de pasajeros
        if rol not in ["pasajero"]:
            raise HTTPException(
                status_code=403, 
                detail="Solo puedes registrarte como pasajero. Los conductores y administradores son registrados por el sistema."
            )
        
        existente = db.query(Usuario).filter(Usuario.correo == correo).first()
        if existente:
            raise HTTPException(status_code=400, detail="El correo ya está registrado")
        
        nuevo = Usuario(
            nombre=nombre,
            correo=correo,
            contraseña=hash_password(contraseña),
            rol=rol
        )
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        
        print(f"✅ Usuario registrado: {correo}")
        
        return {
            "mensaje": "Registro exitoso",
            "usuario": {
                "nombre": nuevo.nombre,
                "correo": nuevo.correo,
                "rol": nuevo.rol
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/login")
def login(
    correo: str = Form(...),
    contraseña: str = Form(...),
    db: Session = Depends(get_db)
):
    print(f"🔐 Intento de login: {correo}")
    
    try:
        usuario = db.query(Usuario).filter(Usuario.correo == correo).first()
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo o contraseña incorrectos"
            )
        
        if not verify_password(contraseña, usuario.contraseña):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo o contraseña incorrectos"
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": usuario.correo, "rol": usuario.rol},
            expires_delta=access_token_expires
        )
        
        print(f"✅ Login exitoso: {correo}")
        
        return {
            "mensaje": "Login exitoso",
            "access_token": access_token,
            "token_type": "bearer",
            "usuario": {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "correo": usuario.correo,
                "rol": usuario.rol
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))