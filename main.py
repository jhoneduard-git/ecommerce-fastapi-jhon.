from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, database
from database import SessionLocal, engine

# Crea las tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mi API Unificada (Tareas e E-commerce)")

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
# =====================================================================
# RUTAS DE LECTURA DE PRODUCTOS (GET) - CÓDIGO CORREGIDO y SIN DUPLICADOS
# =====================================================================

# 1. Obtener todos los productos (con opción de buscar por nombre)
@app.get("/products/", response_model=list[schemas.Product], tags=["Productos"])
def read_products(
    search: str = None, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    # Iniciamos la consulta base
    query = db.query(models.Product)
    
    # Si el usuario escribe algo en el buscador, filtramos las coincidencias
    if search:
        # Recuerda cambiar .name por .nombre si así se llama en tu models.py
        query = query.filter(models.Product.name.contains(search))
    
    # Devolvemos el resultado final aplicando la paginación
    return query.offset(skip).limit(limit).all()


# 2. Obtener un producto específico usando su ID único
@app.get("/products/{product_id}", response_model=schemas.Product, tags=["Productos"])
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
        
    return db_product

# 2. ESTA FUNCIÓN LA DEJAS EXACTAMENTE IGUAL (No la borres)
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
def sell_product(product_id: int, quantity: int = 1, db: Session = Depends(get_db)):
    # 1. Buscar el producto en la base de datos
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    # 2. Validar si el producto existe
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # 3. Validar si la cantidad solicitada es válida (mayor a 0)
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="La cantidad a vender debe ser mayor a 0")
    
    # 4. Validar si hay suficiente stock para cubrir la demanda exacta
    if db_product.stock < quantity:
        raise HTTPException(
            status_code=400, 
            detail=f"No hay suficiente stock. Stock disponible: {db_product.stock}, solicitado: {quantity}"
        )
    
    # 5. Restar la cantidad exacta solicitada
    db_product.stock -= quantity
    
    # 6. Guardar los cambios en la base de datos y refrescar
    db.commit()
    db.refresh(db_product)
    return db_product
# =====================================================================
# RUTAS DE CATEGORÍAS
# =====================================================================

@app.post("/categories/", response_model=schemas.Category, tags=["Categorías"])
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    # Validar si ya existe una categoría con ese nombre
    db_category = db.query(models.Category).filter(models.Category.name == category.name).first()
    if db_category:
        raise HTTPException(status_code=400, detail="La categoría ya existe")
    
    new_category = models.Category(name=category.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@app.get("/categories/", response_model=list[schemas.Category], tags=["Categorías"])
def read_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()
@app.put("/categories/{category_id}", response_model=schemas.Category, tags=["Categorías"])
def update_category(
    category_id: int, 
    category_data: schemas.CategoryCreate, 
    db: Session = Depends(get_db)
):
    # 1. Buscar la categoría por su ID
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    
    # 2. Si no existe, lanzar un error 404
    if not db_category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    # 3. Validar que el nuevo nombre no esté repetido con otra categoría
    name_exists = db.query(models.Category).filter(
        models.Category.name == category_data.name, 
        models.Category.id != category_id
    ).first()
    
    if name_exists:
        raise HTTPException(status_code=400, detail="Ya existe otra categoría con ese nombre")
    
    # 4. Actualizar el nombre
    db_category.name = category_data.name
    
    # 5. Guardar los cambios
    db.commit()
    db.refresh(db_category)
    return db_category