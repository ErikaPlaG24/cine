from database.mysql_connection import MySQLConnection


def get_all_customer_memberships(db: MySQLConnection):
    """
    Obtiene todas las relaciones de clientes con membresía.
    """
    db.execute("SELECT * FROM customer_memberships")
    return db.fetchall()

def get_customer_membership_by_id(db: MySQLConnection, customer_membership_id):
    """
    Obtiene una relación de cliente con membresía por su ID.
    """
    db.execute("SELECT * FROM customer_memberships WHERE customer_membership_id = %s", (customer_membership_id,))
    return db.fetchone()

def create_customer_membership(
    db: MySQLConnection,
    user_id,
    membership_id,
    start_date,
    end_date=None,
    is_active=True
):
    """
    Crea una nueva relación cliente-membresía.
    """
    db.execute(
        """
        INSERT INTO customer_memberships (user_id, membership_id, start_date, end_date, is_active)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (user_id, membership_id, start_date, end_date, is_active)
    )
    db.commit()

def update_customer_membership_by_id(
    db: MySQLConnection,
    customer_membership_id,
    user_id=None,
    membership_id=None,
    start_date=None,
    end_date=None,
    is_active=None
):
    """
    Actualiza los datos de una relación cliente-membresía por su ID.
    """
    updates = []
    values = []

    if user_id is not None:
        updates.append("user_id = %s")
        values.append(user_id)
    if membership_id is not None:
        updates.append("membership_id = %s")
        values.append(membership_id)
    if start_date is not None:
        updates.append("start_date = %s")
        values.append(start_date)
    if end_date is not None:
        updates.append("end_date = %s")
        values.append(end_date)
    if is_active is not None:
        updates.append("is_active = %s")
        values.append(is_active)

    if not updates:
        raise ValueError("No se proporcionaron campos válidos para actualizar.")

    query = f"UPDATE customer_memberships SET {', '.join(updates)} WHERE customer_membership_id = %s"
    values.append(customer_membership_id)

    db.execute(query, tuple(values))
    db.commit()

def delete_customer_membership_by_id(db: MySQLConnection, customer_membership_id):
    """
    Elimina una relación cliente-membresía por su ID.
    """
    db.execute("DELETE FROM customer_memberships WHERE customer_membership_id = %s", (customer_membership_id,))
    db.commit()
