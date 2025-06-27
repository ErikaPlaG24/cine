from fastapi import HTTPException
from database.crud_tables.users import delete_user_by_id, MySQLConnection, get_if_user_exists, get_value_from_user_by_id
import traceback

def delete_user_by_id_controller(data: dict):
    db = MySQLConnection()
    try:
        user_id = data.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="El campo 'user_id' es obligatorio.")
        
        # Check if the user exists
        username = get_value_from_user_by_id(db, user_id, "username")
        existing_user = get_if_user_exists(db, username)
        if not existing_user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        
        if user_id == 1:
            raise HTTPException(status_code=400, detail="Ups! buen intento, pero no puedes borrar a este usuario.")
        
        delete_user_by_id(db, user_id)
        return {"message": "Usuario eliminado exitosamente."}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in delete_user_by_id_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
