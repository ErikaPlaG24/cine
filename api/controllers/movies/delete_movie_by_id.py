from fastapi import HTTPException
from database.crud_tables.movies import delete_movie_by_id, MySQLConnection
import traceback

def delete_movie_by_id_controller(data: dict):
    db = MySQLConnection()
    try:
        required_fields = ["movie_id"]
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
        
        movie_id = data.get("movie_id")
        delete_movie_by_id(db, movie_id)
        
        return {"message": "Película eliminada exitosamente."}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in delete_movie_by_id_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
