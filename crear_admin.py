from backend.database.database import SessionLocal
from backend.models.models import Usuario
from backend.core.security import hash_password

print("🔧 Creando cuenta de administrador...")

db = SessionLocal()

# Verificar si ya existe un admin
admin_existente = db.query(Usuario).filter(Usuario.rol == "administrador").first()

if admin_existente:
    print("⚠️  Ya existe un administrador:")
    print(f"   Nombre: {admin_existente.nombre}")
    print(f"   Correo: {admin_existente.correo}")
else:
    # Crear nuevo administrador
    admin = Usuario(
        nombre="Samir Otero",
        correo="saamiroteroquintero@gmail.com",
        contraseña=hash_password("c1e2m3m4e5"),
        rol="administrador"
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    print("✅ ¡Administrador creado exitosamente!")
    print("\n📋 Datos de acceso:")
    print(f"   📧 Correo: {admin.correo}")
    print(f"   🔑 Contraseña: c1e2m3m4e5")
    print(f"   👤 Nombre: {admin.nombre}")
    print(f"   🎭 Rol: {admin.rol}")
    print("\n🌐 Inicia sesión en: http://127.0.0.1:8000/auth")

db.close()