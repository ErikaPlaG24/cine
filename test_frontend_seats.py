#!/usr/bin/env python3
"""
Script para verificar que los asientos reservados aparezcan correctamente en el frontend
"""

import requests
import time

def verificar_asientos_reservados():
    """Verificar que el backend devuelve asientos reservados correctamente"""
    
    base_url = "http://localhost:8001"
    
    print("🎬 === VERIFICACIÓN DE ASIENTOS RESERVADOS ===")
    print()
    
    # Verificar varios showtimes
    showtimes_to_test = [8, 11, 4, 5, 9, 10]
    
    for showtime_id in showtimes_to_test:
        try:
            url = f"{base_url}/reserved_seats/showtime/{showtime_id}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                reserved_seats = data.get('reserved_seats', [])
                
                print(f"🎟️ Showtime {showtime_id}:")
                print(f"   📍 Asientos reservados: {reserved_seats}")
                print(f"   📊 Total: {len(reserved_seats)} asientos")
                
                # Verificar que los asientos están en el rango correcto
                valid_seats = []
                invalid_seats = []
                
                for seat in reserved_seats:
                    if len(seat) >= 2:
                        row = seat[0]
                        try:
                            number = int(seat[1:])
                            if row in ['A', 'B', 'C', 'D', 'E', 'F'] and 1 <= number <= 10:
                                valid_seats.append(seat)
                            else:
                                invalid_seats.append(seat)
                        except ValueError:
                            invalid_seats.append(seat)
                    else:
                        invalid_seats.append(seat)
                
                if valid_seats:
                    print(f"   ✅ Asientos válidos (deberían aparecer en frontend): {valid_seats}")
                if invalid_seats:
                    print(f"   ❌ Asientos fuera de rango (NO aparecerán): {invalid_seats}")
                    
            else:
                print(f"❌ Error al obtener showtime {showtime_id}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error conectando a showtime {showtime_id}: {e}")
        
        print()
    
    print("🎯 === INSTRUCCIONES PARA VERIFICAR EN EL FRONTEND ===")
    print("1. Abre http://localhost:8001/frontend/")
    print("2. Haz login como admin (admin@test.com / admin123)")
    print("3. Ve a la sección de reservas")
    print("4. Selecciona una película")
    print("5. Selecciona un horario que tenga asientos reservados")
    print("6. Verifica que los asientos aparezcan en ROJO")
    print()
    print("🔍 Asientos que deberían aparecer en ROJO:")
    print("   - Showtime 8: A4, B4, A7, D2, E4, E9, D4, A10, A8")
    print("   - Showtime 11: B2, F10, E8, D9, A6")

if __name__ == "__main__":
    verificar_asientos_reservados()
