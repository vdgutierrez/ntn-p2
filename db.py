import mysql.connector as mysql
from mysql.connector import Error

def db_connection():
    try:
        conexion = mysql.connect(
            host="localhost",
            user="root",
            password="",
            database="Proyecto2",
            port=3306   
        )
        if conexion.is_connected():
            print("Conexión exitosa")
            return conexion
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

    return conexion