from fastapi import HTTPException
from database.crud_tables.showtimes import update_showtime_by_id, MySQLConnection
import traceback

def update_showtime_by_id_controller(data: dict):
    db = MySQLConnection()
    try:
        if "showtime_id" not in data:
            raise HTTPException(
                status_code=400,
                detail="showtime_id es requerido."
            )
        
        showtime_id = data.pop("showtime_id")
        
        # Campos válidos que se pueden actualizar
        valid_fields = ["movie_id", "theater_id", "showtime", "price"]
        update_data = {k: v for k, v in data.items() if k in valid_fields and v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No se proporcionaron campos válidos para actualizar."
            )
        
        update_showtime_by_id(db, showtime_id, **update_data)
        return {"message": "Función actualizada exitosamente."}
    except HTTPException:
        raise
    except ValueError as ve:
        print(f"ValueError in update_showtime_by_id_controller: {ve}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error in update_showtime_by_id_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
