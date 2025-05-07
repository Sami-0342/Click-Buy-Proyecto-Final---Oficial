import pyodbc
from config import Config

def get_connection():
    """
    Devuelve una conexión pyodbc con la cadena ya validada.
    Si falla, lanza la excepción para que Flask la muestre en debug.
    """
    conn_str = Config.get_connection_string()
    # Opcional: imprime para depurar
    print("Cadena de conexión:", conn_str)
    return pyodbc.connect(conn_str)


# Función para obtener los datos de una tabla específica
def obtener_datos(tabla):
    conexion = get_connection()
    if not conexion:
        return []
    try:
        cursor = conexion.cursor()
        query = f"SELECT * FROM {tabla}"
        cursor.execute(query)
        columnas = [column[0] for column in cursor.description]
        datos = [dict(zip(columnas, row)) for row in cursor.fetchall()]
        return datos
    except Exception as ex:
        print(f"❌ Error al obtener datos de {tabla}: {ex}")
        return []
    finally:
        conexion.close()

# Función para actualizar un registro
def actualizar_registro(tabla, id, columna, valor):
    conexion = get_connection()
    if not conexion:
        return {"success": False, "mensaje": "No se pudo conectar a la base de datos"}
    try:
        cursor = conexion.cursor()
        query = f"UPDATE {tabla} SET {columna} = ? WHERE id = ?"
        cursor.execute(query, (valor, id))
        conexion.commit()
        return {"success": True, "mensaje": "Registro actualizado"}
    except Exception as e:
        return {"success": False, "mensaje": str(e)}
    finally:
        conexion.close()

# Función para eliminar un registro
def eliminar_registro(tabla, id):
    conexion = get_connection()
    if not conexion:
        return {"success": False, "mensaje": "No se pudo conectar a la base de datos"}
    try:
        cursor = conexion.cursor()
        query = f"DELETE FROM {tabla} WHERE id = ?"
        cursor.execute(query, (id,))
        conexion.commit()
        return {"success": True, "mensaje": "Registro eliminado"}
    except Exception as e:
        return {"success": False, "mensaje": str(e)}
    finally:
        conexion.close()

# Función para insertar un registro
def insertar_registro(tabla, datos):
    conexion = get_connection()
    if not conexion:
        return {"success": False, "mensaje": "No se pudo conectar a la base de datos"}
    try:
        cursor = conexion.cursor()
        columnas = ", ".join(datos.keys())
        placeholders = ", ".join(["?"] * len(datos))
        valores = list(datos.values())
        query = f"INSERT INTO {tabla} ({columnas}) VALUES ({placeholders})"
        cursor.execute(query, valores)
        conexion.commit()
        return {"success": True}
    except Exception as e:
        return {"success": False, "mensaje": str(e)}
    finally:
        conexion.close()

# Funciones específicas para obtener datos de tablas
def obtener_empleados():
    return obtener_datos("empleado")

def obtener_clientes():
    return obtener_datos("cliente")

def obtener_producto():
    return obtener_datos("producto")

def obtener_venta():
    return obtener_datos("venta")

def obtener_cuenta():
    return obtener_datos("cuenta")
