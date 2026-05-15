from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, database
from database import SessionLocal, engine

# Crea las tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mi API Unificada (Tareas y E-commerce)")

# Dependencia para la DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- RUTAS DE BIENVENIDA ---
@app.get("/")
def home():
    return {"mensaje": "¡Bienvenido a mi API! Tienes acceso a /tareas y /products"}

# --- RUTAS DE TAREAS ---

@app.get("/tareas/", response_model=list[schemas.Tarea], tags=["Tareas"])
def leer_tareas(db: Session = Depends(get_db)):
    return db.query(models.Tarea).all()

@app.post("/tareas/", response_model=schemas.Tarea, tags=["Tareas"])
def crear_tarea(tarea: schemas.TareaCreate, db: Session = Depends(get_db)):
    nueva_tarea = models.Tarea(titulo=tarea.titulo, descripcion=tarea.descripcion)
    db.add(nueva_tarea)
    db.commit()
    db.refresh(nueva_tarea)
    return nueva_tarea

# --- RUTAS DE E-COMMERCE (PRODUCTOS) ---

@app.get("/products/", response_model=list[schemas.Product], tags=["Productos"])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Product).offset(skip).limit(limit).all()

@app.get("/products/{product_id}", response_model=schemas.Product, tags=["Productos"])
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return db_product

@app.post("/products/", response_model=schemas.Product, tags=["Productos"])
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.put("/products/{product_id}", response_model=schemas.Product, tags=["Productos"])
def update_product(product_id: int, product_update: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    update_data = product_update.model_dump()
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/products/{product_id}", tags=["Productos"])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(db_product)
    db.commit()
    return {"mensaje": f"Producto con ID {product_id} eliminado exitosamente"}

@app.post("/products/{product_id}/sell", response_model=schemas.Product, tags=["Productos"])
def sell_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if db_product.stock <= 0:
        raise HTTPException(status_code=400, detail="No hay suficiente stock para realizar la venta")
    
    db_product.stock -= 1
    db.commit()
    db.refresh(db_product)
    return db_product