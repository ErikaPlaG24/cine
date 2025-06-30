#!/usr/bin/env python3
"""
Script simple para ejecutar la API localmente
"""
import os
import sys

# Agregar el directorio api al path para importaciones
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

# Configurar variables de entorno
os.environ["MYSQL_HOST"] = "localhost"
os.environ["JWT_SECRET_KEY"] = "tu_clave_secreta_super_segura_aqui"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["JWT_EXPIRATION_TIME"] = "60"

if __name__ == "__main__":
    print("🚀 Iniciando API localmente...")
    print("📍 Conectándose a MySQL en Docker (puerto 4003)")
    print("🌐 API disponible en: http://localhost:8001")
    print("📁 Frontend estático en: http://localhost:8001/frontend/")
    
    # Ejecutar usando uvicorn directamente
    os.system('cd api && uvicorn main:app --host 0.0.0.0 --port 8001 --reload')
