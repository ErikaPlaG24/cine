from fastapi import HTTPException
from database.crud_tables.sales import get_sale_by_id, MySQLConnection
import traceback

def get_sale_by_id_controller(data: dict):
    db = MySQLConnection()
    try:
        required_fields = ["sale_id"]
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
        
        sale_id = data.get("sale_id")
        sale = get_sale_by_id(db, sale_id)
        
        if not sale:
            raise HTTPException(
                status_code=404,
                detail="Venta no encontrada."
            )
        
        return {"sale": sale}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_sale_by_id_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
