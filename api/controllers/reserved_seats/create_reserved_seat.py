from fastapi import HTTPException
from database.crud_tables.reserved_seats import create_reserved_seat, MySQLConnection
import traceback

def create_reserved_seat_controller(data: dict):
    db = MySQLConnection()
    try:
        required_fields = ["sale_id", "seat_number"]
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
        
        sale_id = data.get("sale_id")
        seat_number = data.get("seat_number")
        
        create_reserved_seat(db, sale_id, seat_number)
        return {"message": "Asiento reservado exitosamente."}
    except HTTPException:
        raise
    except ValueError as ve:
        print(f"ValueError in create_reserved_seat_controller: {ve}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error in create_reserved_seat_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
