#!/usr/bin/env python3
"""
Script para agregar horarios faltantes a las películas
"""

import mysql.connector
from datetime import datetime, timedelta

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

def insert_showtimes():
    """Inserta horarios para las películas faltantes"""
    connection = connect_to_database()
    if not connection:
        return
    
    cursor = connection.cursor()
    
    # Horarios para Misión: Imposible - La sentencia final (movie_id = 12)
    showtimes_mission = [
        {
            'movie_id': 12,
            'theater_id': 1,  # Sala Premium 1
            'datetime': '2024-12-30 16:00:00',
            'base_price': 75.00,
            'available_seats': 25,
            'is_3d': 0,
            'is_imax': 0
        },
        {
            'movie_id': 12,
            'theater_id': 3,  # Sala IMAX
            'datetime': '2024-12-30 21:30:00',
            'base_price': 85.00,
            'available_seats': 40,
            'is_3d': 0,
            'is_imax': 1
        }
    ]
    
    # Horarios para K.O. (movie_id = 13)
    showtimes_ko = [
        {
            'movie_id': 13,
            'theater_id': 2,  # Sala Premium 2
            'datetime': '2024-12-30 17:30:00',
            'base_price': 70.00,
            'available_seats': 30,
            'is_3d': 0,
            'is_imax': 0
        },
        {
            'movie_id': 13,
            'theater_id': 1,  # Sala Premium 1
            'datetime': '2024-12-30 22:00:00',
            'base_price': 70.00,
            'available_seats': 25,
            'is_3d': 0,
            'is_imax': 0
        }
    ]
    
    all_showtimes = showtimes_mission + showtimes_ko
    
    try:
        insert_query = """
        INSERT INTO showtimes 
        (movie_id, theater_id, datetime, base_price, available_seats, is_3d, is_imax, created_by_user_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        for showtime in all_showtimes:
            values = (
                showtime['movie_id'],
                showtime['theater_id'],
                showtime['datetime'],
                showtime['base_price'],
                showtime['available_seats'],
                showtime['is_3d'],
                showtime['is_imax'],
                1  # created_by_user_id (asumimos usuario admin con ID 1)
            )
            
            cursor.execute(insert_query, values)
            print(f"✓ Insertado horario para película {showtime['movie_id']} en sala {showtime['theater_id']} a las {showtime['datetime']}")
        
        connection.commit()
        print(f"\n✅ Se insertaron {len(all_showtimes)} horarios exitosamente")
        
    except mysql.connector.Error as e:
        print(f"❌ Error insertando horarios: {e}")
        connection.rollback()
    
    finally:
        cursor.close()
        connection.close()

def verify_showtimes():
    """Verifica los horarios insertados"""
    connection = connect_to_database()
    if not connection:
        return
    
    cursor = connection.cursor()
    
    try:
        query = """
        SELECT s.showtime_id, m.title, t.name, s.datetime, s.base_price, s.is_imax
        FROM showtimes s
        JOIN movies m ON s.movie_id = m.id
        JOIN theaters t ON s.theater_id = t.theater_id
        ORDER BY m.title, s.datetime
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        print("\n📋 Horarios en la base de datos:")
        print("-" * 80)
        for row in results:
            showtime_id, title, theater, datetime_str, price, is_imax = row
            imax_text = " (IMAX)" if is_imax else ""
            print(f"ID: {showtime_id:2d} | {title:35s} | {theater:15s}{imax_text:7s} | {datetime_str} | ${price}")
        
    except mysql.connector.Error as e:
        print(f"❌ Error verificando horarios: {e}")
    
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    print("🎬 Insertando horarios faltantes para las películas...")
    insert_showtimes()
    verify_showtimes()
