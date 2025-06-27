from fastapi import HTTPException
from database.crud_tables.users import *
import traceback

def get_all_active_users_controller(data: dict):
    db = MySQLConnection()
    
    try:
        roles = data.get("roles", None)
        
        if not roles:
            raise HTTPException(status_code=400, detail="El campo 'roles' es obligatorio.")
        
        if roles != "all" and not isinstance(roles, (list, tuple)):
            raise HTTPException(status_code=400, detail="El campo 'roles' debe ser una lista, tupla o 'all'.")
    
        if roles != "all":
            invalid_roles = set(roles) - {'admin', 'employee', 'customer'}
            if invalid_roles:
                raise HTTPException(status_code=400, detail=f"Roles inválidos: {', '.join(invalid_roles)}. Se aceptan roles: 'admin', 'employee', 'customer'.")

        return get_all_active_users(db, roles)

    except HTTPException: # Permite que FastAPI maneje HTTPException correctamente
        raise
    except Exception as e:
        print(f"Error in get_all_users_controller: {e}")
        traceback.print_exc()  # Imprime el traceback completo
        raise HTTPException(status_code=500, detail="Internal Server Error")
