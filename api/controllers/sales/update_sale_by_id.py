from fastapi import HTTPException
from database.crud_tables.sales import update_sale_by_id, MySQLConnection
import traceback

def update_sale_by_id_controller(data: dict):
    db = MySQLConnection()
    try:
        if "sale_id" not in data:
            raise HTTPException(
                status_code=400,
                detail="sale_id es requerido."
            )
        
        sale_id = data.pop("sale_id")
        
        # Campos válidos que se pueden actualizar
        valid_fields = ["user_id", "showtime_id", "quantity", "total_price", "sale_date"]
        update_data = {k: v for k, v in data.items() if k in valid_fields and v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No se proporcionaron campos válidos para actualizar."
            )
        
        update_sale_by_id(db, sale_id, **update_data)
        return {"message": "Venta actualizada exitosamente."}
    except HTTPException:
        raise
    except ValueError as ve:
        print(f"ValueError in update_sale_by_id_controller: {ve}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error in update_sale_by_id_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
