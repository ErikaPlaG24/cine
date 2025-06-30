import mysql.connector
from mysql.connector import Error

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

print("🎬 Insertando datos de prueba en showtimes...")

try:
    connection = mysql.connector.connect(**DB_CONFIG)
    if connection.is_connected():
        cursor = connection.cursor()
        
        # Primero verificar que tengamos películas y teatros
        cursor.execute("SELECT id FROM movies LIMIT 3")
        movies = cursor.fetchall()
        print(f"Películas disponibles: {movies}")
        
        cursor.execute("SELECT theater_id FROM theaters LIMIT 3")
        theaters = cursor.fetchall()
        print(f"Teatros disponibles: {theaters}")
        
        # Limpiar showtimes existentes
        cursor.execute("DELETE FROM showtimes")
        print("🗑️ Showtimes anteriores eliminados")
        
        # Insertar nuevos showtimes
        showtimes_data = [
            (1, 1, '2024-12-30 14:00:00', 75.00, 20, 0, 0),  # Mad Max, Teatro 1
            (1, 2, '2024-12-30 17:00:00', 85.00, 20, 1, 0),  # Mad Max, Teatro 2, 3D
            (2, 1, '2024-12-30 15:30:00', 65.00, 20, 0, 0),  # Un jefe en pañales, Teatro 1
            (2, 3, '2024-12-30 20:00:00', 70.00, 20, 0, 0),  # Un jefe en pañales, Teatro 3
            (3, 1, '2024-12-30 19:00:00', 80.00, 20, 0, 1),  # El conjuro 3, Teatro 1, IMAX
            (3, 2, '2024-12-30 21:30:00', 75.00, 20, 0, 0),  # El conjuro 3, Teatro 2
        ]
        
        insert_query = """
        INSERT INTO showtimes (movie_id, theater_id, datetime, base_price, available_seats, is_3d, is_imax)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        for data in showtimes_data:
            cursor.execute(insert_query, data)
            print(f"✅ Insertado showtime: movie_id={data[0]}, theater_id={data[1]}, datetime={data[2]}")
        
        # Verificar los datos insertados
        cursor.execute("SELECT showtime_id, movie_id, theater_id, datetime FROM showtimes")
        result = cursor.fetchall()
        print(f"\n📊 Showtimes insertados ({len(result)}):")
        for row in result:
            print(f"   - ID: {row[0]}, Movie: {row[1]}, Theater: {row[2]}, DateTime: {row[3]}")
            
        connection.commit()
        cursor.close()
        connection.close()
        print("\n✅ Datos de showtimes insertados exitosamente!")
        
except Error as e:
    print(f"❌ Error: {e}")
except Exception as e:
    print(f"❌ Error general: {e}")
