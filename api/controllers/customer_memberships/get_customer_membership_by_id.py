from fastapi import HTTPException
from database.crud_tables.customer_memberships import get_customer_membership_by_id, MySQLConnection
import traceback

def get_customer_membership_by_id_controller(data: dict):
    db = MySQLConnection()
    try:
        required_fields = ["customer_membership_id"]
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
        
        customer_membership_id = data.get("customer_membership_id")
        customer_membership = get_customer_membership_by_id(db, customer_membership_id)
        
        if not customer_membership:
            raise HTTPException(
                status_code=404,
                detail="Membresía de cliente no encontrada."
            )
        
        return {"customer_membership": customer_membership}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_customer_membership_by_id_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
