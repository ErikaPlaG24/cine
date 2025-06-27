from fastapi import HTTPException
from database.crud_tables.theaters import get_theater_by_id, MySQLConnection
import traceback

def get_theater_by_id_controller(data: dict):
    db = MySQLConnection()
    try:
        required_fields = ["theater_id"]
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
        
        theater_id = data.get("theater_id")
        theater = get_theater_by_id(db, theater_id)
        
        if not theater:
            raise HTTPException(
                status_code=404,
                detail="Teatro no encontrado."
            )
        
        return {"theater": theater}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_theater_by_id_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
