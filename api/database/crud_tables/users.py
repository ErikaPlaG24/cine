from database.mysql_connection import MySQLConnection
from helpers.hash import hash_password



#           .______       _______       ___        _______  
#           |   _  \     |   ____|     /   \      |       \ 
#           |  |_)  |    |  |__       /  ^  \     |  .--.  |
#           |      /     |   __|     /  /_\  \    |  |  |  |
#           |  |\  \---. |  |____   /  _____  \   |  '--'  |
#           | _| `.____| |_______| /__/     \__\  |_______/ 



def get_all_users(db: MySQLConnection, roles="all"):
    """
    Obtiene usuarios filtrando por roles válidos o 'all' para todos.
    """
    valid_roles = {'admin', 'employee', 'customer'}
    base_query = "SELECT * FROM users"
    params = []

    if roles != "all":
        if not isinstance(roles, (list, tuple)):
            raise ValueError("roles debe ser una lista, tupla o 'all'.")
        invalid_roles = set(roles) - valid_roles
        if invalid_roles:
            raise ValueError(f"Roles inválidos: {', '.join(invalid_roles)}")
        placeholders = ','.join(['%s'] * len(roles))
        base_query += f" WHERE role IN ({placeholders})"
        params.extend(roles)

    db.execute(base_query, tuple(params))
    return db.fetchall()

def get_all_active_users(db: MySQLConnection, roles="all"):
    """
    Obtiene todos los usuarios activos de la tabla 'users', filtrando por roles válidos o 'all' para todos.
    """
    valid_roles = {'admin', 'employee', 'customer'}
    base_query = "SELECT * FROM users WHERE is_active = 1"
    params = []

    if roles != "all":
        if not isinstance(roles, (list, tuple)):
            raise ValueError("roles debe ser una lista, tupla o 'all'.")
        invalid_roles = set(roles) - valid_roles
        if invalid_roles:
            raise ValueError(f"Roles inválidos: {', '.join(invalid_roles)}")
        placeholders = ','.join(['%s'] * len(roles))
        base_query += f" AND role IN ({placeholders})"
        params.extend(roles)

    db.execute(base_query, tuple(params))
    return db.fetchall()

def get_id_by_username(db: MySQLConnection, username):
    """
    Obtiene el ID de un usuario por su nombre de usuario.
    """
    db.execute("SELECT user_id FROM users WHERE username = %s", (username,))
    result = db.fetchone()
    return result["user_id"] if result else None

def get_value_from_user_by_id(db: MySQLConnection, user_id, column_name):
    """
    Obtiene un valor específico de un usuario por su ID.
    Permite obtener cualquier columna de la tabla 'users'.
    """
    db.execute(f"SELECT {column_name} FROM users WHERE user_id = %s", (user_id,))
    result = db.fetchone()
    return result[column_name] if result else None

def search_user_by_name(db: MySQLConnection, search_term, roles="all"):
    """
    Busca usuarios por coincidencias parciales en nombre, apellido o ambos, ordenados por mayor coincidencia.
    Puede filtrar por roles (lista de roles válidos o 'all' para todos).
    """
    valid_roles = {'admin', 'employee', 'customer'}
    search = f"%{search_term}%"
    base_query = """
        SELECT *,
            (CASE WHEN first_name LIKE %s THEN 1 ELSE 0 END +
             CASE WHEN last_name LIKE %s THEN 1 ELSE 0 END +
             CASE WHEN CONCAT_WS(' ', first_name, last_name) LIKE %s THEN 1 ELSE 0 END
            ) AS match_score
        FROM users
        WHERE (first_name LIKE %s OR last_name LIKE %s OR CONCAT_WS(' ', first_name, last_name) LIKE %s)
    """
    params = [search, search, search, search, search, search]

    if roles != "all":
        if not isinstance(roles, (list, tuple)):
            raise ValueError("roles debe ser una lista, tupla o 'all'.")
        invalid_roles = set(roles) - valid_roles
        if invalid_roles:
            raise ValueError(f"Roles inválidos: {', '.join(invalid_roles)}")
        placeholders = ','.join(['%s'] * len(roles))
        base_query += f" AND role IN ({placeholders})"
        params.extend(roles)

    base_query += " ORDER BY match_score DESC, first_name, last_name"
    db.execute(base_query, tuple(params))
    return db.fetchall()

def get_if_user_exists(db: MySQLConnection, username):
    """
    Verifica si un usuario existe en la tabla 'users' por su nombre de usuario.
    Retorna True si existe, False si no.
    """
    db.execute("SELECT COUNT(*) as count FROM users WHERE username = %s", (username,))
    result = db.fetchone()
    return result["count"] > 0

