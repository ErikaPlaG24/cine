#!/usr/bin/env python3
"""
Script para crear usuarios directamente en la base de datos
"""

import mysql.connector
from mysql.connector import Error
import bcrypt

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'database': 'cine',
    'user': 'root',
    'password': 'root',
    'port': 4003,
    'charset': 'utf8mb4',
    'autocommit': True
}

def hash_password(password: str) -> str:
    """Generar hash de contraseña usando bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_admin_user():
    """Crear usuario administrador directamente en la base de datos"""
    
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(**DB_CONFIG)
        
        if connection.is_connected():
            print("✅ Conectado a la base de datos MySQL")
            
            cursor = connection.cursor()
            
            # Verificar si el usuario admin ya existe
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
            exists = cursor.fetchone()[0]
            
            if exists > 0:
                print("⚠️ El usuario 'admin' ya existe")
                return
            
            # Hashear la contraseña
            hashed_password = hash_password('admin123')
            
            # Insertar usuario administrador
            insert_query = """
            INSERT INTO users (username, password, first_name, last_name, phone, role, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            values = ('admin', hashed_password, 'Administrador', 'Sistema', '1234567890', 'admin', True)
            
            cursor.execute(insert_query, values)
            connection.commit()
            
            print("✅ Usuario administrador creado exitosamente!")
            print("🔑 Credenciales:")
            print("   Usuario: admin")
            print("   Contraseña: admin123")
            print("   Rol: admin")
            
    except Error as e:
        print(f"❌ Error: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("🔒 Conexión cerrada")

def create_test_customer():
    """Crear usuario cliente de prueba"""
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Verificar si el usuario cliente ya existe
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'cliente1'")
            exists = cursor.fetchone()[0]
            
            if exists > 0:
                print("⚠️ El usuario 'cliente1' ya existe")
                return
            
            # Hashear la contraseña
            hashed_password = hash_password('cliente123')
            
            # Insertar usuario cliente
            insert_query = """
            INSERT INTO users (username, password, first_name, last_name, phone, role, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            values = ('cliente1', hashed_password, 'Juan', 'Pérez', '9876543210', 'customer', True)
            
            cursor.execute(insert_query, values)
            connection.commit()
            
            print("✅ Usuario cliente creado exitosamente!")
            print("🔑 Credenciales:")
            print("   Usuario: cliente1")
            print("   Contraseña: cliente123")
            print("   Rol: customer")
            
    except Error as e:
        print(f"❌ Error: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    print("🎬 === CREACIÓN DE USUARIOS DE PRUEBA ===")
    print()
    
    create_admin_user()
    print()
    create_test_customer()
    
    print()
    print("🎯 Usuarios creados. Ahora puedes:")
    print("   1. Iniciar sesión como 'admin' para ver funciones de administrador")
    print("   2. Iniciar sesión como 'cliente1' para ver funciones normales")
