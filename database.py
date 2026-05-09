from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Definimos dónde se guardará la base de datos (SQLite crea un archivo .db local)
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# 2. Creamos el motor (Engine). 
# El argumento 'check_same_thread' solo es necesario para SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. Creamos una sesión. Cada vez que alguien pida algo a la DB, usaremos una instancia de esta sesión.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Esta es la clase "Base". De aquí heredarán nuestros modelos (las tablas de la DB)
Base = declarative_base()