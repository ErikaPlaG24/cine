from fastapi import HTTPException
from database.crud_tables.users import get_if_user_exists, MySQLConnection
import traceback

def get_if_user_exists_controller(data: dict):
    db = MySQLConnection()
    try:
        username = data.get("username")
        if not username:
            raise HTTPException(status_code=400, detail="El campo 'username' es obligatorio.")
        exists = get_if_user_exists(db, username)
        return {"exists": exists}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_if_user_exists_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
