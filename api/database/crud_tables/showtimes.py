from database.mysql_connection import MySQLConnection

def get_all_showtimes(db: MySQLConnection):
    query = """
        SELECT 
            s.*,
            m.title as movie_title,
            t.name as theater_name
        FROM showtimes s
        LEFT JOIN movies m ON s.movie_id = m.id
        LEFT JOIN theaters t ON s.theater_id = t.theater_id
        ORDER BY s.datetime DESC
    """
    db.execute(query)
    return db.fetchall()

def get_showtime_by_id(db: MySQLConnection, showtime_id):
    query = """
        SELECT 
            s.*,
            m.title as movie_title,
            t.name as theater_name
        FROM showtimes s
        LEFT JOIN movies m ON s.movie_id = m.id
        LEFT JOIN theaters t ON s.theater_id = t.theater_id
        WHERE s.showtime_id = %s
    """
    db.execute(query, (showtime_id,))
    return db.fetchone()

def create_showtime(db: MySQLConnection, **kwargs):
    keys = []
    values = []
    for k, v in kwargs.items():
        keys.append(k)
        values.append(v)
    columns = ', '.join(keys)
    placeholders = ', '.join(['%s'] * len(keys))
    db.execute(f"INSERT INTO showtimes ({columns}) VALUES ({placeholders})", tuple(values))
    db.commit()

def update_showtime_by_id(db: MySQLConnection, showtime_id, **kwargs):
    updates = []
    values = []
    for k, v in kwargs.items():
        updates.append(f"{k} = %s")
        values.append(v)
    if not updates:
        raise ValueError("No se proporcionaron campos válidos para actualizar.")
    query = f"UPDATE showtimes SET {', '.join(updates)} WHERE showtime_id = %s"
    values.append(showtime_id)
    db.execute(query, tuple(values))
    db.commit()

def delete_showtime_by_id(db: MySQLConnection, showtime_id):
    db.execute("DELETE FROM showtimes WHERE showtime_id = %s", (showtime_id,))
    db.commit()
