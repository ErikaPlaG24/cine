from fastapi import HTTPException
from database.crud_tables.reserved_seats import get_reserved_seat_by_id, MySQLConnection
import traceback

def get_reserved_seat_by_id_controller(data: dict):
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
        reserved_seat = get_reserved_seat_by_id(db, reservation_id)
        
        if not reserved_seat:
            raise HTTPException(
                status_code=404,
                detail="Asiento reservado no encontrado."
            )
        
        return {"reserved_seat": reserved_seat}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_reserved_seat_by_id_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
