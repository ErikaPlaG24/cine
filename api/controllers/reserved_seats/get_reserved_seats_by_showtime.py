from fastapi import HTTPException
from database.mysql_connection import MySQLConnection
import traceback

def get_reserved_seats_by_showtime_controller(showtime_id: int):
    """
    Obtiene todos los asientos reservados para un horario específico
    """
    db = MySQLConnection()
    try:
        print(f"🎟️ Obteniendo asientos reservados para showtime_id: {showtime_id}")
        
        # Query para obtener los asientos reservados de un horario específico
        # Unimos las tablas sales y reserved_seats usando sale_id
        query = """
        SELECT rs.seat_number 
        FROM reserved_seats rs
        INNER JOIN sales s ON rs.sale_id = s.sale_id
        WHERE s.showtime_id = %s
        """
        
        db.execute(query, (showtime_id,))
        results = db.fetchall()
        
        print(f"🎟️ Resultados raw de la consulta: {results}")
        
        # Extraer solo los números de asiento
        if results:
            if isinstance(results[0], dict):
                # Si son diccionarios
                reserved_seats = [row['seat_number'] for row in results]
            else:
                # Si son tuplas
                reserved_seats = [row[0] for row in results]
        else:
            reserved_seats = []
        
        print(f"🎟️ Asientos reservados procesados: {reserved_seats}")
        
        return {
            "showtime_id": showtime_id,
            "reserved_seats": reserved_seats
        }
        
    except Exception as e:
        print(f"❌ Error obteniendo asientos reservados para showtime {showtime_id}: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Error obteniendo asientos reservados: {str(e)}"
        )
    finally:
        if db:
            db.close()
