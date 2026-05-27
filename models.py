from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# ==========================================
# 1. MODELO: CATEGORÍAS
# ==========================================
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    # Relación: Una categoría tiene muchos productos
    products = relationship("Product", back_populates="category")


# ==========================================
# 2. MODELO: PRODUCTOS
# ==========================================
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    stock = Column(Integer)
    
    # Clave Foránea que une el producto a una categoría
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    # Relación: Un producto pertenece a una categoría
    category = relationship("Category", back_populates="products")


# ==========================================
# 3. MODELO: ÍTEMS DE LA ORDEN (Tabla Intermedia)
# ==========================================
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    price_at_purchase = Column(Float) # Guarda el precio del momento de la compra

    # Relaciones para navegar fácilmente entre objetos
    order = relationship("Order", back_populates="items")
    product = relationship("Product")


# ==========================================
# 4. MODELO: ÓRDENES (Carrito / Ventas)
# ==========================================
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.now)
    total_price = Column(Float, default=0.0)
    status = Column(String, default="completed") # completed, pending, cancelled

    # Relación: Una orden contiene muchos ítems
    items = relationship("OrderItem", back_populates="order")
    # ==========================================
# 5. MODELO: USUARIOS (Autenticación)
# ==========================================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)