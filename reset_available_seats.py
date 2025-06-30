import mysql.connector
from mysql.connector import Error

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'port': 4003,
    'user': 'root',
    'password': 'root',
    'database': 'cine'
}

def ver_trigger_completo():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("🔍 Viendo el trigger before_sale_insert completo...")
        
        cursor.execute("""
            SELECT ACTION_STATEMENT
            FROM information_schema.TRIGGERS 
            WHERE TRIGGER_SCHEMA = 'cine' 
            AND TRIGGER_NAME = 'before_sale_insert'
        """)
        trigger = cursor.fetchone()
        
        if trigger:
            print("📋 Código del trigger before_sale_insert:")
            print(trigger[0])
        else:
            print("❌ No se encontró el trigger")
            
        # También resetear available_seats para que funcione
        print("\n🔧 Reseteando available_seats a valores originales...")
        reset_queries = [
            "UPDATE showtimes SET available_seats = 20 WHERE showtime_id = 2",
            "UPDATE showtimes SET available_seats = 15 WHERE showtime_id = 3", 
            "UPDATE showtimes SET available_seats = 20 WHERE showtime_id = 4",
            "UPDATE showtimes SET available_seats = 14 WHERE showtime_id = 5",
            "UPDATE showtimes SET available_seats = 16 WHERE showtime_id = 6",
            "UPDATE showtimes SET available_seats = 20 WHERE showtime_id = 7"
        ]
        
        for query in reset_queries:
            cursor.execute(query)
            
        connection.commit()
        print("✅ Available_seats reseteados")
        
        # Verificar el resultado
        cursor.execute("SELECT showtime_id, available_seats FROM showtimes")
        showtimes = cursor.fetchall()
        
        print("📋 Available seats actualizados:")
        for showtime in showtimes:
            print(f"   Showtime {showtime[0]}: {showtime[1]} asientos disponibles")
        
    except Error as e:
        print(f"❌ Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    ver_trigger_completo()
