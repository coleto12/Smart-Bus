from sqlalchemy import text
from backend.database.database import engine

print("🔧 Agregando columna 'leida' a la tabla quejas...")

with engine.connect() as connection:
    try:
        connection.execute(text("""
            ALTER TABLE quejas 
            ADD COLUMN IF NOT EXISTS leida BOOLEAN DEFAULT FALSE;
        """))
        connection.commit()
        print("✅ Columna 'leida' agregada exitosamente")
    except Exception as e:
        print(f"❌ Error: {e}")
        connection.rollback()