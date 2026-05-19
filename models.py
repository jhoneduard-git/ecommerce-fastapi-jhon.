from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    # Relación: Permite acceder a los productos de esta categoría usando .products
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    stock = Column(Integer)
    
    # 1. Creamos la Clave Foránea (Foreign Key) que une el producto a una categoría
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    # 2. Relación: Permite acceder a la categoría del producto usando .category
    category = relationship("Category", back_populates="products")