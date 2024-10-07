import mysql.connector as mysql
from mysql.connector import Error

def db_connection():
    try:
        conexion = mysql.connect(
            host="sql10.freemysqlhosting.net",
            user="sql10735588",
            password="45LIBtXYi7",
            database="sql10735588",
            port=3308
        )
        if conexion.is_connected():
            print("Conexión exitosa")
            return conexion
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

    return conexion

db_connection()

