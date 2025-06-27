from fastapi import HTTPException
from database.crud_tables.reserved_seats import get_all_reserved_seats, MySQLConnection
import traceback

def get_all_reserved_seats_controller(data: dict):
    db = MySQLConnection()
    try:
        reserved_seats = get_all_reserved_seats(db)
        return {"reserved_seats": reserved_seats}
    except Exception as e:
        print(f"Error in get_all_reserved_seats_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
