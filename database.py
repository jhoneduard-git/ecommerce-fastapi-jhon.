from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Dirección de la base de datos (SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///./ecommerce.db"

# 2. El "Motor" (Engine)
# check_same_thread=False es necesario solo para SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. La sesión (Lo que usaremos para hacer consultas)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. La Clase Base (De aquí heredarán nuestros modelos)
Base = declarative_base()