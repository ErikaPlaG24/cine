from fastapi import HTTPException
from database.crud_tables.genres import get_genre_by_id, MySQLConnection
import traceback

def get_genre_by_id_controller(data: dict):
    db = MySQLConnection()
    try:
        required_fields = ["genre_id"]
        missing_fields = [
            field for field in required_fields
            if field not in data or data.get(field) is None
        ]
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Error de validación",
                    "missing_fields": missing_fields
                }
            )
        
        genre_id = data.get("genre_id")
        genre = get_genre_by_id(db, genre_id)
        
        if not genre:
            raise HTTPException(
                status_code=404,
                detail="Género no encontrado."
            )
        
        return {"genre": genre}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_genre_by_id_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
