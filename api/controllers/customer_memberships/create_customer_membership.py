from fastapi import HTTPException
from database.crud_tables.customer_memberships import create_customer_membership, MySQLConnection
import traceback

def create_customer_membership_controller(data: dict):
    db = MySQLConnection()
    try:
        required_fields = ["user_id", "membership_id", "start_date"]
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
        
        user_id = data.get("user_id")
        membership_id = data.get("membership_id")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        is_active = data.get("is_active", True)
        
        create_customer_membership(db, user_id, membership_id, start_date, end_date, is_active)
        return {"message": "Membresía de cliente creada exitosamente."}
    except HTTPException:
        raise
    except ValueError as ve:
        print(f"ValueError in create_customer_membership_controller: {ve}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error in create_customer_membership_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
