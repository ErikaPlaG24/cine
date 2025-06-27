import mysql.connector

class MySQLConnection:

    """
    Clase de conexión a base de datos MySQL.

    Esta clase proporciona métodos para conectarse a una base de datos MySQL, ejecutar consultas,
    obtener resultados y gestionar transacciones. Utiliza la librería mysql-connector-python.

    El parámetro 'dictionary' en el método cursor() de MySQL Connector/Python
    determina si los resultados de las consultas se devuelven como:
    - diccionarios (True)
    - tuplas (False).
    """

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MySQLConnection, cls).__new__(cls)
        return cls._instance

    def __init__(
        self,
        host="localhost",
        port=3306,
        user=None,
        password=None,
        database=None,
        dictionary=True
    ):
        if not self.__class__._initialized:
            self._host = host
            self._port = port
            self._user = user
            self._password = password
            self._database = database
            self._dictionary = dictionary
            self._connect()
            self.__class__._initialized = True

    def _connect(self):
        self.conn = mysql.connector.connect(
            host=self._host,
            port=self._port,
            user=self._user,
            password=self._password,
            database=self._database,
            time_zone='America/Mexico_City',
            autocommit=True  # CRITICAL CHANGE - enable autocommit
        )
        self.cursor = self.conn.cursor(dictionary=self._dictionary)

    def _ensure_cursor(self):
        """
        Asegura que el cursor esté abierto y actualizado.
        """
        if self.cursor is None or not self.conn.is_connected():
            self.reconnect()

    def reconnect(self):
        """
        Reabre la conexión a la base de datos si está cerrada y reinicia el cursor.
        """
        try:
            if not self.conn.is_connected():
                self._connect()
            else:
                try:
                    self.cursor.close()
                except Exception:
                    pass
                self.cursor = self.conn.cursor(dictionary=self._dictionary)
        except Exception:
            self._connect()

    def execute(self, query, params=None):
        """
        Ejecuta una consulta SQL con parámetros opcionales.
        """
        self._ensure_cursor()
        self.cursor.execute(query, params or ())


    def fetchone(self):
        """
        Obtiene la siguiente fila del conjunto de resultados de la consulta.
        """
        return self.cursor.fetchone()


    def fetchall(self):
        """
        Obtiene todas las filas restantes del conjunto de resultados de la consulta.
        """
        return self.cursor.fetchall()


    def commit(self):
        """
        Confirma la transacción actual.
        """
        self.conn.commit()


    def lastrowid(self):
        """
        Devuelve el ID de la última fila insertada.
        """
        return self.cursor.lastrowid


    def rowcount(self):
        """
        Devuelve el número de filas afectadas por la última ejecución de execute().
        """
        return self.cursor.rowcount


    def close(self):
        """
        Cierra el cursor y la conexión a la base de datos.
        """
        self.cursor.close()
        self.conn.close()