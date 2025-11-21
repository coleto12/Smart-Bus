from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# Supabase connection (Render requires SSL)
DATABASE_URL = (
    "postgresql+psycopg2://postgres:c1e2m3m4e5@db.hgsxcrndzebldtkhhnca.supabase.co:5432/postgres?sslmode=require"
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=False  # Set to True only if debugging
)

# Session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base
Base = declarative_base()


# Dependency for FastAPI routes
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
