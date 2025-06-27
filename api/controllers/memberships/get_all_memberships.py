from fastapi import HTTPException
from database.crud_tables.memberships import get_all_memberships, MySQLConnection
import traceback

def get_all_memberships_controller(data: dict):
    db = MySQLConnection()
    try:
        memberships = get_all_memberships(db)
        return {"memberships": memberships}
    except Exception as e:
        print(f"Error in get_all_memberships_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
