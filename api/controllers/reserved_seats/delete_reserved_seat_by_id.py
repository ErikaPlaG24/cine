from fastapi import HTTPException
from database.crud_tables.reserved_seats import delete_reserved_seat_by_id, MySQLConnection
import traceback

def delete_reserved_seat_by_id_controller(data: dict):
    db = MySQLConnection()
    try:
        required_fields = ["reservation_id"]
        missing_fields = [
            field for field in required_fields
            if field not in data or data.get(field) is None
        ]
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Error de validación",
                    "missing_fields": missing_fields
                }
            )
        
        reservation_id = data.get("reservation_id")
        delete_reserved_seat_by_id(db, reservation_id)
        
        return {"message": "Asiento reservado eliminado exitosamente."}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in delete_reserved_seat_by_id_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
