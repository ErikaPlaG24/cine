from fastapi import HTTPException
from database.crud_tables.customer_memberships import update_customer_membership_by_id, MySQLConnection
import traceback

def update_customer_membership_by_id_controller(data: dict):
    db = MySQLConnection()
    try:
        if "customer_membership_id" not in data:
            raise HTTPException(
                status_code=400,
                detail="customer_membership_id es requerido."
            )
        
        customer_membership_id = data.pop("customer_membership_id")
        
        # Campos válidos que se pueden actualizar
        valid_fields = ["user_id", "membership_id", "start_date", "end_date", "is_active"]
        update_data = {k: v for k, v in data.items() if k in valid_fields and v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No se proporcionaron campos válidos para actualizar."
            )
        
        update_customer_membership_by_id(db, customer_membership_id, **update_data)
        return {"message": "Membresía de cliente actualizada exitosamente."}
    except HTTPException:
        raise
    except ValueError as ve:
        print(f"ValueError in update_customer_membership_by_id_controller: {ve}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error in update_customer_membership_by_id_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
