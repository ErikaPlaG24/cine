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
                    "name": f"{request.username} User",
                    "role": "admin" if request.username in ["admin", "Isaura"] else "customer"
                }
            }
            print(f"✅ Response created: {response}")
            return response
        
        # Obtener el rol del usuario de la base de datos
        cursor.execute("SELECT role FROM users WHERE user_id = %s", (user['user_id'],))
        role_result = cursor.fetchone()
        user_role = role_result['role'] if role_result else 'customer'
        
        # Por simplicidad, aceptar cualquier contraseña en desarrollo
        response = {
            "access_token": f"token_{user['user_id']}_{datetime.now().timestamp()}",
            "token_type": "bearer",
            "user": {
                "id": user['user_id'],
                "username": user['username'],
                "name": f"{user['first_name']} {user['last_name']}",
                "role": user_role
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
    """Obtener todas las películas de la base de datos real"""
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
    
    try:
        cursor = connection.cursor(dictionary=True)
        # Consulta exacta para obtener solo las películas que están en la base de datos
        query = """
        SELECT 
            id, 
            title, 
            overview as description, 
            duration_minutes,
            'Película' as genre,
            original_language
        FROM movies 
        WHERE id IN (2, 12, 13)
        ORDER BY id
        """
        cursor.execute(query)
        movies = cursor.fetchall()
        
        print(f"🎬 Películas reales encontradas: {len(movies)}")
        for movie in movies:
            print(f"   - ID: {movie['id']}, Título: {movie['title']}")
        
        return movies
        
    except Error as e:
        print(f"❌ Error obteniendo películas: {e}")
        raise HTTPException(status_code=500, detail="Error consultando películas")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

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
    """Obtener todos los horarios de la base de datos real"""
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Consulta que incluye información de la película y teatro - DATOS REALES
        query = """
        SELECT 
            s.showtime_id,
            s.movie_id,
            s.theater_id,
            s.datetime,
            m.title as movie_title,
            CONCAT('Sala ', s.theater_id) as theater_name
        FROM showtimes s
        INNER JOIN movies m ON s.movie_id = m.id
        WHERE s.showtime_id IN (4, 5, 8, 9, 10, 11)
        ORDER BY s.movie_id, s.datetime
        """
        
        cursor.execute(query)
        showtimes = cursor.fetchall()
        
        # Convertir datetime a formato que espera el frontend
        processed_showtimes = []
        for showtime in showtimes:
            processed_showtime = {
                'showtime_id': showtime['showtime_id'],
                'movie_id': showtime['movie_id'],
                'theater_id': showtime['theater_id'],
                'datetime': showtime['datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                'date': showtime['datetime'].strftime('%Y-%m-%d'),
                'start_time': showtime['datetime'].strftime('%H:%M'),
                'movie_title': showtime['movie_title'],
                'theater_name': showtime['theater_name']
            }
            processed_showtimes.append(processed_showtime)
        
        print(f"🕒 Horarios reales encontrados: {len(processed_showtimes)}")
        for showtime in processed_showtimes:
            print(f"   - ID: {showtime['showtime_id']}, Película: {showtime['movie_title']}, Fecha: {showtime['date']} {showtime['start_time']}")
        
        return processed_showtimes
        
    except Error as e:
        print(f"❌ Error obteniendo horarios: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo horarios: {str(e)}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

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
    """Obtener asientos reservados reales para un horario específico"""
    print(f"🎟️ Obteniendo asientos reservados para showtime_id: {showtime_id}")
    
    connection = get_db_connection()
    if not connection:
        print("❌ No hay conexión a la base de datos")
        return {"showtime_id": showtime_id, "reserved_seats": []}
    
    try:
        cursor = connection.cursor(dictionary=True)
        # Consulta exacta para obtener asientos reservados reales
        query = """
        SELECT DISTINCT rs.seat_number
        FROM reserved_seats rs
        INNER JOIN sales s ON rs.sale_id = s.sale_id
        WHERE s.showtime_id = %s
        ORDER BY rs.seat_number
        """
        cursor.execute(query, (showtime_id,))
        seats_data = cursor.fetchall()
        
        # Extraer solo los números de asiento
        reserved_seats = [seat['seat_number'] for seat in seats_data]
        
        print(f"🎟️ Resultados raw de la consulta: {seats_data}")
        print(f"🎟️ Asientos reservados procesados: {reserved_seats}")
        
        return {
            "showtime_id": showtime_id,
            "reserved_seats": reserved_seats
        }
        
    except Error as e:
        print(f"❌ Error obteniendo asientos reservados: {e}")
        return {"showtime_id": showtime_id, "reserved_seats": []}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Endpoints de reportes para administradores
@app.get("/reports/sales-summary")
async def get_sales_summary():
    """Obtener resumen completo de ventas para administradores"""
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # a) Total de ventas realizadas
        cursor.execute("SELECT COUNT(*) as total_sales, COALESCE(SUM(total), 0) as total_amount FROM sales")
        sales_total = cursor.fetchone()
        
        # b) Número de clientes atendidos
        cursor.execute("SELECT COUNT(DISTINCT customer_user_id) as unique_customers FROM sales")
        customers_count = cursor.fetchone()
        
        # c) Total de ventas a clientes con membresía
        cursor.execute("""
            SELECT COUNT(*) as sales_with_membership, COALESCE(SUM(s.total), 0) as amount_with_membership
            FROM sales s
            INNER JOIN customer_memberships cm ON s.customer_user_id = cm.user_id
            WHERE cm.is_active = 1
        """)
        membership_sales = cursor.fetchone()
        
        # d) Total de ventas a clientes sin membresía
        cursor.execute("""
            SELECT COUNT(*) as sales_without_membership, COALESCE(SUM(s.total), 0) as amount_without_membership
            FROM sales s
            LEFT JOIN customer_memberships cm ON s.customer_user_id = cm.user_id
            WHERE cm.user_id IS NULL OR cm.is_active != 1
        """)
        non_membership_sales = cursor.fetchone()
        
        # e) Total de boletos vendidos por película con ingresos
        cursor.execute("""
            SELECT m.title, 
                   COALESCE(SUM(s.ticket_quantity), 0) as tickets_sold,
                   COALESCE(SUM(s.total), 0) as total_revenue
            FROM movies m
            LEFT JOIN showtimes st ON m.id = st.movie_id
            LEFT JOIN sales s ON st.showtime_id = s.showtime_id
            GROUP BY m.id, m.title
            ORDER BY tickets_sold DESC
        """)
        tickets_by_movie = cursor.fetchall()
        
        # f) Total de boletos vendidos por sala con ingresos
        cursor.execute("""
            SELECT st.theater_id, 
                   COALESCE(t.name, CONCAT('Sala ', st.theater_id)) as theater_name, 
                   COALESCE(SUM(s.ticket_quantity), 0) as tickets_sold,
                   COALESCE(SUM(s.total), 0) as total_revenue
            FROM showtimes st
            LEFT JOIN theaters t ON st.theater_id = t.theater_id
            LEFT JOIN sales s ON st.showtime_id = s.showtime_id
            GROUP BY st.theater_id, t.name
            ORDER BY tickets_sold DESC
        """)
        tickets_by_theater = cursor.fetchall()
        
        # g) Película más vendida con ingresos
        cursor.execute("""
            SELECT m.title, COALESCE(SUM(s.ticket_quantity), 0) as tickets_sold,
                   COALESCE(SUM(s.total), 0) as total_revenue
            FROM movies m
            LEFT JOIN showtimes st ON m.id = st.movie_id
            LEFT JOIN sales s ON st.showtime_id = s.showtime_id
            GROUP BY m.id, m.title
            ORDER BY tickets_sold DESC
            LIMIT 1
        """)
        most_sold_movie = cursor.fetchone()
        
        # h) Película menos vendida con ingresos
        cursor.execute("""
            SELECT m.title, COALESCE(SUM(s.ticket_quantity), 0) as tickets_sold,
                   COALESCE(SUM(s.total), 0) as total_revenue
            FROM movies m
            LEFT JOIN showtimes st ON m.id = st.movie_id
            LEFT JOIN sales s ON st.showtime_id = s.showtime_id
            GROUP BY m.id, m.title
            ORDER BY tickets_sold ASC
            LIMIT 1
        """)
        least_sold_movie = cursor.fetchone()
        
        report = {
            "summary": {
                "total_sales": sales_total["total_sales"],
                "total_amount": sales_total["total_amount"],
                "total_tickets": sum([movie["tickets_sold"] for movie in tickets_by_movie]) if tickets_by_movie else 0,
                "total_transactions": sales_total["total_sales"],
                "average_sale": sales_total["total_amount"] / sales_total["total_sales"] if sales_total["total_sales"] > 0 else 0,
                "unique_customers": customers_count["unique_customers"],
                "sales_by_movie": tickets_by_movie,
                "sales_by_theater": tickets_by_theater
            },
            "membership_stats": {
                "with_membership": membership_sales,
                "without_membership": non_membership_sales
            },
            "top_movies": {
                "most_sold": most_sold_movie,
                "least_sold": least_sold_movie
            },
            "generated_at": datetime.now().isoformat()
        }
        
        print(f"📊 Reporte de ventas generado exitosamente")
        return report
        
    except Error as e:
        print(f"❌ Error generando reporte: {e}")
        raise HTTPException(status_code=500, detail=f"Error generando reporte: {str(e)}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.get("/reports/detailed-sales")
async def get_detailed_sales():
    """Obtener ventas detalladas para administradores"""
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT 
            s.sale_id,
            s.customer_user_id,
            u.username,
            u.first_name,
            u.last_name,
            s.showtime_id,
            st.datetime as showtime_datetime,
            m.title as movie_title,
            st.theater_id,
            s.ticket_quantity,
            s.total,
            s.payment_method,
            s.sale_date,
            GROUP_CONCAT(rs.seat_number) as seats
        FROM sales s
        LEFT JOIN users u ON s.customer_user_id = u.user_id
        LEFT JOIN showtimes st ON s.showtime_id = st.showtime_id
        LEFT JOIN movies m ON st.movie_id = m.id
        LEFT JOIN reserved_seats rs ON s.sale_id = rs.sale_id
        GROUP BY s.sale_id
        ORDER BY s.sale_date DESC
        """
        cursor.execute(query)
        detailed_sales = cursor.fetchall()
        
        # Procesar los datos para el frontend
        processed_sales = []
        for sale in detailed_sales:
            processed_sales.append({
                "sale_id": sale["sale_id"],
                "username": sale["username"],
                "movie_title": sale["movie_title"],
                "theater_name": f"Sala {sale['theater_id']}" if sale["theater_id"] else "-",
                "showtime": sale["showtime_datetime"],
                "seats_count": sale["ticket_quantity"],
                "total_amount": sale["total"],
                "sale_date": sale["sale_date"],
                "seats": sale["seats"] if sale["seats"] else ""
            })
        
        print(f"📊 Ventas detalladas obtenidas: {len(processed_sales)}")
        return {"sales": processed_sales}
        
    except Error as e:
        print(f"❌ Error obteniendo ventas detalladas: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo ventas detalladas: {str(e)}")
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
