from backend.database.database import engine, Base
from backend.models.models import Usuario, Conductor, Bus, Ruta, Zona, Queja

# ⚠️ ESTO BORRA TODAS LAS TABLAS Y LAS VUELVE A CREAR
print("⚠️  Eliminando tablas existentes...")
Base.metadata.drop_all(bind=engine)

print("✅ Creando tablas nuevas...")
Base.metadata.create_all(bind=engine)

print("🎉 ¡Tablas recreadas exitosamente!")