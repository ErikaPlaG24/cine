from fastapi import HTTPException
from database.crud_tables.users import get_value_from_user_by_id, MySQLConnection
import traceback
from mysql.connector import Error

def get_value_from_user_by_id_controller(data: dict):
    db = MySQLConnection()
    try:
        user_id = data.get("user_id")
        column_name = data.get("column_name")
        if not user_id or not column_name:
            raise HTTPException(status_code=400, detail="Los campos 'user_id' y 'column_name' son obligatorios.")
        value = get_value_from_user_by_id(db, user_id, column_name)
        return {column_name: value}
    except HTTPException:
        raise
    except Error as e:
        print(f"Database error in get_value_from_user_by_id_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Database Error")
    except Exception as e:
        print(f"Error in get_value_from_user_by_id_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
