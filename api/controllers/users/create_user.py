from fastapi import HTTPException
from database.crud_tables.users import create_user, MySQLConnection, get_if_user_exists
import traceback

def create_user_controller(data: dict):
    db = MySQLConnection()
    try:
        required_fields = ["username", "password", "role"]
        missing_fields = [
            field for field in required_fields
            if field not in data or data.get(field) is None or data.get(field) == ""
        ]
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Error de validación",
                    "missing_fields": missing_fields
                }
            )
        username = data.get("username")
        password = data.get("password")
        role = data.get("role")
        
        # Campos opcionales con valores por defecto
        first_name = data.get("first_name", "Usuario")
        last_name = data.get("last_name", "Sistema")
        phone = data.get("phone", "0000000000")
        
        # Cheack if the user already exists
        existing_user = get_if_user_exists(db, username)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="El usuario ya existe."
            )
        
        create_user(db, username, password, first_name, last_name, phone, role)
        return {"message": "Usuario creado exitosamente."}
    except HTTPException:
        raise
    except ValueError as ve:
        print(f"ValueError in create_user_controller: {ve}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error in create_user_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")