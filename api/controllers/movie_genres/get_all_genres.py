from fastapi import HTTPException
from database.crud_tables.genres import get_all_genres, MySQLConnection
import traceback

def get_all_genres_controller(data: dict):
    db = MySQLConnection()
    try:
        genres = get_all_genres(db)
        return {"genres": genres}
    except Exception as e:
        print(f"Error in get_all_genres_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
