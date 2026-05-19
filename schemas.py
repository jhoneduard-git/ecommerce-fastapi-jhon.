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
        from pydantic import BaseModel
from typing import Optional

# 1. Esquema base (lo que comparten todos)
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int

# 2. Esquema para CREAR un producto (lo que el cliente nos envía)
class ProductCreate(ProductBase):
    pass

# 3. Esquema para DEVOLVER un producto (lo que la API responde)
class Product(ProductBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True
        from pydantic import BaseModel

# Esquemas para Categorías
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int

    class Config:
        from_attributes = True


# Modificamos el esquema de Product para que acepte el category_id (Opcional por ahora)
class ProductBase(BaseModel):
    name: str
    price: float
    stock: int
    category_id: int | None = None  # Añadimos esto para poder asignarle categoría al crear

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True