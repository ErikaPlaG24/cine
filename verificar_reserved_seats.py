import mysql.connector
from mysql.connector import Error

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'port': 4003,
    'user': 'root',
    'password': 'root',  # Contraseña correcta
    'database': 'cine'
}

def verificar_tabla_reserved_seats():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("🔍 Verificando estructura de la tabla reserved_seats:")
        cursor.execute("DESCRIBE reserved_seats")
        estructura = cursor.fetchall()
        
        for columna in estructura:
            print(f"   - {columna[0]}: {columna[1]} {'(NULL)' if columna[2] == 'YES' else '(NOT NULL)'}")
        
        print("\n📋 Contenido actual de reserved_seats:")
        cursor.execute("SELECT * FROM reserved_seats LIMIT 10")
        registros = cursor.fetchall()
        
        if registros:
            # Obtener nombres de columnas
            cursor.execute("DESCRIBE reserved_seats")
            columnas = [desc[0] for desc in cursor.fetchall()]
            print(f"   Columnas: {', '.join(columnas)}")
            
            for registro in registros:
                print(f"   {registro}")
        else:
            print("   (No hay registros)")
        
    except Error as e:
        print(f"❌ Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    verificar_tabla_reserved_seats()
