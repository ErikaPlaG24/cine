from fastapi import HTTPException
from database.crud_tables.showtimes import get_all_showtimes, MySQLConnection
import traceback

def get_all_showtimes_controller(data: dict):
    db = MySQLConnection()
    try:
        showtimes = get_all_showtimes(db)
        return {"showtimes": showtimes}
    except Exception as e:
        print(f"Error in get_all_showtimes_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
