#!/usr/bin/env python3
"""
Script para crear un usuario administrador
"""

import requests
import json

# Configuración
API_BASE_URL = "http://localhost:8000"

def create_admin_user():
    """Crear usuario administrador"""
    
    admin_data = {
        "username": "admin",
        "password": "admin123",
        "first_name": "Administrador",
        "last_name": "Sistema",
        "phone": "1234567890",
        "role": "admin"
    }
    
    try:
        print("🔧 Creando usuario administrador...")
        print(f"📡 Endpoint: {API_BASE_URL}/users/create")
        
        response = requests.post(
            f"{API_BASE_URL}/users/create",
            json=admin_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📋 Código de respuesta: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Usuario administrador creado exitosamente!")
            print(f"📋 Respuesta: {result}")
            print()
            print("🔑 Credenciales del administrador:")
            print(f"   Usuario: {admin_data['username']}")
            print(f"   Contraseña: {admin_data['password']}")
            print(f"   Rol: {admin_data['role']}")
            
        else:
            print(f"❌ Error creando usuario administrador:")
            try:
                error_detail = response.json()
                print(f"   Detalle: {error_detail}")
            except:
                print(f"   Respuesta: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor API.")
        print("   Asegúrate de que el servidor esté ejecutándose en http://localhost:8000")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def create_test_customer():
    """Crear usuario cliente de prueba"""
    
    customer_data = {
        "username": "cliente1",
        "password": "cliente123",
        "first_name": "Juan",
        "last_name": "Pérez",
        "phone": "9876543210",
        "role": "customer"
    }
    
    try:
        print("🔧 Creando usuario cliente de prueba...")
        
        response = requests.post(
            f"{API_BASE_URL}/users/create",
            json=customer_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Usuario cliente creado exitosamente!")
            print(f"🔑 Credenciales del cliente:")
            print(f"   Usuario: {customer_data['username']}")
            print(f"   Contraseña: {customer_data['password']}")
            print(f"   Rol: {customer_data['role']}")
            
        else:
            print(f"❌ Error creando usuario cliente (probablemente ya existe)")
                
    except Exception as e:
        print(f"❌ Error creando cliente: {e}")

if __name__ == "__main__":
    print("🎬 === CREACIÓN DE USUARIOS DE PRUEBA ===")
    print()
    
    create_admin_user()
    print()
    create_test_customer()
    
    print()
    print("🎯 Ahora puedes usar estos usuarios para probar el sistema:")
    print("   1. Inicia sesión con 'admin' / 'admin123' para ver funciones de administrador")
    print("   2. Inicia sesión con 'cliente1' / 'cliente123' para ver funciones de cliente")
