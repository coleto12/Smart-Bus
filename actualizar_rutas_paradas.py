from sqlalchemy import text
from backend.database.database import engine

print("🔧 Actualizando tabla rutas para usar paradas...")

with engine.connect() as connection:
    try:
        # Agregar columnas nuevas
        connection.execute(text("""
            ALTER TABLE rutas 
            ADD COLUMN IF NOT EXISTS nombre VARCHAR(100);
        """))
        connection.commit()
        print("✅ Columna 'nombre' agregada")
        
        connection.execute(text("""
            ALTER TABLE rutas 
            ADD COLUMN IF NOT EXISTS id_origen INTEGER;
        """))
        connection.commit()
        print("✅ Columna 'id_origen' agregada")
        
        connection.execute(text("""
            ALTER TABLE rutas 
            ADD COLUMN IF NOT EXISTS id_destino INTEGER;
        """))
        connection.commit()
        print("✅ Columna 'id_destino' agregada")
        
        connection.execute(text("""
            ALTER TABLE rutas 
            ADD COLUMN IF NOT EXISTS paradas_orden VARCHAR(500);
        """))
        connection.commit()
        print("✅ Columna 'paradas_orden' agregada")
        
        # Agregar foreign keys (puede fallar si ya existen)
        try:
            connection.execute(text("""
                ALTER TABLE rutas 
                ADD CONSTRAINT fk_ruta_parada_origen 
                FOREIGN KEY (id_origen) REFERENCES paradas(id);
            """))
            connection.commit()
            print("✅ Foreign key origen agregada")
        except Exception as e:
            print(f"⚠️ Foreign key origen: {e}")
        
        try:
            connection.execute(text("""
                ALTER TABLE rutas 
                ADD CONSTRAINT fk_ruta_parada_destino 
                FOREIGN KEY (id_destino) REFERENCES paradas(id);
            """))
            connection.commit()
            print("✅ Foreign key destino agregada")
        except Exception as e:
            print(f"⚠️ Foreign key destino: {e}")
        
        print("\n🎉 ¡Tabla actualizada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        connection.rollback()