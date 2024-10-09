import tkinter as tk
from tkinter import messagebox
import mysql.connector
import math
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk
#import cos
#import seno
#import fourier

global id_usuario
id_usuario = None
global root

# Función para conectar a la base de datos
def conectar():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="bd_series_trigonometricas"
    )
    return conexion

# Función de verificación de inicio de sesión
def verificar():
    global id_usuario 
    nombre = entry_nombre.get()
    email = entry_email.get()

    if nombre == "" or email == "":
        messagebox.showerror("Error", "Por favor, complete todos los campos.")
    else:
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            consulta = "SELECT id_usuario FROM usuario WHERE nombre = %s AND correo = %s"
            cursor.execute(consulta, (nombre, email))
            resultado = cursor.fetchone()

            if resultado:
                id_usuario = resultado[0]
                messagebox.showinfo("Inicio de sesión", f"Bienvenido/a {nombre}. Tu ID es: {id_usuario}")
                root.withdraw()  # Ocultar la ventana de inicio de sesión
                ventanaPrincipal(id_usuario)  # Mostrar la ventana principal
            else:
                messagebox.showerror("Error", "Usuario no encontrado. Verifique los datos.")
            
            cursor.close()
            conexion.close()

        except mysql.connector.Error as error:
            messagebox.showerror("Error", f"No se pudo conectar a la base de datos: {error}")

# Función para graficar la serie dentro del Frame de Tkinter
def graficar_serie(id_usuario, tipo_serie, frame_grafica):
    for widget in frame_grafica.winfo_children():
        widget.destroy()

    fig, ax = plt.subplots(figsize=(8, 6))

    if tipo_serie == "coseno":
        original_vals, ruido_vals, error_vals = cos.leer_desde_bd(id_usuario, tipo_serie)
    elif tipo_serie == "seno":
        original_vals, ruido_vals, error_vals = seno.leer_desde_bd(id_usuario, tipo_serie)
    elif tipo_serie == "fourier":
        original_vals, ruido_vals, error_vals = fourier.leer_desde_bd(id_usuario, tipo_serie)

    if not original_vals:
        messagebox.showwarning("Advertencia", f"No hay datos disponibles para la serie {tipo_serie}")
        return

    ax.plot(range(len(original_vals)), original_vals, label=f"Serie {tipo_serie.capitalize()} (Original)", marker='o')
    ax.plot(range(len(ruido_vals)), ruido_vals, label=f"Serie {tipo_serie.capitalize()} (Con Ruido)", marker='x')
    ax.plot(range(len(error_vals)), error_vals, label="Error", linestyle='--', color='red')

    ax.set_title(f"Aproximación de la Serie de Taylor de {tipo_serie.capitalize()} (desde BD)")
    ax.set_xlabel("id_registro")
    ax.set_ylabel("Valor de la Serie")
    ax.legend()
    ax.grid(True)

    canvas = FigureCanvasTkAgg(fig, master=frame_grafica)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Función para insertar valores en la base de datos
def insertar_valores(entry_terminos, entry_registros, combobox, id_usuario):
    seleccion = combobox.get()
    nmax = int(entry_terminos.get())
    num_puntos = int(entry_registros.get())
    
    if seleccion == "coseno":
        original_vals, ruido_vals, error_vals = cos.generar_valores_funcion_coseno_con_ruido(num_puntos, nmax)
        guardar_registros(original_vals, ruido_vals, error_vals, id_usuario, tipo_serie="coseno")
    elif seleccion == "seno":
        x_vals, original_vals, ruido_vals, error_vals = seno.generar_valores_funcion_seno_con_ruido(num_puntos, nmax)
        guardar_registros(original_vals, ruido_vals, error_vals, id_usuario, tipo_serie="seno")
    elif seleccion == "fourier":
        x_vals, original_vals, ruido_vals, error_vals = fourier.generar_valores_funcion_fourier_con_ruido(num_puntos, nmax)
        guardar_registros(original_vals, ruido_vals, error_vals, id_usuario, tipo_serie="fourier")

# Función para la ventana principal
def ventanaPrincipal(id_usuario):
    ventana = tk.Toplevel(root)
    ventana.title("SERIE TRIGONOMÉTRICA")
    ventana.geometry("800x600")

    frame_inputs = tk.Frame(ventana)
    frame_inputs.pack(pady=10)

    tk.Label(frame_inputs, text="Número de términos").grid(row=1, column=0, padx=5, pady=5)
    entry_terminos = tk.Entry(frame_inputs)
    entry_terminos.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(frame_inputs, text="Cantidad de registros").grid(row=2, column=0, padx=5, pady=5)
    entry_registros = tk.Entry(frame_inputs)
    entry_registros.grid(row=2, column=1, padx=5, pady=5)

    frame_combobox = tk.Frame(ventana)
    frame_combobox.pack(pady=10)

    tk.Label(frame_combobox, text="Selecciona la serie trigonométrica:").grid(row=0, column=0, padx=5, pady=5)

    series_options = ["seno", "coseno", "fourier"]
    combobox = ttk.Combobox(frame_combobox, values=series_options)
    combobox.grid(row=0, column=1, padx=5, pady=5)
    combobox.current(0)

    frame_botones = tk.Frame(ventana)
    frame_botones.pack(pady=10)
    
    frame_grafica = tk.Frame(ventana)
    frame_grafica.pack(pady=20, fill=tk.BOTH, expand=True)

    btn_insertar = tk.Button(frame_botones, text="Insertar valores", 
                             command=lambda: insertar_valores(entry_terminos, entry_registros, combobox, id_usuario))
    btn_insertar.grid(row=0, column=0, padx=5)

    btn_graficar = tk.Button(frame_botones, text="Graficar", 
                             command=lambda: graficar_serie(id_usuario, combobox.get(), frame_grafica))
    btn_graficar.grid(row=0, column=1, padx=5)

# Ventana de inicio de sesión
def ventanaInicioSesion():
    global root
    root = tk.Tk()
    root.title("Inicio de Sesión")
    root.geometry("300x250")

    tk.Label(root, text="Inicio de Sesión", font=("Arial", 14)).pack(pady=10)

    tk.Label(root, text="Nombre:").pack(pady=5)
    global entry_nombre
    entry_nombre = tk.Entry(root, width=30)
    entry_nombre.pack(pady=5)

    tk.Label(root, text="Correo Electrónico:").pack(pady=5)
    global entry_email
    entry_email = tk.Entry(root, width=30)
    entry_email.pack(pady=5)

    tk.Button(root, text="Iniciar Sesión", command=verificar).pack(pady=10)
    root.mainloop()

ventanaInicioSesion()

