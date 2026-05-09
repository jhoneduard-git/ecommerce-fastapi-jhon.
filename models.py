from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class Tarea(Base):
    __tablename__ = "tareas"  # Este será el nombre de la tabla en la base de datos

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    descripcion = Column(String)
    completada = Column(Boolean, default=False)