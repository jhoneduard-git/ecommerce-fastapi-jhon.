# E-commerce FastAPI API

Este es un proyecto de backend desarrollado con **FastAPI** para gestionar una tienda virtual y una lista de tareas.

## Funcionalidades
* **Gestión de Productos:** CRUD completo (Crear, Leer, Actualizar, Eliminar).
* **Lógica de Inventario:** Ruta especial para ventas que descuenta stock automáticamente.
* **Validaciones:** Control de stock agotado (error 400).
* **Base de Datos:** Implementado con SQLAlchemy y SQLite.

## Cómo ejecutarlo
1. Instala las dependencias: `pip install fastapi uvicorn sqlalchemy`
2. Ejecuta el servidor: `fastapi dev main.py`
3. Accede a la documentación en: `http://127.0.0.1:8000/docs`