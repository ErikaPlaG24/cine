from fastapi import HTTPException
from database.crud_tables.movies import get_all_movies, MySQLConnection
import traceback

def get_all_movies_controller(data: dict):
    db = MySQLConnection()
    try:
        movies = get_all_movies(db)
        return {"movies": movies}
    except Exception as e:
        print(f"Error in get_all_movies_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
