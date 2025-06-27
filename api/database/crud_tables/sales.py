from database.mysql_connection import MySQLConnection

def get_all_sales(db: MySQLConnection):
    db.execute("SELECT * FROM sales")
    return db.fetchall()

def get_sale_by_id(db: MySQLConnection, sale_id):
    db.execute("SELECT * FROM sales WHERE sale_id = %s", (sale_id,))
    return db.fetchone()

def create_sale(db: MySQLConnection, **kwargs):
    keys = []
    values = []
    for k, v in kwargs.items():
        keys.append(k)
        values.append(v)
    columns = ', '.join(keys)
    placeholders = ', '.join(['%s'] * len(keys))
    db.execute(f"INSERT INTO sales ({columns}) VALUES ({placeholders})", tuple(values))
    db.commit()

def update_sale_by_id(db: MySQLConnection, sale_id, **kwargs):
    updates = []
    values = []
    for k, v in kwargs.items():
        updates.append(f"{k} = %s")
        values.append(v)
    if not updates:
        raise ValueError("No se proporcionaron campos válidos para actualizar.")
    query = f"UPDATE sales SET {', '.join(updates)} WHERE sale_id = %s"
    values.append(sale_id)
    db.execute(query, tuple(values))
    db.commit()

def delete_sale_by_id(db: MySQLConnection, sale_id):
    db.execute("DELETE FROM sales WHERE sale_id = %s", (sale_id,))
    db.commit()
