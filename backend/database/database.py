from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm import Session
import os

# Leer DATABASE_URL desde variable de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

# Si no existe, usar la de Supabase como fallback
if not DATABASE_URL:
    DATABASE_URL = "postgresql://postgres.hgsxcrndzebldtkhhnca:c1e23m4e5aws-1-us-east-1.pooler.supabase.com:6543/postgres"
    print("⚠️ Usando DATABASE_URL por defecto (Supabase)")
else:
    print(f"✅ Usando DATABASE_URL de variable de entorno")

# Render usa postgres:// pero SQLAlchemy necesita postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Crear motor
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=300,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()