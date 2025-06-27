from fastapi import HTTPException
from database.crud_tables.memberships import create_membership, MySQLConnection
import traceback

def create_membership_controller(data: dict):
    db = MySQLConnection()
    try:
        required_fields = ["name"]
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
        
        name = data.get("name")
        description = data.get("description")
        discount_percentage = data.get("discount_percentage", 0)
        monthly_price = data.get("monthly_price", 0)
        benefits = data.get("benefits")
        
        create_membership(db, name, description, discount_percentage, monthly_price, benefits)
        return {"message": "Membresía creada exitosamente."}
    except HTTPException:
        raise
    except ValueError as ve:
        print(f"ValueError in create_membership_controller: {ve}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error in create_membership_controller: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
