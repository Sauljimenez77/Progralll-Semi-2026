
import mysql.connector

CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "",
    "database": "db_academica"
}


class Conexion:

    def conectar(self):
        ultimo_error = None

        for puerto in (3307, 3306):
            try:
                conexion = mysql.connector.connect(
                    **CONFIG,
                    port=puerto,
                    connection_timeout=4,
                    use_pure=True
                )
                return conexion

            except Exception as error:
                ultimo_error = error
                print(f"No se pudo conectar al puerto {puerto}: {error}")

        raise RuntimeError(
            f"No se pudo conectar a MySQL: {ultimo_error}"
        )

    def consultar(self, sql, valores=()):
        conexion = self.conectar()

        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(sql, valores)

            resultado = cursor.fetchall()
            cursor.close()

            return resultado

        finally:
            conexion.close()

    def ejecutar(self, sql, valores=()):
        conexion = self.conectar()

        try:
            cursor = conexion.cursor()
            cursor.execute(sql, valores)

            conexion.commit()
            filas = cursor.rowcount
            cursor.close()

            return filas

        finally:
            conexion.close()


def preparar_base():
    conexion = None
    ultimo_error = None

    for puerto in (3307, 3306):
        try:
            conexion = mysql.connector.connect(
                host=CONFIG["host"],
                user=CONFIG["user"],
                password=CONFIG["password"],
                port=puerto,
                connection_timeout=4,
                use_pure=True
            )

            print(f"Conectado a MySQL en el puerto {puerto}")
            break

        except Exception as error:
            ultimo_error = error
            print(f"Error en puerto {puerto}: {error}")

    if conexion is None:
        raise RuntimeError(
            f"No se pudo conectar a MySQL: {ultimo_error}"
        )

    try:
        cursor = conexion.cursor()

        cursor.execute(
            """
            CREATE DATABASE IF NOT EXISTS db_academica
            CHARACTER SET utf8mb4
            COLLATE utf8mb4_unicode_ci
            """
        )

        cursor.execute("USE db_academica")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios_USSS012525 (
                idUsuario INT(10) NOT NULL AUTO_INCREMENT PRIMARY KEY,
                usuario CHAR(35) NOT NULL UNIQUE,
                clave CHAR(35) NOT NULL,
                nombre CHAR(85) NOT NULL,
                direccion CHAR(100) NOT NULL,
                telefono CHAR(9) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )

        conexion.commit()
        cursor.close()

        print("Base de datos db_academica preparada correctamente")
        print("Tabla usuarios_USSS012525 lista")

    finally:
        conexion.close()
