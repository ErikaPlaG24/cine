from fastapi import HTTPException
from database.crud_tables.showtimes import get_showtime_by_id, MySQLConnection
import traceback

def get_showtime_by_id_controller(data: dict):
    db = MySQLConnection()
    try:
        required_fields = ["showtime_id"]
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
        
        showtime_id = data.get("showtime_id")
        showtime = get_showtime_by_id(db, showtime_id)
        
        if not showtime:
            raise HTTPException(
                status_code=404,
                detail="Función no encontrada."
            )
        
        return {"showtime": showtime}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_showtime_by_id_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
