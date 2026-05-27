from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, database
from database import SessionLocal, engine
import jwt
from datetime import datetime, timedelta
import security  # Nuestro archivo auxiliar de encriptación

# Crea las tablas automáticamente al iniciar el servidor
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mi API Unificada (Tareas e E-commerce)")

# =====================================================================
# CONFIGURACIÓN SEGURIDAD (Agrega estas 3 líneas aquí mismo)
# =====================================================================
SECRET_KEY = "MI_LLAVE_SECRETA_SUPER_SEGURA_PARA_EL_PORTAFOLIO"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Dependencia para conectar y cerrar la sesión de la Base de Datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =====================================================================
# --- 1. RUTA DE BIENVENIDA ---
# =====================================================================
@app.get("/", tags=["General"])
def home():
    return {"mensaje": "¡Bienvenido a mi API! Tienes acceso a /tareas, /products y /categories"}


# =====================================================================
# --- 2. RUTAS DE TAREAS ---
# =====================================================================
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


# =====================================================================
# --- 3. RUTAS DE E-COMMERCE (PRODUCTOS) ---
# =====================================================================

# Obtener todos los productos (con opción de buscar por nombre y paginación)
@app.get("/products/", response_model=list[schemas.Product], tags=["Productos"])
def read_products(
    search: str = None, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    query = db.query(models.Product)
    if search:
        query = query.filter(models.Product.name.contains(search))
    return query.offset(skip).limit(limit).all()

# Obtener un producto específico usando su ID único
@app.get("/products/{product_id}", response_model=schemas.Product, tags=["Productos"])
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return db_product

# Crear un nuevo producto
@app.post("/products/", response_model=schemas.Product, tags=["Productos"])
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# Actualizar un producto existente
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

# Eliminar un producto
@app.delete("/products/{product_id}", tags=["Productos"])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(db_product)
    db.commit()
    return {"mensaje": f"Producto con ID {product_id} eliminado exitosamente"}

# Vender una cantidad individual de un producto específico
@app.post("/products/{product_id}/sell", response_model=schemas.Product, tags=["Productos"])
def sell_product(product_id: int, quantity: int = 1, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="La cantidad a vender debe ser mayor a 0")
    if db_product.stock < quantity:
        raise HTTPException(
            status_code=400, 
            detail=f"No hay suficiente stock. Stock disponible: {db_product.stock}, solicitado: {quantity}"
        )
    
    db_product.stock -= quantity
    db.commit()
    db.refresh(db_product)
    return db_product


# =====================================================================
# --- 4. RUTAS DE CATEGORÍAS ---
# =====================================================================

# Crear una nueva categoría
@app.post("/categories/", response_model=schemas.Category, tags=["Categorías"])
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    db_category = db.query(models.Category).filter(models.Category.name == category.name).first()
    if db_category:
        raise HTTPException(status_code=400, detail="La categoría ya existe")
    
    new_category = models.Category(name=category.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

# Obtener todas las categorías
@app.get("/categories/", response_model=list[schemas.Category], tags=["Categorías"])
def read_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()

# Actualizar el nombre de una categoría
@app.put("/categories/{category_id}", response_model=schemas.Category, tags=["Categorías"])
def update_category(category_id: int, category_data: schemas.CategoryCreate, db: Session = Depends(get_db)):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    name_exists = db.query(models.Category).filter(
        models.Category.name == category_data.name, 
        models.Category.id != category_id
    ).first()
    
    if name_exists:
        raise HTTPException(status_code=400, detail="Ya existe otra categoría con ese nombre")
    
    db_category.name = category_data.name
    db.commit()
    db.refresh(db_category)
    return db_category


# =====================================================================
# --- 5. RUTAS DE ÓRDENES (CARRITO DE COMPRAS - MUCHOS A MUCHOS) ---
# =====================================================================

# Procesar una orden con múltiples productos, cantidades y validación integral de stock
@app.post("/orders/", response_model=schemas.OrderResponse, tags=["Órdenes (Carrito)"])
def create_order(order_data: schemas.OrderCreate, db: Session = Depends(get_db)):
    total_order_price = 0.0
    items_to_create = []

    # CAPA 1: Validar stock de todos los productos antes de alterar nada en la DB
    for item in order_data.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        
        if not product:
            raise HTTPException(status_code=404, detail=f"Producto con ID {item.product_id} no encontrado")
        
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Stock insuficiente para {product.name}. Disponible: {product.stock}, Solicitado: {item.quantity}"
            )
        
        item_total = product.price * item.quantity
        total_order_price += item_total
        
        # Almacenamos temporalmente las referencias válidas
        items_to_create.append((product, item.quantity, product.price))

    # CAPA 2: Si todo el carrito es válido, generamos la cabecera de la orden
    new_order = models.Order(total_price=total_order_price, status="completed")
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # CAPA 3: Descontamos inventario y enlazamos a la tabla intermedia
    for product, quantity, price in items_to_create:
        product.stock -= quantity
        
        order_item = models.OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=quantity,
            price_at_purchase=price
        )
        db.add(order_item)

    db.commit()
    db.refresh(new_order)
    return new_order
# =====================================================================
# --- 6. RUTAS DE AUTENTICACIÓN Y USUARIOS ---
# =====================================================================

# 1. Endpoint para REGISTRAR un nuevo usuario
@app.post("/auth/register", response_model=schemas.UserResponse, tags=["Autenticación"])
def register_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    user_exists = db.query(models.User).filter(models.User.username == user_data.username).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")
    
    email_exists = db.query(models.User).filter(models.User.email == user_data.email).first()
    if email_exists:
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")
    
    hashed_pwd = security.get_password_hash(user_data.password)
    
    new_user = models.User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pwd
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# 2. Endpoint para INICIAR SESIÓN (Genera el Token JWT)
@app.post("/auth/login", response_model=schemas.Token, tags=["Autenticación"])
def login(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == user_data.username).first()
    
    if not user or not security.verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now() + access_token_expires
    
    token_data = {
        "sub": user.username,
        "exp": expire
    }
    
    encoded_jwt = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"access_token": encoded_jwt, "token_type": "bearer"}