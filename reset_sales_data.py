#!/usr/bin/env python3
"""
Script para limpiar y recrear datos de prueba con precios correctos
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

def clean_and_recreate_sales():
    """Limpiar ventas existentes y crear nuevas con precios correctos"""
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        
        if connection.is_connected():
            print("✅ Conectado a la base de datos MySQL")
            
            cursor = connection.cursor()
            
            # Limpiar datos existentes
            print("🧹 Limpiando ventas existentes...")
            cursor.execute("DELETE FROM reserved_seats")
            cursor.execute("DELETE FROM sales")
            print("✅ Datos anteriores eliminados")
            
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
            
            # Crear ventas con precio correcto ($75 por boleto)
            sales_created = 0
            
            for i in range(15):  # Crear 15 ventas
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
                    seats_used = set()  # Para evitar duplicados en la misma venta
                    
                    for j in range(ticket_quantity):
                        # Generar asiento único para esta venta
                        attempts = 0
                        while attempts < 20:  # Max 20 intentos para encontrar asiento único
                            row = chr(65 + random.randint(0, 5))  # A-F
                            col = random.randint(1, 10)  # 1-10
                            seat_number = f"{row}{col}"
                            
                            # Verificar que no esté usado en esta venta
                            if seat_number not in seats_used:
                                seats_used.add(seat_number)
                                
                                try:
                                    insert_seat = """
                                    INSERT INTO reserved_seats (sale_id, seat_number)
                                    VALUES (%s, %s)
                                    """
                                    
                                    cursor.execute(insert_seat, (sale_id, seat_number))
                                    break
                                    
                                except Error as seat_error:
                                    if "Duplicate entry" not in str(seat_error):
                                        print(f"⚠️ Error creando asiento: {seat_error}")
                            
                            attempts += 1
                    
                    sales_created += 1
                    print(f"✅ Venta {sales_created}: {ticket_quantity} boletos por ${total} (${price_per_ticket} c/u)")
                    
                except Error as sale_error:
                    print(f"❌ Error creando venta: {sale_error}")
            
            print(f"\n🎯 Se crearon {sales_created} ventas exitosamente!")
            print(f"💰 Todas las ventas usan el precio de $75 por boleto")
            
            # Mostrar resumen
            cursor.execute("SELECT COUNT(*), SUM(total), SUM(ticket_quantity) FROM sales")
            summary = cursor.fetchone()
            print(f"\n📊 Resumen:")
            print(f"   Total ventas: {summary[0]}")
            print(f"   Total ingresos: ${summary[1]}")
            print(f"   Total boletos: {summary[2]}")
            print(f"   Promedio por venta: ${summary[1]/summary[0]:.2f}")
            
    except Error as e:
        print(f"❌ Error: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("🔒 Conexión cerrada")

if __name__ == "__main__":
    print("🎬 === RECREACIÓN DE DATOS CON PRECIOS CORRECTOS ===")
    print()
    clean_and_recreate_sales()
