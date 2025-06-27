from fastapi import HTTPException
from database.crud_tables.reserved_seats import update_reserved_seat_by_id, MySQLConnection
import traceback

def update_reserved_seat_by_id_controller(data: dict):
    db = MySQLConnection()
    try:
        if "reservation_id" not in data:
            raise HTTPException(
                status_code=400,
                detail="reservation_id es requerido."
            )
        
        reservation_id = data.get("reservation_id")
        seat_number = data.get("seat_number")
        
        if seat_number is None:
            raise HTTPException(
                status_code=400,
                detail="seat_number es requerido para actualizar."
            )
        
        update_reserved_seat_by_id(db, reservation_id, seat_number)
        return {"message": "Asiento reservado actualizado exitosamente."}
    except HTTPException:
        raise
    except ValueError as ve:
        print(f"ValueError in update_reserved_seat_by_id_controller: {ve}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error in update_reserved_seat_by_id_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
