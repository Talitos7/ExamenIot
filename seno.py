import math
import random
import matplotlib.pyplot as plt
import mysql.connector

# Función para calcular la serie de Taylor para la función seno
def serie_taylor_seno(x, nmax):
    sumatoria = 0
    for n in range(nmax + 1):
        # Término de la serie de Taylor para seno: (-1)^n * x^(2n+1) / (2n+1)!
        termino = ((-1)**n * (x**(2 * n + 1))) / math.factorial(2 * n + 1)
        sumatoria += termino
    return sumatoria

# Función para generar valores con ruido
def generar_valores_funcion_seno_con_ruido(num_puntos, nmax):
    x_vals = []
    original_vals = []
    ruido_vals = []
    error_vals = []
    
    for i in range(num_puntos):
        x = i * (2 * math.pi / num_puntos)  # Espaciado de puntos entre 0 y 2*pi
        y_original = serie_taylor_seno(x, nmax)  # Valor original de la serie
        
        # Ruido proporcional a la amplitud
        ruido = random.uniform(-0.1, 0.1) * abs(y_original)  # Ruido entre [-10%, 10%] de la amplitud
        y_con_ruido = y_original + ruido  # Valor con ruido añadido
        error = abs(y_con_ruido - y_original)  # Error absoluto entre original y con ruido
        
        # Almacenar los valores
        x_vals.append(x)
        original_vals.append(y_original)
        ruido_vals.append(y_con_ruido)
        error_vals.append(error)
    
    return x_vals, original_vals, ruido_vals, error_vals

# Función para guardar los datos bd
def guardar_registros_bd(original_vals, ruido_vals, error_vals, id_usuario, tipo_serie="seno"):
    try:
        # Conexión con la base de datos
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="bd_series_trigonometricas"
        )
        cursor = conexion.cursor()

        for i in range(len(original_vals)):
            consulta = """
            INSERT INTO registros (valor_calculado, valor_con_ruido, error, id_usuario, tipo_serie) 
            VALUES (%s, %s, %s, %s, %s)
            """
            valores = (original_vals[i], ruido_vals[i], error_vals[i], id_usuario, tipo_serie)
            cursor.execute(consulta, valores)

        conexion.commit()
        print("Registros guardados en la base de datos.")
        
        cursor.close()
        conexion.close()

    except mysql.connector.Error as error:
        print(f"Error al conectar con la base de datos: {error}")

# Función para leer los datos desde la base de datos
def leer_desde_bd(id_usuario, tipo_serie = "seno"):
    try:
        # Conexión con la base de datos
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="bd_series_trigonometricas"
        )
        cursor = conexion.cursor()

        # Consultar los registros por tipo de serie
        consulta = "SELECT valor_calculado, valor_con_ruido, error FROM registros WHERE tipo_serie = %s AND id_usuario = %s"
        cursor.execute(consulta, (tipo_serie, id_usuario))

        original_vals = []
        ruido_vals = []
        error_vals = []

        for fila in cursor.fetchall():
            original_vals.append(fila[0])
            ruido_vals.append(fila[1])
            error_vals.append(fila[2])

        cursor.close()
        conexion.close()

        return original_vals, ruido_vals, error_vals

    except mysql.connector.Error as error:
        print(f"Error al conectar con la base de datos: {error}")
        return [], [], []
