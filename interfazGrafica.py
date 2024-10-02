import mysql.connector
import math
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import *
from tkinter import ttk, messagebox
import cos
import seno
import fourier

# Función para conectar a la base de datos
def conectar():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="bd_series_trigonometricas"
    )
    return conexion

#Funcion para borrar datos
def borrar_datos(combobox, id_usuario):
    try:
        tipo_serie = obtener_seleccion(combobox)
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

# Función para graficar la serie dentro del Frame de Tkinter
def graficar_serie(id_usuario, tipo_serie, frame_grafica):
    # Eliminar contenido previo en el frame de gráfica
    for widget in frame_grafica.winfo_children():
        widget.destroy()

    # Crear la figura de Matplotlib
    fig, ax = plt.subplots(figsize=(8, 6))

    if tipo_serie == "coseno":
        original_vals, ruido_vals, error_vals = cos.leer_desde_bd(id_usuario, tipo_serie)
    elif tipo_serie == "seno":
        original_vals, ruido_vals, error_vals = seno.leer_desde_bd(id_usuario, tipo_serie)
    elif tipo_serie == "fourier":
        original_vals, ruido_vals, error_vals = fourier.leer_desde_bd(id_usuario, tipo_serie)
    else:
        return

    # Si no hay datos, salir
    if not original_vals:
        messagebox.showwarning("Advertencia", f"No hay datos disponibles para la serie {tipo_serie}")
        return

    # Graficar los valores
    ax.plot(range(len(original_vals)), original_vals, label=f"Serie {tipo_serie.capitalize()} (Original)", marker='o')
    ax.plot(range(len(ruido_vals)), ruido_vals, label=f"Serie {tipo_serie.capitalize()} (Con Ruido)", marker='x')
    ax.plot(range(len(error_vals)), error_vals, label="Error", linestyle='--', color='red')

    ax.set_title(f"Aproximación de la Serie de Taylor de {tipo_serie.capitalize()} (desde BD)")
    ax.set_xlabel("id_registro")
    ax.set_ylabel("Valor de la Serie")
    ax.legend()
    ax.grid(True)

    # Crear el canvas de Matplotlib y mostrarlo en el frame de Tkinter
    canvas = FigureCanvasTkAgg(fig, master=frame_grafica)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=BOTH, expand=True)
    
# Función para obtener el valor seleccionado
def obtener_seleccion(combobox):
    seleccion = combobox.get()
    return seleccion

# Función para insertar valores en la base de datos
def insertar_valores(entry_terminos, entry_registros, combobox, id_usuario):
    seleccion = obtener_seleccion(combobox)
    nmax = int(entry_terminos.get())
    num_puntos = int(entry_registros.get())
    
    if seleccion == "coseno":
        original_vals, ruido_vals, error_vals = cos.generar_valores_funcion_coseno_con_ruido(num_puntos, nmax)
        guardar_registros(original_vals, ruido_vals, error_vals, id_usuario, tipo_serie="coseno")
        messagebox.showinfo("Éxito", "Valores de coseno guardados en la base de datos.")
    elif seleccion == "seno":
        x_vals, original_vals, ruido_vals, error_vals = seno.generar_valores_funcion_seno_con_ruido(num_puntos, nmax)
        guardar_registros(original_vals, ruido_vals, error_vals, id_usuario, tipo_serie="seno")
        messagebox.showinfo("Éxito", "Valores de seno guardados en la base de datos.")
    elif seleccion == "fourier":
        x_vals, original_vals, ruido_vals, error_vals = fourier.generar_valores_funcion_fourier_con_ruido(num_puntos, nmax)
        guardar_registros(original_vals, ruido_vals, error_vals, id_usuario, tipo_serie="fourier")
        messagebox.showinfo("Éxito", "Valores de fourier guardados en la base de datos.")    
    else:
        messagebox.showwarning("Advertencia", "Funcionalidad no implementada para la serie seleccionada.")

# Función para la ventana principal, recibe el id_usuario como argumento
def ventanaPrincipal(id_usuario):
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

    # Frame para los botones
    frame_botones = Frame(root)
    frame_botones.pack(pady=10)
    
    # Frame donde se insertará la gráfica
    frame_grafica = Frame(root)
    frame_grafica.pack(pady=20, fill=BOTH, expand=True)

    # Botón para insertar valores
    btn_insertar = Button(frame_botones, text="Insertar valores", 
                          command=lambda: insertar_valores(entry_terminos, entry_registros, combobox, id_usuario))
    btn_insertar.grid(row=0, column=0, padx=5)

    # Botón para graficar
    btn_graficar = Button(frame_botones, text="Graficar", command=lambda: graficar_serie(id_usuario, obtener_seleccion(combobox), frame_grafica))
    btn_graficar.grid(row=0, column=1, padx=5)
    
    # Botón para borrar datos
    btn_borrar = Button(frame_botones, text="Borrar datos", command=lambda: borrar_datos(combobox, id_usuario))
    btn_borrar.grid(row=0, column=2, padx=5)

    root.mainloop()
