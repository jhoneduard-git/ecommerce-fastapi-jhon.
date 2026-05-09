from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

# Importamos nuestras piezas
import models, schemas, database
from database import SessionLocal, engine

# 1. Crea las tablas físicamente en tu archivo .db (si no existen)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mi API de Tareas")

# 2. Función para obtener la conexión a la DB (Dependencia)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- NUESTRAS RUTAS (ENDPOINTS) ---

@app.get("/")
def home():
    return {"mensaje": "¡Bienvenido a mi API de Tareas!"}

@app.get("/tareas/", response_model=list[schemas.Tarea])
def leer_tareas(db: Session = Depends(get_db)):
    # Buscamos todas las tareas en la base de datos
    tareas = db.query(models.Tarea).all()
    return tareas
@app.post("/tareas/", response_model=schemas.Tarea)
def crear_tarea(tarea: schemas.TareaCreate, db: Session = Depends(get_db)):
    # 1. Creamos el objeto para la base de datos usando los datos del usuario
    nueva_tarea = models.Tarea(
        titulo=tarea.titulo, 
        descripcion=tarea.descripcion
    )
    # 2. Guardamos en la DB
    db.add(nueva_tarea)
    db.commit()
    db.refresh(nueva_tarea) # Esto nos da el ID que generó la base de datos
    return nueva_tarea
@app.put("/tareas/{tarea_id}", response_model=schemas.Tarea)
def actualizar_tarea(tarea_id: int, db: Session = Depends(get_db)):
    # 1. Buscamos la tarea por su ID
    tarea_db = db.query(models.Tarea).filter(models.Tarea.id == tarea_id).first()
    
    # 2. Si no existe, lanzamos un error 404
    if not tarea_db:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    # 3. Cambiamos el estado (si estaba en False, pasa a True y viceversa)
    tarea_db.completada = not tarea_db.completada
    
    db.commit()
    db.refresh(tarea_db)
    return tarea_db