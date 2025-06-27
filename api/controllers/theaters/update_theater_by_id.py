from fastapi import HTTPException
from database.crud_tables.theaters import update_theater_by_id, MySQLConnection
import traceback

def update_theater_by_id_controller(data: dict):
    db = MySQLConnection()
    try:
        if "theater_id" not in data:
            raise HTTPException(
                status_code=400,
                detail="theater_id es requerido."
            )
        
        theater_id = data.pop("theater_id")
        
        # Campos válidos que se pueden actualizar
        valid_fields = ["name", "capacity", "has_3d", "has_dolby", "is_imax"]
        update_data = {k: v for k, v in data.items() if k in valid_fields and v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No se proporcionaron campos válidos para actualizar."
            )
        
        update_theater_by_id(db, theater_id, **update_data)
        return {"message": "Teatro actualizado exitosamente."}
    except HTTPException:
        raise
    except ValueError as ve:
        print(f"ValueError in update_theater_by_id_controller: {ve}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error in update_theater_by_id_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
