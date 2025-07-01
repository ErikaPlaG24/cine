import os
import sys

# Agregar la carpeta api al path
sys.path.append(os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database.mysql_connection import MySQLConnection
from routes.auth import router as auth_routes
from routes.users import router as user_routes
from routes.movies import router as movie_routes
from routes.theaters import router as theater_routes
from routes.memberships import router as membership_routes
from routes.movie_genres import router as movie_genre_routes
from routes.showtimes import router as showtime_routes
from routes.sales import router as sale_routes
from routes.reserved_seats import router as reserved_seat_routes
from routes.customer_memberships import router as customer_membership_routes
from datetime import datetime
from fastapi import HTTPException

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En desarrollo permite todos los orígenes
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize the database connection
db = MySQLConnection(
    host        = os.getenv("MYSQL_HOST", "localhost"),
    port        = int(os.getenv("MYSQL_PORT", "3306")),
    user        = os.getenv("MYSQL_USER", "root"),
    password    = os.getenv("MYSQL_PASSWORD", "root"),
    database    = os.getenv("MYSQL_DATABASE", "cine")
)

@app.get("/")
def read_root():
    return {"message": "Cine API"}

app.include_router(auth_routes, prefix="/auth")
app.include_router(user_routes, prefix="/users")
app.include_router(movie_routes, prefix="/movies")
app.include_router(theater_routes, prefix="/theaters")
app.include_router(membership_routes, prefix="/memberships")
app.include_router(movie_genre_routes, prefix="/movie_genres")
app.include_router(showtime_routes, prefix="/showtimes")
app.include_router(sale_routes, prefix="/sales")
app.include_router(reserved_seat_routes, prefix="/reserved_seats")
app.include_router(customer_membership_routes, prefix="/customer_memberships")

# Endpoints de reportes para administradores
@app.get("/reports/sales-summary")
async def get_sales_summary():
    """Obtener resumen completo de ventas para administradores"""
    try:
        # a) Total de ventas realizadas
        db.execute("SELECT COUNT(*) as total_sales, COALESCE(SUM(total), 0) as total_amount FROM sales")
        sales_total = db.fetchone()
        
        # b) Número de clientes atendidos
        db.execute("SELECT COUNT(DISTINCT customer_user_id) as unique_customers FROM sales")
        customers_count = db.fetchone()
        
        # c) Total de ventas a clientes con membresía
        db.execute("""
            SELECT COUNT(*) as sales_with_membership, COALESCE(SUM(s.total), 0) as amount_with_membership
            FROM sales s
            INNER JOIN customer_memberships cm ON s.customer_user_id = cm.user_id
            WHERE cm.is_active = 1
        """)
        membership_sales = db.fetchone()
        
        # d) Total de ventas a clientes sin membresía
        db.execute("""
            SELECT COUNT(*) as sales_without_membership, COALESCE(SUM(s.total), 0) as amount_without_membership
            FROM sales s
            LEFT JOIN customer_memberships cm ON s.customer_user_id = cm.user_id
            WHERE cm.user_id IS NULL OR cm.is_active != 1
        """)
        non_membership_sales = db.fetchone()
        
        # e) Total de boletos vendidos por película con ingresos
        db.execute("""
            SELECT m.title, 
                   COALESCE(SUM(s.ticket_quantity), 0) as tickets_sold,
                   COALESCE(SUM(s.total), 0) as total_revenue
            FROM movies m
            LEFT JOIN showtimes st ON m.id = st.movie_id
            LEFT JOIN sales s ON st.showtime_id = s.showtime_id
            GROUP BY m.id, m.title
            ORDER BY tickets_sold DESC
        """)
        tickets_by_movie = db.fetchall()
        
        # f) Total de boletos vendidos por sala con ingresos
        db.execute("""
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
        tickets_by_theater = db.fetchall()
        
        # g) Película más vendida con ingresos
        db.execute("""
            SELECT m.title, COALESCE(SUM(s.ticket_quantity), 0) as tickets_sold,
                   COALESCE(SUM(s.total), 0) as total_revenue
            FROM movies m
            LEFT JOIN showtimes st ON m.id = st.movie_id
            LEFT JOIN sales s ON st.showtime_id = s.showtime_id
            GROUP BY m.id, m.title
            ORDER BY tickets_sold DESC
            LIMIT 1
        """)
        most_sold_movie = db.fetchone()
        
        # h) Película menos vendida con ingresos
        db.execute("""
            SELECT m.title, COALESCE(SUM(s.ticket_quantity), 0) as tickets_sold,
                   COALESCE(SUM(s.total), 0) as total_revenue
            FROM movies m
            LEFT JOIN showtimes st ON m.id = st.movie_id
            LEFT JOIN sales s ON st.showtime_id = s.showtime_id
            GROUP BY m.id, m.title
            ORDER BY tickets_sold ASC
            LIMIT 1
        """)
        least_sold_movie = db.fetchone()
        
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
        
    except Exception as e:
        print(f"❌ Error generando reporte: {e}")
        raise HTTPException(status_code=500, detail=f"Error generando reporte: {str(e)}")

@app.get("/reports/detailed-sales")
async def get_detailed_sales():
    """Obtener ventas detalladas para administradores"""
    try:
        query = """
        SELECT s.sale_id, s.customer_user_id, s.showtime_id, s.ticket_quantity, s.total, s.sale_date,
               u.email as customer_email,
               m.title as movie_title,
               st.theater_id, st.start_time, st.date as showtime_date,
               COALESCE(t.name, CONCAT('Sala ', st.theater_id)) as theater_name
        FROM sales s
        LEFT JOIN users u ON s.customer_user_id = u.user_id
        LEFT JOIN showtimes st ON s.showtime_id = st.showtime_id
        LEFT JOIN movies m ON st.movie_id = m.id
        LEFT JOIN theaters t ON st.theater_id = t.theater_id
        ORDER BY s.sale_date DESC
        """
        
        db.execute(query)
        sales = db.fetchall()
        
        return {
            "sales": sales,
            "total_sales": len(sales) if sales else 0,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error obteniendo ventas detalladas: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo ventas detalladas: {str(e)}")