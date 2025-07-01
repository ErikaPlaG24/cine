#!/usr/bin/env python3
"""
Test del endpoint de usuarios
"""

import requests
import json

def test_users_endpoint():
    # Primero hacer login para obtener token
    login_url = "http://localhost:5000/auth/login"
    login_data = {
        "username": "Isaura",
        "password": "123456"
    }
    
    try:
        print("🔍 Haciendo login...")
        login_response = requests.post(login_url, json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Login falló: {login_response.text}")
            return
            
        login_result = login_response.json()
        token = login_result.get('access_token')
        print(f"✅ Login exitoso, token obtenido")
        
        # Ahora probar el endpoint de usuarios
        users_url = "http://localhost:5000/users/all"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        print("🔍 Probando endpoint de usuarios...")
        users_response = requests.get(users_url, headers=headers)
        
        print(f"Status Code: {users_response.status_code}")
        print(f"Response: {users_response.text}")
        
        if users_response.status_code == 200:
            print("✅ Endpoint de usuarios funciona correctamente!")
            users_data = users_response.json()
            print(f"📊 Datos recibidos: {json.dumps(users_data, indent=2)}")
        else:
            print("❌ Endpoint de usuarios falló")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_users_endpoint()
