from fastapi import HTTPException
from database.crud_tables.users import get_user_by_id, MySQLConnection
import traceback

def get_user_by_id_controller(data: dict):
    db = MySQLConnection()
    try:
        required_fields = ["user_id"]
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
        
        user_id = data.get("user_id")
        user = get_user_by_id(db, user_id)
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail="Usuario no encontrado."
            )
        
        return {"user": user}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_user_by_id_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
