from fastapi import HTTPException
from database.crud_tables.movies import search_movies, MySQLConnection
import traceback

def search_movies_controller(data: dict):
    db = MySQLConnection()
    try:
        required_fields = ["search_term"]
        missing_fields = [
            field for field in required_fields
            if field not in data or data.get(field) is None or data.get(field) == ""
        ]
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Error de validación",
                    "missing_fields": missing_fields
                }
            )
        
        search_term = data.get("search_term")
        genre_id = data.get("genre_id", "all")
        
        movies = search_movies(db, search_term, genre_id)
        return {"movies": movies}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in search_movies_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
