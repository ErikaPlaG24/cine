from fastapi import HTTPException
from database.crud_tables.genres import update_genre_by_id, MySQLConnection
import traceback

def update_genre_by_id_controller(data: dict):
    db = MySQLConnection()
    try:
        if "genre_id" not in data:
            raise HTTPException(
                status_code=400,
                detail="genre_id es requerido."
            )
        
        genre_id = data.pop("genre_id")
        name = data.get("name")
        
        if name is None:
            raise HTTPException(
                status_code=400,
                detail="name es requerido para actualizar."
            )
        
        update_genre_by_id(db, genre_id, name)
        return {"message": "Género actualizado exitosamente."}
    except HTTPException:
        raise
    except ValueError as ve:
        print(f"ValueError in update_genre_by_id_controller: {ve}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error in update_genre_by_id_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
