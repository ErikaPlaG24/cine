#!/usr/bin/env python3
"""
Verificar usuarios en la base de datos
"""

import mysql.connector
from mysql.connector import Error

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'database': 'cine',
    'user': 'root',
    'password': 'root',
    'port': 4003,
    'charset': 'utf8mb4'
}

def check_users():
    """Verificar usuarios en la base de datos"""
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        
        if connection.is_connected():
            print("✅ Conectado a la base de datos MySQL")
            
            cursor = connection.cursor()
            
            # Obtener todos los usuarios
            cursor.execute("SELECT user_id, username, first_name, last_name, role, is_active FROM users")
            users = cursor.fetchall()
            
            print("\n👥 Usuarios en la base de datos:")
            print("=" * 70)
            print(f"{'ID':<5} {'Usuario':<15} {'Nombre':<20} {'Rol':<10} {'Activo'}")
            print("=" * 70)
            
            for user in users:
                user_id, username, first_name, last_name, role, is_active = user
                full_name = f"{first_name} {last_name}"
                active_status = "Sí" if is_active else "No"
                print(f"{user_id:<5} {username:<15} {full_name:<20} {role:<10} {active_status}")
            
            print("=" * 70)
            print(f"Total de usuarios: {len(users)}")
            
    except Error as e:
        print(f"❌ Error: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔒 Conexión cerrada")

if __name__ == "__main__":
    check_users()
