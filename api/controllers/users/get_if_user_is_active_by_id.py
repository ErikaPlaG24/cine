from fastapi import HTTPException
from database.crud_tables.users import get_if_user_is_active_by_id, MySQLConnection
import traceback

def get_if_user_is_active_by_id_controller(data: dict):
    db = MySQLConnection()
    try:
        user_id = data.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="El campo 'user_id' es obligatorio.")
        is_active = get_if_user_is_active_by_id(db, user_id)
        return {"is_active": is_active}
    except HTTPException:
        raise
    except ValueError as ve:
        print(f"ValueError in get_if_user_is_active_by_id_controller: {ve}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error in get_if_user_is_active_by_id_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
