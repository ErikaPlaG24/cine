#!/usr/bin/env python3
"""
Script para probar el login completo y verificar JWT
"""

import requests
import json
import base64

def test_complete_login():
    """Probar el login completo y verificar el token JWT"""
    
    # Hacer login
    login_url = "http://localhost:5000/auth/login"
    login_data = {
        "username": "Isaura",
        "password": "123456"
    }
    
    try:
        print("🔍 Probando login con admin...")
        response = requests.post(login_url, json=login_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"✅ Login exitoso!")
            print(f"Token (primeros 50 chars): {token[:50]}...")
            
            # Verificar que es un JWT
            parts = token.split('.')
            if len(parts) == 3:
                print("✅ Token tiene formato JWT válido")
                
                # Decodificar payload
                try:
                    # Agregar padding si es necesario
                    payload_b64 = parts[1]
                    missing_padding = len(payload_b64) % 4
                    if missing_padding:
                        payload_b64 += '=' * (4 - missing_padding)
                    
                    payload_decoded = base64.b64decode(payload_b64)
                    payload_json = json.loads(payload_decoded)
                    print(f"✅ Payload decodificado: {payload_json}")
                    
                    # Verificar campos necesarios
                    required_fields = ['username', 'role', 'exp', 'iat']
                    missing_fields = [field for field in required_fields if field not in payload_json]
                    
                    if missing_fields:
                        print(f"⚠️ Campos faltantes en el payload: {missing_fields}")
                    else:
                        print("✅ Payload contiene todos los campos necesarios")
                        
                    return token, payload_json
                    
                except Exception as decode_error:
                    print(f"❌ Error decodificando JWT: {decode_error}")
                    return None, None
            else:
                print("❌ Token no tiene formato JWT válido")
                return None, None
        else:
            print(f"❌ Login falló: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return None, None

if __name__ == "__main__":
    print("🎬 === PRUEBA COMPLETA DE LOGIN Y JWT ===")
    token, payload = test_complete_login()
    
    if token and payload:
        print("\n✅ Prueba exitosa: El sistema está generando JWTs válidos")
        print(f"Usuario: {payload.get('username')}")
        print(f"Rol: {payload.get('role')}")
    else:
        print("\n❌ Prueba falló: Hay problemas con el sistema de autenticación")
