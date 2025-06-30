import os
import sys
from datetime import datetime
from typing import Dict, Any

# Agregar la carpeta api al path
sys.path.append(os.path.dirname(__file__))

from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "file://", "http://localhost:3000", "http://127.0.0.1:3000", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'database': 'cine',
    'user': 'root',
    'password': 'root',  # Contraseña desde docker-compose.yml
    'port': 4003,        # Puerto desde docker-compose.yml
    'charset': 'utf8mb4',
    'autocommit': True
}

def get_db_connection():
    """Crear conexión a la base de datos MySQL"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print(f"✅ Conexión exitosa a MySQL: {DB_CONFIG['database']}")
            return connection
    except Error as e:
        print(f"❌ Error conectando a MySQL: {e}")
        print(f"   Configuración usada: host={DB_CONFIG['host']}, database={DB_CONFIG['database']}, user={DB_CONFIG['user']}")
        print("   Verifica que MySQL esté corriendo y que la base de datos 'cine' exista")
        return None

# Modelos Pydantic
class LoginRequest(BaseModel):
    username: str
    password: str

class SaleRequest(BaseModel):
    customer_user_id: int
    showtime_id: int
    ticket_quantity: int
    total: float
    payment_method: str = "cash"
    seats: list = []  # Lista de asientos comprados

class ReservationRequest(BaseModel):
    showtime_id: int
    seat_row: str
    seat_number: int
    reservation_date: str

@app.get("/")
def read_root():
    connection = get_db_connection()
    is_connected = connection is not None
    if connection:
        connection.close()
    return {"message": "Cine API - Database Version", "database_connected": is_connected}

@app.post("/auth/login")
async def login(request: LoginRequest):
    print(f"🔍 Login request received: username={request.username}")
    
    connection = get_db_connection()
    if not connection:
        print("❌ No database connection available")
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = connection.cursor(dictionary=True)
        print(f"✅ Database cursor created")
        
        # Buscar usuario por username
        query = "SELECT user_id, username, password, first_name, last_name FROM users WHERE username = %s"
        print(f"🔍 Executing query: {query} with username: {request.username}")
        cursor.execute(query, (request.username,))
        user = cursor.fetchone()
        print(f"📊 Query result: {user}")
        
        if not user:
            # Si no existe el usuario, crear uno de prueba
            print(f"👤 Usuario {request.username} no encontrado, creando usuario de prueba")
            response = {
                "access_token": f"token_{request.username}_{datetime.now().timestamp()}",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "username": request.username,
                    "name": f"{request.username} User"
                }
            }
            print(f"✅ Response created: {response}")
            return response
        
        # Por simplicidad, aceptar cualquier contraseña en desarrollo
        response = {
            "access_token": f"token_{user['user_id']}_{datetime.now().timestamp()}",
            "token_type": "bearer",
            "user": {
                "id": user['user_id'],
                "username": user['username'],
                "name": f"{user['first_name']} {user['last_name']}"
            }
        }
        print(f"✅ User found, response created: {response}")
        return response
            
    except Error as e:
        print(f"❌ MySQL Error en login: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        print(f"❌ General Error en login: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
    finally:
        try:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
                print("🔒 Database connection closed")
        except Exception as e:
            print(f"⚠️ Error closing connection: {e}")

@app.get("/movies/all")
async def get_all_movies():
    # Devolver siempre estas 3 películas específicas
    return [
        {
            "id": 1, 
            "title": "Mad Max: Furia en la carretera", 
            "description": "Una película de acción post-apocalíptica donde Max ayuda a un grupo de mujeres rebeldes a escapar de un tirano en el desierto.",
            "genre": "Acción", 
            "duration": 120,
            "rating": "R",
            "poster_url": "/poster1.jpg"
        },
        {
            "id": 2, 
            "title": "Un jefe en pañales", 
            "description": "Un bebé con traje de ejecutivo llega a casa de una familia y resulta que puede hablar y tiene una misión secreta.",
            "genre": "Comedia", 
            "duration": 97,
            "rating": "PG",
            "poster_url": "/poster2.jpg"
        },
        {
            "id": 3, 
            "title": "El conjuro 3", 
            "description": "Los investigadores paranormales Ed y Lorraine Warren enfrentan uno de los casos más sensacionales de su carrera.",
            "genre": "Terror", 
            "duration": 112,
            "rating": "R",
            "poster_url": "/poster3.jpg"
        }
    ]

@app.get("/theaters/all")  
async def get_all_theaters():
    connection = get_db_connection()
    if not connection:
        return [
            {"id": 1, "name": "Sala 1", "capacity": 20},
            {"id": 2, "name": "Sala 2", "capacity": 20},
            {"id": 3, "name": "Sala 3", "capacity": 20}
        ]
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT theater_id as id, name, capacity, has_3d, has_dolby, is_imax FROM theaters"
        cursor.execute(query)
        theaters = cursor.fetchall()
        
        print(f"📊 Theaters encontrados: {len(theaters)}")
        return theaters
        
    except Error as e:
        print(f"Error getting theaters: {e}")
        return [{"id": 1, "name": "Sala 1", "capacity": 20}]
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.get("/showtimes/all")
async def get_all_showtimes():
    # Devolver horarios fijos para las 3 películas usando IDs reales de la DB
    from datetime import datetime, timedelta
    
    # Obtener fecha de hoy y mañana en formato string
    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    return [
        # Horarios para Mad Max (película ID 1) - Usando IDs reales de la DB
        {"id": 2, "movie_id": 1, "theater_id": 1, "start_time": "14:00", "date": today, "movie_title": "Mad Max: Furia en la carretera", "theater_name": "Sala 1"},
        {"id": 3, "movie_id": 1, "theater_id": 1, "start_time": "17:00", "date": today, "movie_title": "Mad Max: Furia en la carretera", "theater_name": "Sala 1"},
        {"id": 4, "movie_id": 1, "theater_id": 2, "start_time": "20:00", "date": today, "movie_title": "Mad Max: Furia en la carretera", "theater_name": "Sala 2"},
        
        # Horarios para Un jefe en pañales (película ID 2)
        {"id": 5, "movie_id": 2, "theater_id": 2, "start_time": "14:30", "date": today, "movie_title": "Un jefe en pañales", "theater_name": "Sala 2"},
        {"id": 6, "movie_id": 2, "theater_id": 1, "start_time": "16:30", "date": today, "movie_title": "Un jefe en pañales", "theater_name": "Sala 1"},
        {"id": 7, "movie_id": 2, "theater_id": 2, "start_time": "19:00", "date": today, "movie_title": "Un jefe en pañales", "theater_name": "Sala 2"},
        
        # Para mañana, reutilizar algunos IDs para simplificar
        {"id": 2, "movie_id": 3, "theater_id": 1, "start_time": "15:30", "date": tomorrow, "movie_title": "El conjuro 3", "theater_name": "Sala 1"},
        {"id": 3, "movie_id": 3, "theater_id": 2, "start_time": "18:30", "date": tomorrow, "movie_title": "El conjuro 3", "theater_name": "Sala 2"}
    ]

@app.get("/reserved_seats/all")
async def get_reserved_seats():
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        # La tabla reserved_seats tiene sale_id y seat_number, no showtime_id
        query = "SELECT sale_id, seat_number FROM reserved_seats"
        cursor.execute(query)
        seats = cursor.fetchall()
        return seats
        
    except Error as e:
        print(f"Error getting reserved seats: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.post("/sales")
async def create_sale(request: SaleRequest):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = connection.cursor()
        
        # Crear la venta
        sale_query = """
        INSERT INTO sales (user_id, showtime_id, total_amount, sale_date, status)
        VALUES (%s, %s, %s, %s, 'completed')
        """
        sale_date = datetime.now()
        cursor.execute(sale_query, (request.user_id, request.showtime_id, request.total_amount, sale_date))
        
        # Obtener el ID de la venta recién creada
        sale_id = cursor.lastrowid
        connection.commit()
        
        print(f"✅ Venta creada exitosamente:")
        print(f"   - ID de venta: {sale_id}")
        print(f"   - Usuario: {request.user_id}")
        print(f"   - Horario: {request.showtime_id}")
        print(f"   - Total: ${request.total_amount}")
        print(f"   - Fecha: {sale_date}")
        
        return {
            "sale_id": sale_id,
            "message": "Venta registrada exitosamente en la base de datos",
            "total_amount": request.total_amount,
            "sale_date": sale_date.isoformat()
        }
        
    except Error as e:
        print(f"❌ Error creating sale: {e}")
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear la venta: {str(e)}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.post("/reserved_seats")
async def create_reservation(request: ReservationRequest):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = connection.cursor()
        
        # Verificar si el asiento ya está reservado
        check_query = """
        SELECT id FROM reserved_seats 
        WHERE showtime_id = %s AND seat_row = %s AND seat_number = %s
        """
        cursor.execute(check_query, (request.showtime_id, request.seat_row, request.seat_number))
        existing = cursor.fetchone()
        
        if existing:
            raise HTTPException(status_code=400, detail="Asiento ya reservado")
        
        # Insertar la reserva
        query = """
        INSERT INTO reserved_seats (showtime_id, seat_row, seat_number, reservation_date, status)
        VALUES (%s, %s, %s, %s, 'reserved')
        """
        cursor.execute(query, (request.showtime_id, request.seat_row, request.seat_number, datetime.now()))
        connection.commit()
        
        reservation_id = cursor.lastrowid
        
        print(f"✅ Asiento reservado:")
        print(f"   - Reserva ID: {reservation_id}")
        print(f"   - Horario: {request.showtime_id}")
        print(f"   - Asiento: Fila {request.seat_row}, Número {request.seat_number}")
        
        return {
            "reservation_id": reservation_id,
            "message": "Asiento reservado exitosamente",
            "seat": f"Fila {request.seat_row}, Asiento {request.seat_number}"
        }
        
    except Error as e:
        print(f"❌ Error creating reservation: {e}")
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error al reservar asiento: {str(e)}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Endpoint para crear ventas
@app.post("/sales/create")
async def create_sale(request: SaleRequest):
    print(f"🛒 Creating sale: customer_id={request.customer_user_id}, showtime_id={request.showtime_id}, total=${request.total}")
    
    connection = get_db_connection()
    if not connection:
        # Si no hay conexión a DB, simular venta exitosa
        return {
            "success": True,
            "sale_id": 999,
            "message": "Venta creada exitosamente (modo prueba)",
            "total_paid": request.total
        }
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Para simplificar, vamos a crear una venta básica
        # Insertar en la tabla sales con las columnas que realmente existen
        sale_query = """
        INSERT INTO sales (showtime_id, customer_user_id, ticket_quantity, subtotal, total, payment_method, sale_date)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """
        # Calcular subtotal (mismo que el total por simplicidad)
        subtotal = request.total
        
        sale_values = (
            request.showtime_id,
            request.customer_user_id,
            request.ticket_quantity,
            subtotal,
            request.total,
            request.payment_method or 'cash'
        )
        
        print(f"🔍 Executing sale query: {sale_query}")
        print(f"📊 Sale values: {sale_values}")
        
        cursor.execute(sale_query, sale_values)
        sale_id = cursor.lastrowid
        
        print(f"✅ Sale created with ID: {sale_id}")
        
        # Insertar los asientos reservados
        reserved_seats_ids = []
        if request.seats:
            for seat in request.seats:
                # La tabla actual solo tiene sale_id y seat_number
                reservation_query = """
                INSERT INTO reserved_seats (sale_id, seat_number)
                VALUES (%s, %s)
                """
                cursor.execute(reservation_query, (sale_id, seat))
                reservation_id = cursor.lastrowid
                reserved_seats_ids.append(reservation_id)
                print(f"🪑 Reserved seat: {seat} (Reservation ID: {reservation_id}, Sale ID: {sale_id})")
        
        
        connection.commit()
        
        response = {
            "success": True,
            "sale_id": sale_id,
            "message": "Venta creada exitosamente",
            "reserved_seats": reserved_seats_ids,
            "total_paid": request.total
        }
        
        print(f"🎫 Sale completed: {response}")
        return response
        
    except Error as e:
        print(f"❌ MySQL Error creating sale: {e}")
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear la venta: {str(e)}")
    except Exception as e:
        print(f"❌ General Error creating sale: {e}")
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("🔒 Database connection closed")

# Endpoint para verificar ventas en la base de datos
@app.get("/sales/all")
async def get_all_sales():
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT s.sale_id, s.customer_user_id, s.showtime_id, s.ticket_quantity,
               s.subtotal, s.total, s.sale_date, s.payment_method,
               st.start_time, st.date as show_date,
               m.title as movie_title, m.genre,
               t.name as theater_name
        FROM sales s
        LEFT JOIN showtimes st ON s.showtime_id = st.id
        LEFT JOIN movies m ON st.movie_id = m.id
        LEFT JOIN theaters t ON st.theater_id = t.id
        ORDER BY s.sale_date DESC
        """
        cursor.execute(query)
        sales = cursor.fetchall()
        
        print(f"📊 Ventas encontradas en la base de datos: {len(sales)}")
        for sale in sales:
            print(f"   - Venta ID: {sale['sale_id']}, Total: ${sale['total']}, Fecha: {sale['sale_date']}")
        
        return sales
        
    except Error as e:
        print(f"Error getting sales: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.get("/reserved_seats/showtime/{showtime_id}")
async def get_reserved_seats_by_showtime(showtime_id: int):
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        # Obtener asientos reservados para un showtime específico
        # JOIN correcto: reserved_seats.sale_id = sales.sale_id
        query = """
        SELECT DISTINCT 
            rs.reservation_id as id,
            s.showtime_id,
            rs.seat_number,
            rs.sale_id,
            rs.created_at as reservation_date
        FROM reserved_seats rs
        INNER JOIN sales s ON rs.sale_id = s.sale_id
        WHERE s.showtime_id = %s
        """
        cursor.execute(query, (showtime_id,))
        seats = cursor.fetchall()
        
        # Agregar información de fila y número parseando seat_number
        for seat in seats:
            seat_str = seat['seat_number']
            if len(seat_str) >= 2:
                seat['seat_row'] = seat_str[0]  # Primera letra (A, B, C, D)
                seat['seat_number_parsed'] = seat_str[1:]  # Números después de la letra
            else:
                seat['seat_row'] = 'A'
                seat['seat_number_parsed'] = '1'
        
        print(f"📋 Asientos reservados para showtime {showtime_id}: {len(seats)} asientos encontrados")
        for seat in seats:
            print(f"   🪑 ID: {seat['id']}, Asiento: {seat['seat_number']}, Sale ID: {seat['sale_id']}")
        
        return seats
        
    except Error as e:
        print(f"Error getting reserved seats by showtime: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando servidor con conexión a base de datos MySQL...")
    print(f"📦 Base de datos: {DB_CONFIG['database']}")
    print(f"🔗 Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
