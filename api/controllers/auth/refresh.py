from fastapi import HTTPException
from database.crud_tables.users import *
from helpers.hash import verify_password
from helpers.token import *
import traceback

def refresh_token_controller(data: dict):
    db = MySQLConnection()
    
    try:
        refresh_token = data.get("refresh_token")
        
        if not refresh_token:
            raise HTTPException(status_code=400, detail="El campo 'refresh_token' es obligatorio.")
        
        # Decodificar el token de actualización
        payload = decode_token(refresh_token, JWT_REFRESH_SECRET_KEY)
        if not payload:
            raise HTTPException(status_code=401, detail="Token de actualización inválido")
    
        #
        #  GENERAR UN NUEVO TOKEN
        #
    
        username = payload.get("username")
        
        # Verificar que el usuario exista
        if get_if_user_exists(db, username) is False:
            raise HTTPException(status_code=404, detail="El usuario no existe.")
        
        id_user = get_id_by_username(db, username)
        
        # Verificar que el usuario no esté bloqueado
        if not get_if_user_is_active_by_id(db, id_user):
            raise HTTPException(status_code=403, detail="El usuario está bloqueado.")
        
        # Obtener el id del usuario
        role = get_value_from_user_by_id(db, id_user, "role")
        
        # Verificar que el usuario no haya cambiado su contraseña
        token_password_date = get_token_expiration(refresh_token)
        password_updated_at = get_password_updated_at_by_id(db, id_user)
        
        print(f"Token password date: {token_password_date}")
        print(f"Password updated at: {password_updated_at}")

        if password_updated_at > token_password_date:
            raise HTTPException(status_code=403, detail="La contraseña ha sido cambiada. Inicie sesión nuevamente.")

        user_data = {
            "username": username,
            "role": role,
        }
        
        return {
            "access_token": create_access_token(user_data),
        }

    except HTTPException: # Permite que FastAPI maneje HTTPException correctamente
        raise
    except Exception as e:
        print(f"Error in refresh_controller: {e}")
        traceback.print_exc()  # Imprime el traceback completo
        raise HTTPException(status_code=500, detail="Internal Server Error")
        raise HTTPException(status_code=500, detail="Internal Server Error")
