from pydantic import BaseModel
from typing import Optional

# 1. Este es el esquema "Base" con lo que siempre tiene una tarea
class TareaBase(BaseModel):
    titulo: str
    descripcion: Optional[str] = None

# 2. Este lo usaremos cuando alguien quiera CREAR una tarea (pide lo mínimo)
class TareaCreate(TareaBase):
    pass  # Hereda titulo y descripcion de TareaBase

# 3. Este es el que la API devolverá al usuario (incluye el ID y el estado)
class Tarea(TareaBase):
    id: int
    completada: bool

    class Config:
        # Esto es vital para que Pydantic pueda leer los modelos de SQLAlchemy
        from_attributes = True