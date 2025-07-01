import requests
import json

# Probar login con usuario que tiene contraseña en texto plano
def test_login():
    url = "http://localhost:5000/auth/login"
    
    # Probar con Isaura (contraseña en texto plano)
    login_data = {
        "username": "Isaura",
        "password": "123456"
    }
    
    try:
        print("🔍 Probando login con Isaura...")
        response = requests.post(url, json=login_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login exitoso!")
            data = response.json()
            print(f"Token: {data.get('access_token', 'No token')}")
            print(f"Usuario: {data.get('user', 'No user data')}")
        else:
            print("❌ Login falló")
            
    except Exception as e:
        print(f"❌ Error en login: {e}")

if __name__ == "__main__":
    test_login()
