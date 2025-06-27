from fastapi import HTTPException
from database.crud_tables.customer_memberships import get_all_customer_memberships, MySQLConnection
import traceback

def get_all_customer_memberships_controller(data: dict):
    db = MySQLConnection()
    try:
        customer_memberships = get_all_customer_memberships(db)
        return {"customer_memberships": customer_memberships}
    except Exception as e:
        print(f"Error in get_all_customer_memberships_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
