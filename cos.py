import math
import random
import matplotlib.pyplot as plt
import csv

# Función para calcular la serie de Taylor para la función coseno
def serie_taylor_coseno(x, nmax):
    sumatoria = 0
    for n in range(nmax + 1):
        # Término de la serie de Taylor para coseno: (-1)^n * x^(2n) / (2n)!
        termino = ((-1)**n * (x**(2 * n))) / math.factorial(2 * n)
        sumatoria += termino
    return sumatoria

# Función para generar valores con ruido
def generar_valores_funcion_coseno_con_ruido(num_puntos, nmax):
    x_vals = []
    original_vals = []
    ruido_vals = []
    error_vals = []
    
    for i in range(num_puntos):
        x = i * (2 * math.pi / num_puntos)  # Espaciado de puntos entre 0 y 2*pi
        y_original = serie_taylor_coseno(x, nmax)  # Valor original de la serie
        
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

# Función para guardar los datos en un archivo CSV
def guardar_en_csv(x_vals, original_vals, ruido_vals, error_vals, usuario=1, funcion="coseno", nombre_archivo="datos_funcion_coseno.csv"):
    with open(nombre_archivo, mode='w', newline='') as archivo_csv:
        escritor_csv = csv.writer(archivo_csv)
        # Escribir la cabecera
        escritor_csv.writerow(["x", "Serie Original", "Serie con Ruido", "Error", "Usuario", "Función"])
        
        # Escribir los datos
        for i in range(len(x_vals)):
            escritor_csv.writerow([x_vals[i], original_vals[i], ruido_vals[i], error_vals[i], usuario, funcion])
    
    print(f"Datos guardados en el archivo: {nombre_archivo}")

# Función para leer los datos desde el archivo CSV
def leer_desde_csv(nombre_archivo="datos_funcion_coseno.csv"):
    x_vals = []
    original_vals = []
    ruido_vals = []
    error_vals = []
    usuarios = []
    funciones = []
    
    with open(nombre_archivo, mode='r') as archivo_csv:
        lector_csv = csv.reader(archivo_csv)
        next(lector_csv)  # Saltar la cabecera
        
        for fila in lector_csv:
            x_vals.append(float(fila[0]))
            original_vals.append(float(fila[1]))
            ruido_vals.append(float(fila[2]))
            error_vals.append(float(fila[3]))
            usuarios.append(fila[4])  # Leer el campo usuario
            funciones.append(fila[5])  # Leer el campo función
    
    return x_vals, original_vals, ruido_vals, error_vals, usuarios, funciones

# Función para graficar los resultados desde los datos del CSV
def graficar_desde_csv(nombre_archivo="datos_funcion_coseno.csv"):
    # Leer los datos desde el archivo CSV
    x_vals, original_vals, ruido_vals, error_vals, usuarios, funciones = leer_desde_csv(nombre_archivo)
    
    # Graficar los resultados
    plt.figure(figsize=(10, 6))
    
    # Graficar valores originales de la serie de Taylor
    plt.plot(x_vals, original_vals, label="Serie Coseno (Original)", marker='o')
    
    # Graficar valores con ruido
    plt.plot(x_vals, ruido_vals, label="Serie Coseno (Con Ruido)", marker='x')
    
    # Graficar el error
    plt.plot(x_vals, error_vals, label="Error", linestyle='--', color='red')
    
    # Personalización del gráfico
    plt.title("Aproximación de la Serie de Taylor de Coseno (desde CSV)")
    plt.xlabel("x")
    plt.ylabel("Valor de la Serie")
    plt.legend()
    plt.grid(True)
    
    # Mostrar el gráfico
    plt.show()

# Número de puntos a generar y número de términos en la serie de Taylor
num_puntos = 100  # Número de puntos en el gráfico
nmax = 10         # Número de términos en la serie de Taylor

# Generar los valores de la serie, con ruido y error
x_vals, original_vals, ruido_vals, error_vals = generar_valores_funcion_coseno_con_ruido(num_puntos, nmax)

# Guardar los datos en un archivo CSV, incluyendo los campos usuario y función
guardar_en_csv(x_vals, original_vals, ruido_vals, error_vals, usuario=1, funcion="coseno", nombre_archivo="datos_funcion_coseno.csv")

# Graficar los resultados leyendo desde el CSV
graficar_desde_csv("datos_funcion_coseno.csv")
