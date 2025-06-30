from fastapi import HTTPException
from database.crud_tables.sales import create_sale, MySQLConnection
from database.crud_tables.reserved_seats import create_reserved_seat
import traceback

def create_sale_controller(data: dict):
    db = MySQLConnection()
    try:
        print(f"🛒 Datos recibidos para crear venta: {data}")
        
        required_fields = ["customer_user_id", "showtime_id", "ticket_quantity", "total"]
        missing_fields = [
            field for field in required_fields
            if field not in data or data.get(field) is None or data.get(field) == ""
        ]
        
        print(f"🔍 Campos requeridos: {required_fields}")
        print(f"🔍 Campos faltantes: {missing_fields}")
        
        if missing_fields:
            print(f"❌ Error de validación: campos faltantes {missing_fields}")
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Error de validación",
                    "missing_fields": missing_fields
                }
            )
        
        # Campos válidos para crear venta (según la estructura real de la tabla)
        valid_fields = ["customer_user_id", "showtime_id", "ticket_quantity", "subtotal", "total", "payment_method", "sale_date"]
        sale_data = {k: v for k, v in data.items() if k in valid_fields}
        
        # Crear la venta
        create_sale(db, **sale_data)
        
        # Obtener el ID de la venta recién creada
        db.execute("SELECT LAST_INSERT_ID()")
        result = db.fetchone()
        print(f"🔍 Resultado de LAST_INSERT_ID(): {result}")
        print(f"🔍 Tipo de resultado: {type(result)}")
        
        # Manejar tanto diccionarios como tuplas
        if isinstance(result, dict):
            sale_id = result.get('LAST_INSERT_ID()', result.get('last_insert_id()'))
        else:
            sale_id = result[0] if result else None
        
        print(f"🔍 Sale ID obtenido: {sale_id}")
        
        if not sale_id:
            raise ValueError("No se pudo obtener el ID de la venta creada")
        
        # Crear los asientos reservados si se proporcionaron
        if "seats" in data and data["seats"]:
            for seat in data["seats"]:
                create_reserved_seat(db, sale_id, seat)
        
        return {"message": "Venta creada exitosamente.", "sale_id": sale_id}
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
