#!/usr/bin/env python3
"""
Script para ejecutar la API localmente conectándose a MySQL en Docker
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar variables de entorno para conectarse a MySQL en Docker
os.environ["MYSQL_HOST"] = "localhost"
os.environ["JWT_SECRET_KEY"] = "tu_clave_secreta_super_segura_aqui"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["JWT_EXPIRATION_TIME"] = "60"

# Importar dependencias
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.database.mysql_connection import MySQLConnection

# Importar rutas
from api.routes.auth import router as auth_router
from api.routes.movies import router as movies_router
from api.routes.theaters import router as theaters_router
from api.routes.showtimes import router as showtimes_router
from api.routes.reserved_seats import router as reserved_seats_router
from api.routes.sales import router as sales_router
from api.routes.users import router as users_router
from api.routes.memberships import router as memberships_router
from api.routes.customer_memberships import router as customer_memberships_router
from api.routes.movie_genres import router as movie_genres_router

# Crear app FastAPI
app = FastAPI(title="Cinema API", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Inicializar conexión a base de datos con puerto correcto para Docker
db = MySQLConnection(
    host="localhost",
    port=4003,  # Puerto mapeado en docker-compose
    user="root",
    password="root",
    database="cine"
)

# Registrar rutas
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(movies_router, prefix="/movies", tags=["movies"])
app.include_router(theaters_router, prefix="/theaters", tags=["theaters"])
app.include_router(showtimes_router, prefix="/showtimes", tags=["showtimes"])
app.include_router(reserved_seats_router, prefix="/reserved_seats", tags=["reserved_seats"])
app.include_router(sales_router, prefix="/sales", tags=["sales"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(memberships_router, prefix="/memberships", tags=["memberships"])
app.include_router(customer_memberships_router, prefix="/customer_memberships", tags=["customer_memberships"])
app.include_router(movie_genres_router, prefix="/movie_genres", tags=["movie_genres"])

# Servir archivos estáticos del frontend
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/")
async def root():
    return {"message": "Cinema API is running!", "status": "ok", "version": "1.0.0"}

if __name__ == "__main__":
    print("🚀 Iniciando API localmente...")
    print("📍 Conectándose a MySQL en Docker (puerto 4003)")
    print("🌐 API disponible en: http://localhost:8001")
    print("📁 Frontend estático en: http://localhost:8001/frontend/")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8001,  # Usar puerto diferente para no conflictuar con Docker
        reload=True
    )
