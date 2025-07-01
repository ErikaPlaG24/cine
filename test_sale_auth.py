#!/usr/bin/env python3
"""
Script para obtener token y probar venta
"""

import requests
import json

def get_auth_token():
    """Obtener token de autenticación"""
    login_url = "http://localhost:5000/auth/login"
    login_data = {
        "username": "Isaura",
        "password": "123456"  # Usar la contraseña correcta en texto plano
    }
    
    print("🔐 Obteniendo token de autenticación...")
    
    try:
        response = requests.post(login_url, json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"✅ Token obtenido: {token[:20]}...")
            return token
        else:
            print(f"❌ Error en login: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión en login: {e}")
        return None

def test_create_sale_with_auth():
    """Probar crear venta con autenticación"""
    token = get_auth_token()
    if not token:
        print("❌ No se pudo obtener token")
        return
    
    test_sale_data = {
        "customer_user_id": 1,
        "showtime_id": 4,
        "ticket_quantity": 2,
        "subtotal": 150.0,
        "total": 150.0,
        "payment_method": "cash",
        "seats": ["A1", "A2"]
    }
    
    url = "http://localhost:5000/sales/create"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    print(f"\n🧪 Probando endpoint de crear venta con autenticación...")
    print(f"URL: {url}")
    print(f"Datos: {json.dumps(test_sale_data, indent=2)}")
    
    try:
        response = requests.post(url, json=test_sale_data, headers=headers)
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Éxito!")
            print(f"Respuesta: {response.json()}")
        else:
            print(f"❌ Error {response.status_code}")
            try:
                error_detail = response.json()
                print(f"Detalle del error: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"Respuesta de error: {response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    test_create_sale_with_auth()
