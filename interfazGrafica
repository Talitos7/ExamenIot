import mysql.connector
import math
import matplotlib.pyplot as plt
import random
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from interfazLogin import id_usuario

# Función para conectar a la base de datos
def conectar():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",  # Cambia por tu usuario
        password="",  # Cambia por tu contraseña
        database="bd_series_trigonometricas"
    )
    return conexion








# Crear la ventana principal con Tkinter
root = Tk()
root.title("SERIE DE FIBONACCI")
root.geometry("800x600")

# Frame para entradas de datos
frame_inputs = Frame(root)
frame_inputs.pack(pady=10)

# Etiquetas y entradas de datos
Label(frame_inputs, text="Número de términos").grid(row=1, column=0, padx=5, pady=5)
entry_terminos = Entry(frame_inputs)
entry_terminos.grid(row=1, column=1, padx=5, pady=5)

# Frame para el ComboBox
frame_combobox = Frame(root)
frame_combobox.pack(pady=10)

# Etiqueta para el ComboBox
Label(frame_combobox, text="Selecciona la serie trigonométrica:").grid(row=0, column=0, padx=5, pady=5)

# ComboBox para seleccionar la serie trigonométrica
series_options = ["seno", "coseno", "fourier"]
combobox = ttk.Combobox(frame_combobox, values=series_options)
combobox.grid(row=0, column=1, padx=5, pady=5)
combobox.current(0)  # Selecciona por defecto la primera opción ('seno')

# Frame para los botones
frame_botones = Frame(root)
frame_botones.pack(pady=10)

# Botón para insertar valores
btn_insertar = Button(frame_botones, text="Insertar valores", command="")
btn_insertar.grid(row=0, column=0, padx=5)

# Botón para graficar datos
btn_graficar = Button(frame_botones, text="Graficar datos", command="")
btn_graficar.grid(row=0, column=1, padx=5)

# Frame para gráficos
frame_canvas = Frame(root)
frame_canvas.pack(pady=20)

# Ejecutar la aplicación
root.mainloop()