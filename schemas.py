from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# =====================================================================
# 1. ESQUEMAS DE TAREAS
# =====================================================================
class TareaBase(BaseModel):
    titulo: str
    descripcion: Optional[str] = None

class TareaCreate(TareaBase):
    pass  # Hereda titulo y descripcion de TareaBase

class Tarea(TareaBase):
    id: int
    completada: bool = False  # Le asignamos un valor por defecto

    class Config:
        from_attributes = True


# =====================================================================
# 2. ESQUEMAS DE CATEGORÍAS
# =====================================================================
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int

    class Config:
        from_attributes = True


# =====================================================================
# 3. ESQUEMAS DE PRODUCTOS
# =====================================================================
class ProductBase(BaseModel):
    name: str
    price: float
    stock: int
    category_id: Optional[int] = None  # Permite asociar una categoría (opcional)

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True


# =====================================================================
# 4. ESQUEMAS DE ÓRDENES (CARRITO DE COMPRAS)
# =====================================================================

# Lo que el cliente nos envía para cada artículo individual del carrito
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

# Lo que el cliente envía para crear la orden completa con su lista de productos
class OrderCreate(BaseModel):
    items: list[OrderItemCreate]

# Lo que la API responde cuando consultamos un artículo dentro de una orden
class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price_at_purchase: float

    class Config:
        from_attributes = True

# Lo que la API responde para la orden completa terminada
class OrderResponse(BaseModel):
    id: int
    created_at: datetime
    total_price: float
    status: str
    items: list[OrderItemResponse]

    class Config:
        from_attributes = True