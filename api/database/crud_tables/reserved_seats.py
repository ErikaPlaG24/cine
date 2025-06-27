from database.mysql_connection import MySQLConnection

def get_all_reserved_seats(db: MySQLConnection):
    db.execute("SELECT * FROM reserved_seats")
    return db.fetchall()

def get_reserved_seat_by_id(db: MySQLConnection, reservation_id):
    db.execute("SELECT * FROM reserved_seats WHERE reservation_id = %s", (reservation_id,))
    return db.fetchone()

def create_reserved_seat(db: MySQLConnection, sale_id, seat_number):
    db.execute(
        "INSERT INTO reserved_seats (sale_id, seat_number) VALUES (%s, %s)",
        (sale_id, seat_number)
    )
    db.commit()

def update_reserved_seat_by_id(db: MySQLConnection, reservation_id, seat_number=None):
    if seat_number is None:
        raise ValueError("No se proporcionaron campos válidos para actualizar.")
    db.execute(
        "UPDATE reserved_seats SET seat_number = %s WHERE reservation_id = %s",
        (seat_number, reservation_id)
    )
    db.commit()

def delete_reserved_seat_by_id(db: MySQLConnection, reservation_id):
    db.execute("DELETE FROM reserved_seats WHERE reservation_id = %s", (reservation_id,))
    db.commit()
