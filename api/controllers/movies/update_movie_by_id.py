from fastapi import HTTPException
from database.crud_tables.movies import update_movie_by_id, MySQLConnection
import traceback

def update_movie_by_id_controller(data: dict):
    db = MySQLConnection()
    try:
        if "movie_id" not in data:
            raise HTTPException(
                status_code=400,
                detail="movie_id es requerido."
            )
        
        movie_id = data.pop("movie_id")
        
        # Campos válidos que se pueden actualizar
        valid_fields = ["title", "original_title", "overview", "release_date", "runtime", "popularity", "vote_average", "vote_count", "poster_path", "backdrop_path"]
        update_data = {k: v for k, v in data.items() if k in valid_fields and v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No se proporcionaron campos válidos para actualizar."
            )
        
        update_movie_by_id(db, movie_id, **update_data)
        return {"message": "Película actualizada exitosamente."}
    except HTTPException:
        raise
    except ValueError as ve:
        print(f"ValueError in update_movie_by_id_controller: {ve}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error in update_movie_by_id_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
