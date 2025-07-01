#!/usr/bin/env python3
"""
Verificar estructura de tablas
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

def check_table_structure():
    """Verificar estructura de las tablas principales"""
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        
        if connection.is_connected():
            print("✅ Conectado a la base de datos MySQL")
            
            cursor = connection.cursor()
            
            # Verificar estructura de la tabla sales
            print("\n📋 Estructura de la tabla 'sales':")
            cursor.execute("DESCRIBE sales")
            columns = cursor.fetchall()
            
            for column in columns:
                field, type_, null, key, default, extra = column
                print(f"   {field:<20} {type_:<15} NULL: {null:<3} Key: {key:<3} Default: {default}")
            
            # Verificar estructura de la tabla reserved_seats
            print("\n📋 Estructura de la tabla 'reserved_seats':")
            cursor.execute("DESCRIBE reserved_seats")
            columns = cursor.fetchall()
            
            for column in columns:
                field, type_, null, key, default, extra = column
                print(f"   {field:<20} {type_:<15} NULL: {null:<3} Key: {key:<3} Default: {default}")
            
            # Ver algunas ventas existentes
            print("\n💰 Ventas existentes (muestra):")
            cursor.execute("SELECT * FROM sales LIMIT 3")
            sales = cursor.fetchall()
            
            if sales:
                # Obtener nombres de columnas
                cursor.execute("SHOW COLUMNS FROM sales")
                columns = [col[0] for col in cursor.fetchall()]
                print(f"   Columnas: {columns}")
                
                for sale in sales:
                    print(f"   {sale}")
            else:
                print("   No hay ventas en la base de datos")
            
    except Error as e:
        print(f"❌ Error: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔒 Conexión cerrada")

if __name__ == "__main__":
    check_table_structure()
