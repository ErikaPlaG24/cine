from fastapi import HTTPException
from database.crud_tables.movies import create_movie, MySQLConnection
import traceback

def create_movie_controller(data: dict):
    db = MySQLConnection()
    try:
        required_fields = ["title", "original_title", "overview", "release_date", "runtime", "popularity", "vote_average", "vote_count", "poster_path", "backdrop_path"]
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
        
        # Crear película con todos los campos recibidos
        movie_data = {k: v for k, v in data.items() if k in required_fields}
        create_movie(db, **movie_data)
        
        return {"message": "Película creada exitosamente."}
    except HTTPException:
        raise
    except ValueError as ve:
        print(f"ValueError in create_movie_controller: {ve}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error in create_movie_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
