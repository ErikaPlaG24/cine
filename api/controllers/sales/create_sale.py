from fastapi import HTTPException
from database.crud_tables.sales import create_sale, MySQLConnection
import traceback

def create_sale_controller(data: dict):
    db = MySQLConnection()
    try:
        required_fields = ["user_id", "showtime_id", "quantity", "total_price"]
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
        
        # Campos válidos para crear venta
        valid_fields = ["user_id", "showtime_id", "quantity", "total_price", "sale_date"]
        sale_data = {k: v for k, v in data.items() if k in valid_fields}
        
        create_sale(db, **sale_data)
        return {"message": "Venta creada exitosamente."}
    except HTTPException:
        raise
    except ValueError as ve:
        print(f"ValueError in create_sale_controller: {ve}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error in create_sale_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
