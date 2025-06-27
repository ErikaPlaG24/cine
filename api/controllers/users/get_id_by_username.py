from fastapi import HTTPException
from database.crud_tables.users import get_id_by_username, MySQLConnection
import traceback

def get_id_by_username_controller(data: dict):
    db = MySQLConnection()
    try:
        username = data.get("username")
        if not username:
            raise HTTPException(status_code=400, detail="El campo 'username' es obligatorio.")
        user_id = get_id_by_username(db, username)
        if user_id is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        return {"user_id": user_id}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_id_by_username_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
