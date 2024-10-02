import math
import random
import matplotlib.pyplot as plt
import mysql.connector

# Función para calcular la serie de Fourier para la función seno
def serie_fourier_seno(x, nmax):
    sumatoria = 0
    for n in range(1, nmax + 1):  # La serie de Fourier para seno comienza en n=1
        # Término de la serie de Fourier para seno: (2 / (n * π)) * (1 - (-1)^n)
        termino = (2 / (n * math.pi)) * (1 - (-1)**n) * math.sin(n * x)
        sumatoria += termino
    return sumatoria

# Función para generar valores con ruido
def generar_valores_funcion_fourier_con_ruido(num_puntos, nmax):
    x_vals = []
    original_vals = []
    ruido_vals = []
    error_vals = []
    
    for i in range(num_puntos):
        x = i * (2 * math.pi / num_puntos)  # Espaciado de puntos entre 0 y 2*pi
        y_original = serie_fourier_seno(x, nmax)  # Valor original de la serie
        
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

# Función para guardar los datos en la base de datos
def guardar_registros_bd(original_vals, ruido_vals, error_vals, id_usuario, tipo_serie="fourier"):
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
def leer_desde_bd(id_usuario, tipo_serie="fourier"):
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

# Ejemplo de uso
if __name__ == "__main__":
    num_puntos = 100
    nmax = 10  # Número máximo de términos en la serie de Fourier
    id_usuario = 1  # ID de usuario para la base de datos

    x_vals, original_vals, ruido_vals, error_vals = generar_valores_funcion_fourier_con_ruido(num_puntos, nmax)
    
    # Guardar en base de datos
    guardar_registros_bd(original_vals, ruido_vals, error_vals, id_usuario)

    # Graficar resultados
    plt.plot(x_vals, original_vals, label='Serie de Fourier (sin ruido)')
    plt.plot(x_vals, ruido_vals, label='Valores con ruido', linestyle='--')
    plt.title('Serie de Fourier para Seno')
    plt.xlabel('x')
    plt.ylabel('Valor')
    plt.legend()
    plt.show()
