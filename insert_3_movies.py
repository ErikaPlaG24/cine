#!/usr/bin/env python3
"""
Script para insertar exactamente 3 películas en la base de datos
"""

import mysql.connector
from mysql.connector import Error

def connect_to_database():
    """Conectar a la base de datos MySQL"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            database='cine',
            user='root',
            password='root'
        )
        
        if connection.is_connected():
            print("✅ Conexión exitosa a MySQL")
            return connection
            
    except Error as e:
        print(f"❌ Error conectando a MySQL: {e}")
        return None

def clear_and_insert_movies():
    """Limpiar tabla de películas e insertar exactamente 3 películas"""
    connection = connect_to_database()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        # Limpiar tabla de películas
        print("🧹 Limpiando tabla de películas...")
        cursor.execute("DELETE FROM movies")
        
        # Insertar exactamente 3 películas
        movies = [
            (1, "Avatar: El Camino del Agua", "Ciencia ficción", 192, "La familia Sully se enfrenta a nuevos desafíos", "https://example.com/avatar2.jpg"),
            (2, "Top Gun: Maverick", "Acción", 131, "Pete 'Maverick' Mitchell regresa para entrenar a una nueva generación de pilotos", "https://example.com/topgun.jpg"),
            (3, "Spider-Man: No Way Home", "Superhéroes", 148, "Peter Parker debe enfrentar villanos del multiverso", "https://example.com/spiderman.jpg")
        ]
        
        insert_query = """
        INSERT INTO movies (movie_id, title, genre, duration_minutes, description, poster_url) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        cursor.executemany(insert_query, movies)
        connection.commit()
        
        print(f"✅ Se insertaron {cursor.rowcount} películas exitosamente")
        
        # Verificar que las películas se insertaron
        cursor.execute("SELECT movie_id, title, genre, duration_minutes FROM movies ORDER BY movie_id")
        movies_in_db = cursor.fetchall()
        
        print("\n📽️ Películas en la base de datos:")
        for movie in movies_in_db:
            print(f"  ID: {movie[0]} | Título: {movie[1]} | Género: {movie[2]} | Duración: {movie[3]} min")
            
    except Error as e:
        print(f"❌ Error ejecutando consulta: {e}")
        connection.rollback()
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("🔌 Conexión cerrada")

if __name__ == "__main__":
    print("🎬 Insertando exactamente 3 películas...")
    clear_and_insert_movies()
