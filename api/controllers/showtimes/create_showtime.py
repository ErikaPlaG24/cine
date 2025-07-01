from fastapi import HTTPException
from database.crud_tables.showtimes import create_showtime, MySQLConnection
import traceback

def create_showtime_controller(data: dict):
    db = MySQLConnection()
    try:
        required_fields = ["movie_id", "theater_id", "datetime"]
        optional_fields = ["base_price", "available_seats", "is_3d", "is_imax"]
        
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
        showtime_data = {}
        if data.get("movie_id"):
            showtime_data["movie_id"] = data["movie_id"]
        if data.get("theater_id"):
            showtime_data["theater_id"] = data["theater_id"]
        if data.get("datetime"):
            showtime_data["datetime"] = data["datetime"]
        if data.get("base_price"):
            showtime_data["base_price"] = data["base_price"]
        if data.get("available_seats"):
            showtime_data["available_seats"] = data["available_seats"]
        if data.get("is_3d"):
            showtime_data["is_3d"] = data["is_3d"]
        if data.get("is_imax"):
            showtime_data["is_imax"] = data["is_imax"]
        
        create_showtime(db, **showtime_data)
        return {"message": "Función creada exitosamente."}
    except HTTPException:
        raise
    except ValueError as ve:
        print(f"ValueError in create_showtime_controller: {ve}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error in create_showtime_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
