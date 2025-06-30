import os
import sys

# Agregar la carpeta api al path
sys.path.append(os.path.dirname(__file__))

from fastapi import FastAPI
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
    host        = os.getenv("MYSQL_HOST"),
    port        = 3306,
    user        = "root",
    password    = "root",
    database    = "cine"
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