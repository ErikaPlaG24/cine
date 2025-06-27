from database.mysql_connection import MySQLConnection



#           .______       _______       ___        _______  
#           |   _  \     |   ____|     /   \      |       \ 
#           |  |_)  |    |  |__       /  ^  \     |  .--.  |
#           |      /     |   __|     /  /_\  \    |  |  |  |
#           |  |\  \---. |  |____   /  _____  \   |  '--'  |
#           | _| `.____| |_______| /__/     \__\  |_______/ 



def get_all_memberships(db: MySQLConnection):
    """
    Obtiene todas las membresías de la tabla 'memberships'.
    """
    db.execute("SELECT * FROM memberships")
    return db.fetchall()

def get_membership_by_id(db: MySQLConnection, membership_id):
    """
    Obtiene una membresía por su ID.
    """
    db.execute("SELECT * FROM memberships WHERE membership_id = %s", (membership_id,))
    return db.fetchone()



#             ______   ______       _______       ___       .___________.  _______ 
#            /      | |   _  \     |   ____|     /   \      |           | |   ____|
#           |  ,----' |  |_)  |    |  |__       /  ^  \     `---|  |----` |  |__   
#           |  |      |      /     |   __|     /  /_\  \        |  |      |   __|  
#           |  `----. |  |\  \---. |  |____   /  _____  \       |  |      |  |____ 
#            \______| | _| `.____| |_______| /__/     \__\      |__|      |_______|



def create_membership(db: MySQLConnection, name, description=None, discount_percentage=0, monthly_price=0, benefits=None):
    """
    Crea una nueva membresía en la tabla 'memberships'.
    """
    db.execute(
        """
        INSERT INTO memberships (name, description, discount_percentage, monthly_price, benefits)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (name, description, discount_percentage, monthly_price, benefits)
    )
    db.commit()



#            __    __   .______     _______        ___       .___________.  _______ 
#           |  |  |  |  |   _  \   |       \      /   \      |           | |   ____|
#           |  |  |  |  |  |_)  |  |  .--.  |    /  ^  \     `---|  |----` |  |__   
#           |  |  |  |  |   ___/   |  |  |  |   /  /_\  \        |  |      |   __|  
#           |  `--'  |  |  |       |  '--'  |  /  _____  \       |  |      |  |____ 
#            \______/   | _|       |_______/  /__/     \__\      |__|      |_______|

         
           
def update_membership_by_id(
    db: MySQLConnection,
    membership_id,
    name=None,
    description=None,
    discount_percentage=None,
    monthly_price=None,
    benefits=None
):
    """
    Actualiza los datos de una membresía por su ID.
    """
    updates = []
    values = []

    if name is not None:
        updates.append("name = %s")
        values.append(name)
    if description is not None:
        updates.append("description = %s")
        values.append(description)
    if discount_percentage is not None:
        updates.append("discount_percentage = %s")
        values.append(discount_percentage)
    if monthly_price is not None:
        updates.append("monthly_price = %s")
        values.append(monthly_price)
    if benefits is not None:
        updates.append("benefits = %s")
        values.append(benefits)

    if not updates:
        raise ValueError("No se proporcionaron campos válidos para actualizar.")

    query = f"UPDATE memberships SET {', '.join(updates)} WHERE membership_id = %s"
    values.append(membership_id)

    db.execute(query, tuple(values))
    db.commit()



#           _______    _______   __       _______  .___________.  _______ 
#          |       \  |   ____| |  |     |   ____| |           | |   ____|
#          |  .--.  | |  |__    |  |     |  |__    `---|  |----` |  |__   
#          |  |  |  | |   __|   |  |     |   __|       |  |      |   __|  
#          |  '--'  | |  |____  |  `---. |  |____      |  |      |  |____ 
#          |_______/  |_______| |______| |_______|     |__|      |_______|



def delete_membership_by_id(db: MySQLConnection, membership_id):
    """
    Elimina una membresía por su ID.
    """
    db.execute("DELETE FROM memberships WHERE membership_id = %s", (membership_id,))
    db.commit()
