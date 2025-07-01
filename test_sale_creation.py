#!/usr/bin/env python3
"""
Script para probar el endpoint de crear venta directamente
"""

import requests
import json

# Datos de prueba para crear una venta
test_sale_data = {
    "customer_user_id": 1,
    "showtime_id": 4,
    "ticket_quantity": 2,
    "subtotal": 150.0,
    "total": 150.0,
    "payment_method": "cash",
    "seats": ["A1", "A2"]
}

def test_create_sale():
    url = "http://localhost:5000/sales/create"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer dummy_token"  # Token dummy para prueba
    }
    
    print("🧪 Probando endpoint de crear venta...")
    print(f"URL: {url}")
    print(f"Datos: {json.dumps(test_sale_data, indent=2)}")
    
    try:
        response = requests.post(url, json=test_sale_data, headers=headers)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
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
    test_create_sale()
