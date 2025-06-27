from fastapi import HTTPException
from database.crud_tables.users import update_user_by_id, MySQLConnection
import traceback
from mysql.connector.errors import Error as MySQLError

def update_user_by_id_controller(data: dict):
    db = MySQLConnection()
    try:
        user_id = data.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="El campo 'user_id' es obligatorio.")
        update_fields = {k: data.get(k) for k in ["username", "password", "first_name", "last_name", "phone", "role", "is_active"]}
        update_user_by_id(db, user_id, **update_fields)
        return {"message": "Usuario actualizado exitosamente."}
    except HTTPException:
        raise
    except MySQLError as e:
        print(f"MySQL error in update_user_by_id_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error de base de datos")
    except ValueError as ve:
        print(f"ValueError in update_user_by_id_controller: {ve}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error in update_user_by_id_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
