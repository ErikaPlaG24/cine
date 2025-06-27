from database.mysql_connection import MySQLConnection


def get_all_genres(db: MySQLConnection):
    db.execute("SELECT * FROM genres")
    return db.fetchall()

def get_genre_by_id(db: MySQLConnection, genre_id):
    db.execute("SELECT * FROM genres WHERE id = %s", (genre_id,))
    return db.fetchone()

def create_genre(db: MySQLConnection, genre_id, name):
    db.execute("INSERT INTO genres (id, name) VALUES (%s, %s)", (genre_id, name))
    db.commit()

def update_genre_by_id(db: MySQLConnection, genre_id, name=None):
    if name is None:
        raise ValueError("No se proporcionaron campos válidos para actualizar.")
    db.execute("UPDATE genres SET name = %s WHERE id = %s", (name, genre_id))
    db.commit()

def delete_genre_by_id(db: MySQLConnection, genre_id):
    db.execute("DELETE FROM genres WHERE id = %s", (genre_id,))
    db.commit()
