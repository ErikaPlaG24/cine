#!/usr/bin/env python3
"""
Verificar estructura de la tabla customer_memberships
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

def check_memberships_table():
    """Verificar estructura de customer_memberships"""
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        
        if connection.is_connected():
            print("✅ Conectado a la base de datos MySQL")
            
            cursor = connection.cursor()
            
            # Verificar si la tabla existe
            cursor.execute("SHOW TABLES LIKE 'customer_memberships'")
            table_exists = cursor.fetchone()
            
            if table_exists:
                print("\n📋 Estructura de la tabla 'customer_memberships':")
                cursor.execute("DESCRIBE customer_memberships")
                columns = cursor.fetchall()
                
                for column in columns:
                    field, type_, null, key, default, extra = column
                    print(f"   {field:<20} {type_:<15} NULL: {null:<3} Key: {key:<3} Default: {default}")
                
                # Ver datos existentes
                cursor.execute("SELECT COUNT(*) FROM customer_memberships")
                count = cursor.fetchone()[0]
                print(f"\n📊 Registros en customer_memberships: {count}")
                
                if count > 0:
                    cursor.execute("SELECT * FROM customer_memberships LIMIT 3")
                    records = cursor.fetchall()
                    print("\n📋 Muestra de registros:")
                    for record in records:
                        print(f"   {record}")
                        
            else:
                print("❌ La tabla 'customer_memberships' no existe")
                
                # Verificar otras tablas relacionadas con membresías
                cursor.execute("SHOW TABLES")
                tables = [table[0] for table in cursor.fetchall()]
                print(f"\n📋 Tablas disponibles: {tables}")
                
                membership_tables = [t for t in tables if 'member' in t.lower()]
                if membership_tables:
                    print(f"📋 Tablas relacionadas con membresías: {membership_tables}")
                    
                    for table in membership_tables:
                        print(f"\n📋 Estructura de '{table}':")
                        cursor.execute(f"DESCRIBE {table}")
                        columns = cursor.fetchall()
                        
                        for column in columns:
                            field, type_, null, key, default, extra = column
                            print(f"   {field:<20} {type_:<15} NULL: {null:<3} Key: {key:<3} Default: {default}")
            
    except Error as e:
        print(f"❌ Error: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔒 Conexión cerrada")

if __name__ == "__main__":
    check_memberships_table()
