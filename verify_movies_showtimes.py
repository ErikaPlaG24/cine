#!/usr/bin/env python3
"""
Script para verificar que todas las películas tengan horarios
"""

import mysql.connector

def connect_to_database():
    """Conecta a la base de datos MySQL"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=4003,
            user='root',
            password='root',
            database='cine'
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def verify_movies_and_showtimes():
    """Verifica que todas las películas tengan horarios"""
    connection = connect_to_database()
    if not connection:
        return
    
    cursor = connection.cursor()
    
    try:
        # Obtener todas las películas
        query_movies = "SELECT id, title FROM movies ORDER BY id"
        cursor.execute(query_movies)
        movies = cursor.fetchall()
        
        print("🎬 PELÍCULAS EN LA BASE DE DATOS:")
        print("-" * 50)
        for movie_id, title in movies:
            print(f"ID: {movie_id:2d} | {title}")
        
        print("\n🕐 HORARIOS POR PELÍCULA:")
        print("-" * 80)
        
        for movie_id, title in movies:
            # Obtener horarios para esta película
            query_showtimes = """
            SELECT s.showtime_id, s.theater_id, s.datetime, s.base_price, s.is_imax, t.name
            FROM showtimes s
            JOIN theaters t ON s.theater_id = t.theater_id
            WHERE s.movie_id = %s
            ORDER BY s.datetime
            """
            
            cursor.execute(query_showtimes, (movie_id,))
            showtimes = cursor.fetchall()
            
            print(f"\n📽️ {title} (ID: {movie_id})")
            if not showtimes:
                print("   ❌ Sin horarios disponibles")
            else:
                for showtime_id, theater_id, datetime_str, price, is_imax, theater_name in showtimes:
                    imax_text = " (IMAX)" if is_imax else ""
                    print(f"   ✅ ID: {showtime_id:2d} | {theater_name:15s}{imax_text:7s} | {datetime_str} | ${price}")
        
        # Verificar endpoint de la API
        print("\n🌐 VERIFICACIÓN DE ENDPOINTS:")
        print("-" * 50)
        
        # Simular la respuesta del endpoint de horarios
        query_all_showtimes = """
        SELECT showtime_id, movie_id, theater_id, datetime, base_price, available_seats, is_3d, is_imax
        FROM showtimes
        ORDER BY movie_id, datetime
        """
        
        cursor.execute(query_all_showtimes)
        all_showtimes = cursor.fetchall()
        
        print("Horarios que debería devolver /showtimes/all:")
        for row in all_showtimes:
            showtime_id, movie_id, theater_id, datetime_str, price, available, is_3d, is_imax = row
            print(f"   showtime_id: {showtime_id}, movie_id: {movie_id}, theater_id: {theater_id}, datetime: {datetime_str}")
        
    except mysql.connector.Error as e:
        print(f"❌ Error en consulta: {e}")
    
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    verify_movies_and_showtimes()
