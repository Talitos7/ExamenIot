import mysql.connector
from tkinter import *
import requests
from tkinter import Tk, Frame, Label, Entry, Button, messagebox, ttk
from tkinter import ttk, messagebox
import requests
from interfazLogin import id_usuario
from cos import generar_valores_funcion_coseno_con_ruido

def conectar():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",  # Cambia por tu usuario
        password="",  # Cambia por tu contraseña
        database="bd_series_trigonometricas"
    )
    return conexion

# Función para graficar llamando a la API Flask
def graficar():
    seleccion = obtener_seleccion()
    original_vals = [...]  # Obtener estos valores desde tu base de datos
    ruido_vals = [...]     # Obtener estos valores desde tu base de datos

    # Obtener el URL ingresado
    url_dashboard = entry_url.get()

    response = requests.post('http://127.0.0.1:5000/graficar_datos', json={
        'original_vals': original_vals,
        'ruido_vals': ruido_vals,
        'tipo_serie': seleccion,
        'url_dashboard': url_dashboard  # Agregar URL al cuerpo de la petición
    })

    if response.ok:
        messagebox.showinfo("Éxito", "Gráfico generado.")
    else:
        messagebox.showerror("Error", "No se pudo generar el gráfico.")

# Resto del código de la interfaz Tkinter
def guardar_registros(original_vals, ruido_vals, error_vals, id_usuario, tipo_serie="coseno"):
    try:
        conexion = conectar()
        cursor = conexion.cursor()

        for i in range(len(original_vals)):
            consulta = "INSERT INTO registros (valor_calculado, valor_con_ruido, error, id_usuario, tipo_serie) VALUES (%s, %s, %s, %s, %s)"
            valores = (original_vals[i], ruido_vals[i], error_vals[i], id_usuario, tipo_serie)
            cursor.execute(consulta, valores)

        conexion.commit()
    except mysql.connector.Error as error:
        messagebox.showerror("Error", f"No se pudo conectar a la base de datos: {error}")
    finally:
        cursor.close()
        conexion.close()

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

def obtener_seleccion():
    return combobox.get()

def insertar_valores():
    seleccion = obtener_seleccion()
    nmax = int(entry_terminos.get())
    num_puntos = int(entry_registros.get())

    # Aquí puedes llamar a una función específica según la serie seleccionada
    original_vals, ruido_vals, error_vals = generar_valores_funcion_coseno_con_ruido(num_puntos, nmax)
    
    guardar_registros(original_vals, ruido_vals, error_vals, id_usuario, tipo_serie=seleccion)
    messagebox.showinfo("Éxito", f"Valores de {seleccion} guardados en la base de datos.")

# Frame para los botones
frame_botones = Frame(root)
frame_botones.pack(pady=10)

btn_insertar = Button(frame_botones, text="Insertar valores", command=insertar_valores)
btn_insertar.grid(row=0, column=0, padx=5)

# Botón para graficar
btn_graficar = Button(frame_botones, text="Graficar", command=graficar)
btn_graficar.grid(row=0, column=1, padx=5)

# Campo de entrada para el URL del dashboard
Label(frame_botones, text="URL del Dashboard:").grid(row=1, column=0, padx=5, pady=5)
entry_url = Entry(frame_botones, width=40)
entry_url.grid(row=1, column=1, padx=5, pady=5)

root.mainloop()
