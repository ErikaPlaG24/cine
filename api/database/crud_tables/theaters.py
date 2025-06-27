from database.mysql_connection import MySQLConnection

def get_all_theaters(db: MySQLConnection):
    db.execute("SELECT * FROM theaters")
    return db.fetchall()

def get_theater_by_id(db: MySQLConnection, theater_id):
    db.execute("SELECT * FROM theaters WHERE theater_id = %s", (theater_id,))
    return db.fetchone()

def create_theater(db: MySQLConnection, name, capacity, has_3d=False, has_dolby=False, is_imax=False):
    db.execute(
        """
        INSERT INTO theaters (name, capacity, has_3d, has_dolby, is_imax)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (name, capacity, has_3d, has_dolby, is_imax)
    )
    db.commit()

def update_theater_by_id(db: MySQLConnection, theater_id, **kwargs):
    updates = []
    values = []
    for k, v in kwargs.items():
        updates.append(f"{k} = %s")
        values.append(v)
    if not updates:
        raise ValueError("No se proporcionaron campos válidos para actualizar.")
    query = f"UPDATE theaters SET {', '.join(updates)} WHERE theater_id = %s"
    values.append(theater_id)
    db.execute(query, tuple(values))
    db.commit()

def delete_theater_by_id(db: MySQLConnection, theater_id):
    db.execute("DELETE FROM theaters WHERE theater_id = %s", (theater_id,))
    db.commit()
