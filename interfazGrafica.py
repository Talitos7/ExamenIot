import mysql.connector
import math
import random
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import ttk, messagebox
from interfazLogin import id_usuario
from cos import generar_valores_funcion_coseno_con_ruido


# Función para conectar a la base de datos
def conectar():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",  # Cambia por tu usuario
        password="",  # Cambia por tu contraseña
        database="bd_series_trigonometricas"
    )
    return conexion
def borrar_datos():
    try:
        tipo_serie = obtener_seleccion()
        conexion = conectar()
        cursor = conexion.cursor()
        
        consulta = "DELETE FROM registros WHERE id_usuario = %s AND tipo_serie = %s"
        valores = (id_usuario, tipo_serie)
        cursor.execute(consulta, valores)

        conexion.commit()
        cursor.close()
        conexion.close()
        
        messagebox.showinfo("Éxito", "Datos borrados correctamente.")
    except mysql.connector.Error as error:
        messagebox.showerror("Error", f"No se pudo borrar los datos: {error}")
# Función para guardar los registros en la base de datos
def guardar_registros(original_vals, ruido_vals, error_vals, id_usuario, tipo_serie="coseno"):
    try:
        conexion = conectar()
        cursor = conexion.cursor()

        for i in range(len(original_vals)):
            consulta = "INSERT INTO registros (valor_calculado, valor_con_ruido, error, id_usuario, tipo_serie) VALUES (%s, %s, %s, %s, %s)"
            valores = (original_vals[i], ruido_vals[i], error_vals[i], id_usuario, tipo_serie)
            cursor.execute(consulta, valores)

        conexion.commit()
        cursor.close()
        conexion.close()

    except mysql.connector.Error as error:
        messagebox.showerror("Error", f"No se pudo conectar a la base de datos: {error}")

# Función para graficar
def graficar():
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        
        # Obtener el tipo de serie seleccionado
        tipo_serie = obtener_seleccion()
        
        # Consulta SQL para obtener los datos filtrados
        sql = "SELECT valor_calculado, valor_con_ruido, error FROM registros WHERE tipo_serie = %s AND id_usuario = %s"
        cursor.execute(sql, (tipo_serie, id_usuario))
        resultados = cursor.fetchall()

        # Listas para almacenar los datos
        valor_calculado = []
        valor_con_ruido = []
        error = []

        # Procesar los resultados
        for fila in resultados:
            valor_calculado.append(fila[0])   # Valor calculado
            valor_con_ruido.append(fila[1])    # Valor con ruido
            error.append(fila[2])              # Error

        # Cerrar la conexión
        cursor.close()
        conexion.close()

        # Graficar los resultados
        plt.figure(figsize=(10, 6))
        plt.plot(valor_calculado, label="Valor Calculado", marker='o')
        plt.plot(valor_con_ruido, label="Valor con Ruido", marker='x')
        plt.plot(error, label="Error", linestyle='--', color='red')

        # Personalización del gráfico
        plt.title(f"Gráfico de la serie: {tipo_serie}")
        plt.xlabel("Índice")
        plt.ylabel("Valores")
        plt.legend()
        plt.grid(True)

        # Mostrar el gráfico
        plt.show()

    except mysql.connector.Error as error:
        messagebox.showerror("Error", f"No se pudo obtener los datos: {error}")

# Crear la ventana principal con Tkinter
root = Tk()
root.title("SERIE TRIGONOMÉTRICA")
root.geometry("800x600")

# Frame para entradas de datos
frame_inputs = Frame(root)
frame_inputs.pack(pady=10)

# Etiquetas y entradas de datos
Label(frame_inputs, text="Número de términos").grid(row=1, column=0, padx=5, pady=5)
entry_terminos = Entry(frame_inputs)
entry_terminos.grid(row=1, column=1, padx=5, pady=5)

Label(frame_inputs, text="Cantidad de registros").grid(row=2, column=0, padx=5, pady=5)
entry_registros = Entry(frame_inputs)
entry_registros.grid(row=2, column=1, padx=5, pady=5)

# Frame para el ComboBox
frame_combobox = Frame(root)
frame_combobox.pack(pady=10)

Label(frame_combobox, text="Selecciona la serie trigonométrica:").grid(row=0, column=0, padx=5, pady=5)

series_options = ["seno", "coseno", "fourier"]
combobox = ttk.Combobox(frame_combobox, values=series_options)
combobox.grid(row=0, column=1, padx=5, pady=5)
combobox.current(0)

# Función para obtener el valor seleccionado
def obtener_seleccion():
    seleccion = combobox.get()
    return seleccion

# Función para insertar valores en la base de datos
def insertar_valores():
    seleccion = obtener_seleccion()
    nmax = int(entry_terminos.get())
    num_puntos = int(entry_registros.get())
    
    if seleccion == "coseno":
        original_vals, ruido_vals, error_vals = generar_valores_funcion_coseno_con_ruido(num_puntos, nmax)
        guardar_registros(original_vals, ruido_vals, error_vals, id_usuario, tipo_serie="coseno")
        messagebox.showinfo("Éxito", "Valores de coseno guardados en la base de datos.")
    elif seleccion == "seno":
        original_vals, ruido_vals, error_vals = generar_valores_funcion_coseno_con_ruido(num_puntos, nmax)
        guardar_registros(original_vals, ruido_vals, error_vals, id_usuario, tipo_serie="seno")
        messagebox.showinfo("Éxito", "Valores de seno guardados en la base de datos.")
    elif seleccion == "fourier":
        original_vals, ruido_vals, error_vals = generar_valores_funcion_coseno_con_ruido(num_puntos, nmax)
        guardar_registros(original_vals, ruido_vals, error_vals, id_usuario, tipo_serie="fourier")
        messagebox.showinfo("Éxito", "Valores de fourier guardados en la base de datos.")    
    else:
        messagebox.showwarning("Advertencia", "Funcionalidad no implementada para la serie seleccionada.")

# Frame para los botones
frame_botones = Frame(root)
frame_botones.pack(pady=10)

# Botón para insertar valores
btn_insertar = Button(frame_botones, text="Insertar valores", command=insertar_valores)
btn_insertar.grid(row=0, column=0, padx=5)

# Botón para graficar
btn_graficar = Button(frame_botones, text="Graficar", command=graficar)
btn_graficar.grid(row=0, column=1, padx=5)
# Botón para borrar datos
btn_borrar = Button(frame_botones, text="Borrar datos", command=borrar_datos)
btn_borrar.grid(row=0, column=2, padx=5)
root.mainloop()
