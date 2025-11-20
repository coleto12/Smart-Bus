from backend.database.database import Base, engine
from backend.models.models import Usuario, Zona, Ruta, Conductor, Bus, Queja

print("Modelos registrados en Base.metadata:")
print(list(Base.metadata.tables.keys()))
print("\nCreando tablas en Supabase...")
Base.metadata.create_all(bind=engine)
print("Tablas creadas correctamente.")