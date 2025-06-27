from fastapi import HTTPException
from database.crud_tables.theaters import get_all_theaters, MySQLConnection
import traceback

def get_all_theaters_controller(data: dict):
    db = MySQLConnection()
    try:
        theaters = get_all_theaters(db)
        return {"theaters": theaters}
    except Exception as e:
        print(f"Error in get_all_theaters_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
