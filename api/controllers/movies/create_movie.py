from fastapi import HTTPException
from database.crud_tables.movies import create_movie, MySQLConnection
import traceback

def create_movie_controller(data: dict):
    db = MySQLConnection()
    try:
        required_fields = ["title"]  # Solo título es realmente obligatorio
        optional_fields = ["original_title", "overview", "release_date", "duration_minutes", "poster_url", "wallpaper_url"]
        
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
        
        # Mapear los campos del frontend a los de la base de datos
        movie_data = {}
        if data.get("title"):
            movie_data["title"] = data["title"]
        if data.get("original_title"):
            movie_data["original_title"] = data["original_title"]
        if data.get("overview"):
            movie_data["overview"] = data["overview"]
        if data.get("release_date"):
            movie_data["release_date"] = data["release_date"]
        if data.get("duration_minutes"):
            movie_data["duration_minutes"] = data["duration_minutes"]
        if data.get("poster_url"):
            movie_data["poster_url"] = data["poster_url"]
        if data.get("wallpaper_url"):
            movie_data["wallpaper_url"] = data["wallpaper_url"]
        
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
