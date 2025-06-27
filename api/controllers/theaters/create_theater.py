from fastapi import HTTPException
from database.crud_tables.theaters import create_theater, MySQLConnection
import traceback

def create_theater_controller(data: dict):
    db = MySQLConnection()
    try:
        required_fields = ["name", "capacity"]
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
        
        name = data.get("name")
        capacity = data.get("capacity")
        has_3d = data.get("has_3d", False)
        has_dolby = data.get("has_dolby", False)
        is_imax = data.get("is_imax", False)
        
        create_theater(db, name, capacity, has_3d, has_dolby, is_imax)
        return {"message": "Teatro creado exitosamente."}
    except HTTPException:
        raise
    except ValueError as ve:
        print(f"ValueError in create_theater_controller: {ve}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error in create_theater_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
