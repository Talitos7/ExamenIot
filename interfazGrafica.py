import mysql.connector
from tkinter import *
from tkinter import ttk, messagebox
from interfazLogin import id_usuario
from cos import generar_valores_funcion_coseno_con_ruido
import webbrowser  # Para abrir el link en el navegador
import threading   # Para correr Flask en un hilo separado
import requests    # Para hacer solicitudes HTTP a Flask
import dashboard   # Importa el archivo dashboard

# Función para conectar a la base de datos
def conectar():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",  # Cambia por tu usuario
        password="",  # Cambia por tu contraseña
        database="bd_series_trigonometricas"
    )
    return conexion

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

def graficar():
    nmax = int(entry_terminos.get())
    num_puntos = int(entry_registros.get())
    tipo_serie = obtener_seleccion()

    # Genera los valores para la serie trigonométrica
    original_vals, ruido_vals, error_vals = generar_valores_funcion_coseno_con_ruido(num_puntos, nmax)
    
    # Llama a la función del archivo dashboard para graficar
    dashboard.graficar_datos_serie(original_vals, ruido_vals, tipo_serie)
    
    # Simula la generación del link del gráfico
    try:
        # Hacer una petición HTTP al servidor Flask para obtener el gráfico generado
        response = requests.get(f"http://localhost:5000/datos_grafico/{tipo_serie}/{id_usuario}")
        
        if response.status_code == 200:
            link = "http://localhost:5000"  # Podrías mostrar el dashboard completo
        else:
            link = "Error al generar gráfico"
    
    except Exception as e:
        link = f"Error de conexión: {e}"

    # Muestra el link en el input de la interfaz
    entry_link.delete(0, END)
    entry_link.insert(0, link)
# Función para ejecutar Flask en un hilo separado
def iniciar_servidor_flask():
    threading.Thread(target=dashboard.app.run, kwargs={"debug": False, "use_reloader": False}).start()

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

# Input para el link del gráfico
Label(frame_combobox, text="Link del gráfico:").grid(row=1, column=0, padx=5, pady=5)
entry_link = Entry(frame_combobox, width=40)
entry_link.grid(row=1, column=1, padx=5, pady=5)

# Función para obtener el valor seleccionado
def obtener_seleccion():
    seleccion = combobox.get()
    return seleccion

# Frame para los botones
frame_botones = Frame(root)
frame_botones.pack(pady=10)

# Botón para insertar valores
btn_insertar = Button(frame_botones, text="Insertar valores", command=graficar)
btn_insertar.grid(row=0, column=0, padx=5)

# Iniciar el servidor Flask
iniciar_servidor_flask()

root.mainloop()
