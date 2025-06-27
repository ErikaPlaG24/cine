from fastapi import HTTPException
from database.crud_tables.sales import get_all_sales, MySQLConnection
import traceback

def get_all_sales_controller(data: dict):
    db = MySQLConnection()
    try:
        sales = get_all_sales(db)
        return {"sales": sales}
    except Exception as e:
        print(f"Error in get_all_sales_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
