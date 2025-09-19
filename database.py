from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Define la ruta y el nombre de tu archivo de base de datos SQLite
DATABASE_URL = "sqlite:///./palettes.db"

# 2. Crea el "motor" de la base de datos
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. Crea una sesión para las transacciones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Crea una clase base para nuestros modelos de datos (las tablas)
Base = declarative_base()