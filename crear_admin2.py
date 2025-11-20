from backend.database.database import SessionLocal
from backend.models.models import Usuario
from backend.core.security import hash_password

print("🔧 Creando cuenta de administrador...")

db = SessionLocal()

# Verificar si ya existe un admin
admin_existente = db.query(Usuario).filter(Usuario.rol == "administrador").first()


    # Crear nuevo administrador
admin = Usuario(
        nombre="Jovanny Jimenez",
        correo="jovannyjimenez@gmail.com",
        contraseña=hash_password("123456"),
        rol="administrador"
    )
db.add(admin)
db.commit()
db.refresh(admin)
    
print("✅ ¡Administrador creado exitosamente!")
print("\n📋 Datos de acceso:")
print(f"   📧 Correo: {admin.correo}")
print(f"   🔑 Contraseña: 123456")
print(f"   👤 Nombre: {admin.nombre}")
print(f"   🎭 Rol: {admin.rol}")
print("\n🌐 Inicia sesión en: http://127.0.0.1:8000/auth")

db.close()