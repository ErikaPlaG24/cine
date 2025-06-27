from database.mysql_connection import MySQLConnection

def get_all_movie_genres(db: MySQLConnection):
    db.execute("SELECT * FROM movie_genres")
    return db.fetchall()

def get_movie_genres_by_movie_id(db: MySQLConnection, movie_id):
    db.execute("SELECT * FROM movie_genres WHERE movie_id = %s", (movie_id,))
    return db.fetchall()

def add_movie_genre(db: MySQLConnection, movie_id, genre_id):
    db.execute("INSERT INTO movie_genres (movie_id, genre_id) VALUES (%s, %s)", (movie_id, genre_id))
    db.commit()

def delete_movie_genre(db: MySQLConnection, movie_id, genre_id):
    db.execute("DELETE FROM movie_genres WHERE movie_id = %s AND genre_id = %s", (movie_id, genre_id))
    db.commit()
