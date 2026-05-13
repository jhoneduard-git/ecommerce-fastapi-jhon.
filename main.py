from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

# Importamos nuestras piezas (Asegúrate de que estos archivos existan)
import models, schemas, database
from database import SessionLocal, engine

# 1. Crea las tablas físicamente en la DB (si no existen)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mi API Unificada (Tareas y E-commerce)")

# 2. Función para obtener la conexión a la DB (Dependencia)
# Solo necesitamos una función get_db para todo el archivo
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

@app.get("/tareas/", response_model=list[schemas.Tarea])
def leer_tareas(db: Session = Depends(get_db)):
    tareas = db.query(models.Tarea).all()
    return tareas

@app.post("/tareas/", response_model=schemas.Tarea)
def crear_tarea(tarea: schemas.TareaCreate, db: Session = Depends(get_db)):
    nueva_tarea = models.Tarea(
        titulo=tarea.titulo, 
        descripcion=tarea.descripcion
    )
    db.add(nueva_tarea)
    db.commit()
    db.refresh(nueva_tarea)
    return nueva_tarea

@app.put("/tareas/{tarea_id}", response_model=schemas.Tarea)
def actualizar_tarea(tarea_id: int, db: Session = Depends(get_db)):
    tarea_db = db.query(models.Tarea).filter(models.Tarea.id == tarea_id).first()
    
    if not tarea_db:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    tarea_db.completada = not tarea_db.completada
    db.commit()
    db.refresh(tarea_db)
    return tarea_db

# --- RUTAS DE E-COMMERCE (PRODUCTOS) ---

@app.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    # 1. Convertir el esquema en un modelo de base de datos
    db_product = models.Product(**product.model_dump()) # .dict() está deprecado en Pydantic V2, mejor model_dump()
    
    # 2. Guardarlo en la DB
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return db_product
# Obtener todos los productos
@app.get("/products/", response_model=list[schemas.Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Product).offset(skip).limit(limit).all()

# Obtener un producto específico
@app.get("/products/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return db_product

# Eliminar un producto
@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(db_product)
    db.commit()
    return {"ok": True, "mensaje": "Producto eliminado"}
# Actualizar un producto existente
@app.put("/products/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, product_update: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Actualizamos los campos con la nueva información
    update_data = product_update.model_dump()
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

# Eliminar un producto
@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    db.delete(db_product)
    db.commit()
    return {"mensaje": f"Producto con ID {product_id} eliminado exitosamente"}
# --- ACTUALIZAR PRODUCTO ---
@app.put("/products/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, product_update: schemas.ProductCreate, db: Session = Depends(get_db)):
    # 1. Buscar el producto en la base de datos
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    # 2. Si no existe, lanzar error 404
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # 3. Actualizar los campos con la nueva información
    # Convertimos el esquema a un diccionario
    update_data = product_update.model_dump()
    
    for key, value in update_data.items():
        setattr(db_product, key, value) # Esto cambia nombre, precio, etc.
    
    # 4. Guardar cambios
    db.commit()
    db.refresh(db_product)
    return db_product
    # --- RUTA PARA VENDER (DESCONTAR STOCK) ---
@app.post("/products/{product_id}/sell", response_model=schemas.Product)
def sell_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    if db_product.stock <= 0:
        raise HTTPException(status_code=400, detail="No hay suficiente stock para realizar la venta")
    
    # Restamos una unidad
    db_product.stock -= 1
    
    db.commit()
    db.refresh(db_product)
    return db_product