#!/usr/bin/env python3
"""
Verificar ventas en la base de datos
"""

import mysql.connector
from mysql.connector import Error

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'database': 'cine',
    'user': 'root',
    'password': 'root',
    'port': 4003,
    'charset': 'utf8mb4'
}

def check_sales():
    """Verificar ventas en la base de datos"""
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        
        if connection.is_connected():
            print("✅ Conectado a la base de datos MySQL")
            
            cursor = connection.cursor()
            
            # Contar todas las ventas
            cursor.execute("SELECT COUNT(*) as total_sales, SUM(total) as total_amount FROM sales")
            totals = cursor.fetchone()
            print(f"\n📊 Totales generales:")
            print(f"   Total de ventas: {totals[0]}")
            print(f"   Monto total: ${totals[1]}")
            
            # Ver las últimas 10 ventas
            cursor.execute("""
                SELECT sale_id, customer_user_id, showtime_id, ticket_quantity, total, sale_date
                FROM sales 
                ORDER BY sale_date DESC 
                LIMIT 10
            """)
            sales = cursor.fetchall()
            
            print(f"\n📋 Últimas {len(sales)} ventas:")
            print("=" * 80)
            print(f"{'ID':<5} {'Cliente':<8} {'Horario':<8} {'Boletos':<8} {'Total':<10} {'Fecha'}")
            print("=" * 80)
            
            for sale in sales:
                sale_id, customer_id, showtime_id, tickets, total, date = sale
                print(f"{sale_id:<5} {customer_id:<8} {showtime_id:<8} {tickets:<8} ${total:<9} {date}")
            
            # Verificar ventas por película
            print(f"\n🎬 Ventas por película:")
            cursor.execute("""
                SELECT m.title, COUNT(s.sale_id) as num_sales, 
                       SUM(s.ticket_quantity) as total_tickets,
                       SUM(s.total) as total_revenue
                FROM movies m
                LEFT JOIN showtimes st ON m.id = st.movie_id
                LEFT JOIN sales s ON st.showtime_id = s.showtime_id
                GROUP BY m.id, m.title
                ORDER BY total_revenue DESC
            """)
            movie_sales = cursor.fetchall()
            
            print("=" * 70)
            print(f"{'Película':<30} {'Ventas':<8} {'Boletos':<8} {'Ingresos'}")
            print("=" * 70)
            
            for movie in movie_sales:
                title, num_sales, tickets, revenue = movie
                print(f"{title:<30} {num_sales or 0:<8} {tickets or 0:<8} ${revenue or 0}")
            
    except Error as e:
        print(f"❌ Error: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔒 Conexión cerrada")

if __name__ == "__main__":
    check_sales()
