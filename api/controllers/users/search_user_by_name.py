from fastapi import HTTPException
from database.crud_tables.users import search_user_by_name, MySQLConnection
import traceback

def search_user_by_name_controller(data: dict):
    db = MySQLConnection()
    try:
        search_term = data.get("search_term")
        roles = data.get("roles", "all")
        if not search_term:
            raise HTTPException(status_code=400, detail="El campo 'search_term' es obligatorio.")
        return search_user_by_name(db, search_term, roles)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in search_user_by_name_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
