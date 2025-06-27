import os
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(root_dir)

from database.crud_tables.users import *
from database.crud_tables.memberships import *
from database.crud_tables.movies import *
from mysql_connection import MySQLConnection
import json
from datetime import datetime

def default_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)

def main():
    db = MySQLConnection(
        host        = "localhost",
        port        = 4000,
        user        = "root",
        password    = "root",
        database    = "cine"
    )

    # Test consulta
    #resultado = update_user_by_id(db, user_id=4, is_active=True)

    #resultado = get_all_active_users(db)

    resultado = get_all_users(db)

    # Guardar resultados en un archivo JSON formateado
    with open("resultado.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=4, default=default_serializer)

    db.close()

if __name__ == "__main__":
    main()