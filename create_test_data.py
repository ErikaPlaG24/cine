#!/usr/bin/env python3
"""
Script para crear datos de prueba para los reportes
"""

import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import random

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'database': 'cine',
    'user': 'root',
    'password': 'root',
    'port': 4003,
    'charset': 'utf8mb4',
    'autocommit': True
}

def create_test_sales():
    """Crear ventas de prueba"""
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        
        if connection.is_connected():
            print("✅ Conectado a la base de datos MySQL")
            
            cursor = connection.cursor()
            
            # Obtener IDs de usuarios existentes
            cursor.execute("SELECT user_id FROM users WHERE role = 'customer'")
            customers = [row[0] for row in cursor.fetchall()]
            
            if not customers:
                print("❌ No hay clientes en la base de datos")
                return
                
            # Obtener horarios existentes
            cursor.execute("SELECT showtime_id, movie_id, theater_id FROM showtimes")
            showtimes = cursor.fetchall()
            
            if not showtimes:
                print("❌ No hay horarios en la base de datos")
                return
            
            print(f"🎬 Encontrados {len(customers)} clientes y {len(showtimes)} horarios")
            
            # Crear ventas de prueba
            sales_created = 0
            
            for i in range(10):  # Crear 10 ventas
                customer_id = random.choice(customers)
                showtime_id, movie_id, theater_id = random.choice(showtimes)
                
                # Generar datos de venta
                ticket_quantity = random.randint(1, 4)
                price_per_ticket = 75  # Precio fijo de $75 por boleto
                subtotal = ticket_quantity * price_per_ticket
                discount = 0  # Sin descuento por ahora
                total = subtotal - discount
                
                # Fecha de venta (últimos 30 días)
                sale_date = datetime.now() - timedelta(days=random.randint(0, 30))
                
                try:
                    # Insertar venta
                    insert_sale = """
                    INSERT INTO sales (customer_user_id, showtime_id, ticket_quantity, subtotal, discount_amount, total, payment_method, sale_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    cursor.execute(insert_sale, (
                        customer_id,
                        showtime_id,
                        ticket_quantity,
                        subtotal,
                        discount,
                        total,
                        random.choice(['credit_card', 'cash', 'debit_card']),
                        sale_date
                    ))
                    
                    sale_id = cursor.lastrowid
                    
                    # Crear asientos reservados para esta venta
                    for j in range(ticket_quantity):
                        seat_number = f"{chr(65 + random.randint(0, 5))}{random.randint(1, 10)}"  # A1-F10
                        
                        try:
                            insert_seat = """
                            INSERT INTO reserved_seats (sale_id, seat_number)
                            VALUES (%s, %s)
                            """
                            
                            cursor.execute(insert_seat, (sale_id, seat_number))
                            
                        except Error as seat_error:
                            # Ignorar duplicados de asientos
                            if "Duplicate entry" not in str(seat_error):
                                print(f"⚠️ Error creando asiento: {seat_error}")
                    
                    sales_created += 1
                    print(f"✅ Venta {sales_created}: {ticket_quantity} boletos por ${total}")
                    
                except Error as sale_error:
                    print(f"❌ Error creando venta: {sale_error}")
            
            print(f"\n🎯 Se crearon {sales_created} ventas de prueba exitosamente!")
            
    except Error as e:
        print(f"❌ Error: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("🔒 Conexión cerrada")

def check_existing_data():
    """Verificar datos existentes"""
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Contar ventas
            cursor.execute("SELECT COUNT(*) FROM sales")
            sales_count = cursor.fetchone()[0]
            
            # Contar asientos reservados
            cursor.execute("SELECT COUNT(*) FROM reserved_seats")
            seats_count = cursor.fetchone()[0]
            
            # Contar películas
            cursor.execute("SELECT COUNT(*) FROM movies")
            movies_count = cursor.fetchone()[0]
            
            # Contar horarios
            cursor.execute("SELECT COUNT(*) FROM showtimes")
            showtimes_count = cursor.fetchone()[0]
            
            print(f"📊 Estado actual de la base de datos:")
            print(f"   🎬 Películas: {movies_count}")
            print(f"   🕐 Horarios: {showtimes_count}")
            print(f"   💰 Ventas: {sales_count}")
            print(f"   🪑 Asientos reservados: {seats_count}")
            
    except Error as e:
        print(f"❌ Error: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    print("🎬 === CREACIÓN DE DATOS DE PRUEBA PARA REPORTES ===")
    print()
    
    print("📊 Verificando datos existentes...")
    check_existing_data()
    print()
    
    create_test_sales()
    print()
    
    print("📊 Estado final:")
    check_existing_data()
