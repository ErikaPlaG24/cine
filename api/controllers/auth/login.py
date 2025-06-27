from fastapi import HTTPException
from database.crud_tables.users import *
from helpers.hash import verify_password
from helpers.token import *
import traceback

def login_controller(data: dict):
    db = MySQLConnection()
    
    try:
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            raise HTTPException(status_code=400, detail="Los campos 'username' y 'password' son obligatorios.")
        
        # Obtener el id del usuario
        id_user = get_id_by_username(db, username)

        # Verificar que el usuario exista
        if get_if_user_exists(db, username) is False:
            raise HTTPException(status_code=404, detail="El usuario no existe.")
        
        # Verificar que el usuario no esté bloqueado
        if not get_if_user_is_active_by_id(db, id_user):
            raise HTTPException(status_code=403, detail="El usuario está bloqueado.")
        
        # Obtener la contraseña del usuario
        user_password = get_hashed_password_by_id(db, id_user)
        # Convertir a bytes si es str
        if isinstance(user_password, str):
            user_password = user_password.encode('utf-8')
        
        # Verificar la contraseña
        if not verify_password(password, user_password):
            raise HTTPException(status_code=401, detail="Contraseña incorrecta.")
        
        # Obtener fecha de actualización de contraseña
        password_updated_at = get_password_updated_at_by_id(db, id_user)
        
        role = get_value_from_user_by_id(db, id_user, "role")
        
        user_data = {
            "username": username,
            "role": role,
        }
        
        return {
            "access_token": create_access_token(user_data),
            "refresh_token": create_refresh_token(user_data),
        }

    except HTTPException: # Permite que FastAPI maneje HTTPException correctamente
        raise
    except Exception as e:
        print(f"Error in login_controller: {e}")
        traceback.print_exc()  # Imprime el traceback completo
        raise HTTPException(status_code=500, detail="Internal Server Error")
