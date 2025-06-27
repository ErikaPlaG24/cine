from database.mysql_connection import MySQLConnection

def get_all_movies(db: MySQLConnection):
    db.execute("SELECT * FROM movies")
    return db.fetchall()

def get_movie_by_id(db: MySQLConnection, movie_id):
    db.execute("SELECT * FROM movies WHERE id = %s", (movie_id,))
    return db.fetchone()

def create_movie(db: MySQLConnection, **kwargs):
    keys = []
    values = []
    for k, v in kwargs.items():
        keys.append(k)
        values.append(v)
    columns = ', '.join(keys)
    placeholders = ', '.join(['%s'] * len(keys))
    db.execute(f"INSERT INTO movies ({columns}) VALUES ({placeholders})", tuple(values))
    db.commit()

def update_movie_by_id(db: MySQLConnection, movie_id, **kwargs):
    updates = []
    values = []
    for k, v in kwargs.items():
        updates.append(f"{k} = %s")
        values.append(v)
    if not updates:
        raise ValueError("No se proporcionaron campos válidos para actualizar.")
    query = f"UPDATE movies SET {', '.join(updates)} WHERE id = %s"
    values.append(movie_id)
    db.execute(query, tuple(values))
    db.commit()

def delete_movie_by_id(db: MySQLConnection, movie_id):
    db.execute("DELETE FROM movies WHERE id = %s", (movie_id,))
    db.commit()

def search_movies(db: MySQLConnection, search_term, genre_id="all"):
    """
    Busca películas por coincidencia parcial en título, título original u overview.
    Puede filtrar por genre_id (int o lista de int) o 'all' para todos los géneros.
    """
    search = f"%{search_term}%"
    base_query = """
        SELECT m.*
        FROM movies m
        """
    params = []

    if genre_id != "all":
        # Permitir lista o int
        if isinstance(genre_id, (list, tuple)):
            placeholders = ','.join(['%s'] * len(genre_id))
            base_query += f"""
                JOIN movie_genres mg ON m.id = mg.movie_id
                WHERE (m.title LIKE %s OR m.original_title LIKE %s OR m.overview LIKE %s)
                AND mg.genre_id IN ({placeholders})
            """
            params.extend([search, search, search])
            params.extend(genre_id)
        else:
            base_query += """
                JOIN movie_genres mg ON m.id = mg.movie_id
                WHERE (m.title LIKE %s OR m.original_title LIKE %s OR m.overview LIKE %s)
                AND mg.genre_id = %s
            """
            params.extend([search, search, search, genre_id])
    else:
        base_query += """
            WHERE (m.title LIKE %s OR m.original_title LIKE %s OR m.overview LIKE %s)
        """
        params.extend([search, search, search])

    base_query += " ORDER BY m.title"
    db.execute(base_query, tuple(params))
    return db.fetchall()
