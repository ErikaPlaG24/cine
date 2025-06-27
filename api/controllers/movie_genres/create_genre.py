from fastapi import HTTPException
from database.crud_tables.genres import create_genre, MySQLConnection
import traceback

def create_genre_controller(data: dict):
    db = MySQLConnection()
    try:
        required_fields = ["genre_id", "name"]
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
        
        genre_id = data.get("genre_id")
        name = data.get("name")
        
        create_genre(db, genre_id, name)
        return {"message": "Género creado exitosamente."}
    except HTTPException:
        raise
    except ValueError as ve:
        print(f"ValueError in create_genre_controller: {ve}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error in create_genre_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