def get_if_user_is_active_by_id(db: MySQLConnection, user_id):
    """
    Verifica si un usuario está activo por su ID.
    Retorna True si está activo, False si no.
    """
    db.execute("SELECT is_active FROM users WHERE user_id = %s", (user_id,))
    result = db.fetchone()
    if not result:
        raise ValueError(f"No se encontró un usuario con ID {user_id}.")
    if result["is_active"] == 1:
        return True
    else:
        return False

def get_hashed_password_by_id(db: MySQLConnection, user_id):
    """
    Obtiene la contraseña hasheada de un usuario por su ID.
    """
    db.execute("SELECT password FROM users WHERE user_id = %s", (user_id,))
    result = db.fetchone()
    return result["password"] if result else None

def get_password_updated_at_by_id(db: MySQLConnection, user_id):
    """
    Obtiene la fecha de última actualización de la contraseña de un usuario por su ID.
    """
    db.execute("SELECT password_updated_at FROM users WHERE user_id = %s", (user_id,))
    result = db.fetchone()
    return result["password_updated_at"] if result else None



#             ______   ______       _______       ___       .___________.  _______ 
#            /      | |   _  \     |   ____|     /   \      |           | |   ____|
#           |  ,----' |  |_)  |    |  |__       /  ^  \     `---|  |----` |  |__   
#           |  |      |      /     |   __|     /  /_\  \        |  |      |   __|  
#           |  `----. |  |\  \---. |  |____   /  _____  \       |  |      |  |____ 
#            \______| | _| `.____| |_______| /__/     \__\      |__|      |_______|



def create_user(db: MySQLConnection, username, password, first_name, lastname, phone, role="customer"):
    """
    Crea un nuevo usuario en la tabla 'users'.
    """
    if role not in ['admin', 'employee', 'customer']:
        raise ValueError("El rol debe ser 'customer', 'employee' o 'admin'.")
    db.execute(
        """
        INSERT INTO users (username, password, first_name, last_name, role, phone, is_active)
        VALUES (%s, %s, %s, %s, %s, %s, 1)
        """,
        (username, hash_password(password), first_name, lastname, role, phone)
    )
    db.commit()



#            __    __   .______     _______        ___       .___________.  _______ 
#           |  |  |  |  |   _  \   |       \      /   \      |           | |   ____|
#           |  |  |  |  |  |_)  |  |  .--.  |    /  ^  \     `---|  |----` |  |__   
#           |  |  |  |  |   ___/   |  |  |  |   /  /_\  \        |  |      |   __|  
#           |  `--'  |  |  |       |  '--'  |  /  _____  \       |  |      |  |____ 
#            \______/   | _|       |_______/  /__/     \__\      |__|      |_______|

         
                                                                   
def update_user_by_id(
    db: MySQLConnection,
    user_id,
    username=None,
    password=None,
    first_name=None,
    last_name=None,
    phone=None,
    role=None,
    is_active=None,
):
    """
    Actualiza los datos de un usuario en la tabla 'users' por su ID.
    Solo se pueden editar: username, password, first_name, last_name, role, phone, is_active.
    """
    updates = []
    values = []

    if username is not None:
        updates.append("username = %s")
        values.append(username)
    if password is not None:
        updates.append("password = %s")
        values.append(hash_password(password))
        updates.append("password_updated_at = CURRENT_TIMESTAMP")
    if first_name is not None:
        updates.append("first_name = %s")
        values.append(first_name)
    if last_name is not None:
        updates.append("last_name = %s")
        values.append(last_name)
    if role is not None:
        updates.append("role = %s")
        values.append(role)
    if phone is not None:
        updates.append("phone = %s")
        values.append(phone)
    if is_active is not None:
        updates.append("is_active = %s")
        values.append(is_active)

    if not updates:
        raise ValueError("No se proporcionaron campos válidos para actualizar.")

    query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = %s"
    values.append(user_id)

    db.execute(query, tuple(values))
    db.commit()



#           _______    _______   __       _______  .___________.  _______ 
#          |       \  |   ____| |  |     |   ____| |           | |   ____|
#          |  .--.  | |  |__    |  |     |  |__    `---|  |----` |  |__   
#          |  |  |  | |   __|   |  |     |   __|       |  |      |   __|  
#          |  '--'  | |  |____  |  `---. |  |____      |  |      |  |____ 
#          |_______/  |_______| |______| |_______|     |__|      |_______|



def delete_user_by_id(db: MySQLConnection, user_id):
    """
    Elimina un usuario de la tabla 'users' por su ID.
    """
    db.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
    db.commit()