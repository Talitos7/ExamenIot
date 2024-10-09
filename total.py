import tkinter as tk
from tkinter import messagebox
import mysql.connector
import math
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk
import math
import random

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

def registrar_usuario():
    nombre = entry_nombre.get()
    email = entry_email.get()
    
    if nombre == "" or email == "":
        messagebox.showerror("Error", "Por favor, complete todos los campos.")
    else:
        try:
            # Conexión con la base de datos
            conexion = mysql.connector.connect(
                host="localhost",       
                user="root",           
                password="", 
                database="bd_series_trigonometricas"
            )
            cursor = conexion.cursor()

            # Verificar si el correo ya está registrado
            consulta_verificar = "SELECT id_usuario FROM usuario WHERE correo = %s"
            cursor.execute(consulta_verificar, (email,))
            resultado = cursor.fetchone()

            if resultado:
                messagebox.showerror("Error", "Este correo ya está registrado. Intenta con otro correo.")
            else:
                # Insertar el nuevo usuario
                consulta = "INSERT INTO usuario (nombre, correo) VALUES (%s, %s)"
                cursor.execute(consulta, (nombre, email))
                conexion.commit()

                # Obtener el id del usuario recién registrado
                cursor.execute("SELECT id_usuario FROM usuario WHERE correo = %s", (email,))
                id_usuario = cursor.fetchone()[0]
                
                messagebox.showinfo("Registro exitoso", f"Usuario {nombre} registrado correctamente.")
                
                root.withdraw() # Cerrar la ventana de registro
                ventanaPrincipal(id_usuario)  # Abrir la ventana principal y pasar el id_usuario

            cursor.close()
            conexion.close()

        except mysql.connector.Error as error:
            messagebox.showerror("Error", f"No se pudo conectar a la base de datos: {error}")
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
        original_vals, ruido_vals, error_vals = leer_desde_bd(id_usuario, tipo_serie)
    elif tipo_serie == "seno":
        original_vals, ruido_vals, error_vals = leer_desde_bd(id_usuario, tipo_serie)
    elif tipo_serie == "fourier":
        original_vals, ruido_vals, error_vals = leer_desde_bd(id_usuario, tipo_serie)

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
    seleccion = combobox.get()  # Obtener el valor seleccionado en el combobox
    nmax = int(entry_terminos.get())
    num_puntos = int(entry_registros.get())
    
    if seleccion == "coseno":
        original_vals, ruido_vals, error_vals = generar_valores_funcion_coseno_con_ruido(num_puntos, nmax)
        guardar_registros_bd(original_vals, ruido_vals, error_vals, id_usuario, tipo_serie="coseno")
    elif seleccion == "seno":
        x_vals, original_vals, ruido_vals, error_vals = generar_valores_funcion_seno_con_ruido(num_puntos, nmax)
        guardar_registros_bd(original_vals, ruido_vals, error_vals, id_usuario, tipo_serie="seno")
    elif seleccion == "fourier":
        x_vals, original_vals, ruido_vals, error_vals = generar_valores_funcion_fourier_con_ruido(num_puntos, nmax)
        guardar_registros_bd(original_vals, ruido_vals, error_vals, id_usuario, tipo_serie="fourier")

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
    
    return original_vals, ruido_vals, error_vals
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
# Función para guardar los registros en la base de datos

def guardar_registros_bd(original_vals, ruido_vals, error_vals, id_usuario, tipo_serie):
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
def leer_desde_bd(id_usuario, tipo_serie):
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


def ventanaRegistro():
    global entry_nombre, entry_email, root
    root.withdraw()  # Ocultar la ventana de inicio de sesión

    # Crear nueva ventana para el registro
    ventana_registro = tk.Toplevel(root)
    ventana_registro.title("Registro de Usuario")
    ventana_registro.geometry("500x350")
    ventana_registro.configure(bg="#f2e9e4")  # Color de fondo
    
    label_titulo = tk.Label(ventana_registro, text="Formulario de Registro", font=("Arial", 16, "bold"), bg="#f2e9e4")
    label_titulo.pack(pady=10)

    label_nombre = tk.Label(ventana_registro, text="Nombre:", bg="#f2e9e4",font=("Arial", 10, "bold"))
    label_nombre.pack(pady=5)
    entry_nombre = tk.Entry(ventana_registro, width=30, bg="#FFFFFF", bd=2, relief="groove")
    entry_nombre.pack(pady=5)

    label_email = tk.Label(ventana_registro, text="Correo Electrónico:", bg="#f2e9e4",font=("Arial", 10, "bold"))
    label_email.pack(pady=5)
    entry_email = tk.Entry(ventana_registro, width=30, bg="#FFFFFF", bd=2, relief="groove")
    entry_email.pack(pady=5)

    button_registrar = tk.Button(ventana_registro, text="Registrar", command=registrar_usuario, 
                                  bg="#6a994e", fg="white", font=("Arial", 12), relief="raised")
    button_registrar.pack(pady=20)


def ventanaPrincipal(id_usuario):
    ventana = tk.Toplevel(root)
    ventana.title("SERIE TRIGONOMÉTRICA")
    ventana.geometry("800x600")
    ventana.configure(bg="#f2e9e4")  # Color de fondo

    frame_inputs = tk.Frame(ventana, bg="#f2e9e4")
    frame_inputs.pack(pady=10)

    tk.Label(frame_inputs, text="Número de términos:", bg="#f2e9e4",font=("Arial", 10, "bold")).grid(row=1, column=0, padx=5, pady=5)
    entry_terminos = tk.Entry(frame_inputs, bg="#FFFFFF", bd=2, relief="groove")
    entry_terminos.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(frame_inputs, text="Cantidad de registros:", bg="#f2e9e4",font=("Arial", 10, "bold")).grid(row=2, column=0, padx=5, pady=5)
    entry_registros = tk.Entry(frame_inputs, bg="#FFFFFF", bd=2, relief="groove")
    entry_registros.grid(row=2, column=1, padx=5, pady=5)

    frame_combobox = tk.Frame(ventana, bg="#F1F1F1")
    frame_combobox.pack(pady=10)

    tk.Label(frame_combobox, text="Selecciona la serie trigonométrica:", bg="#F1F1F1",font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5)

    series_options = ["seno", "coseno", "fourier"]
    combobox = ttk.Combobox(frame_combobox, values=series_options)
    combobox.grid(row=0, column=1, padx=5, pady=5)
    combobox.current(0)

    frame_botones = tk.Frame(ventana, bg="#F1F1F1")
    frame_botones.pack(pady=10)

    frame_grafica = tk.Frame(ventana)
    frame_grafica.pack(pady=20, fill=tk.BOTH, expand=True)

    btn_insertar = tk.Button(frame_botones, text="Insertar valores", 
                             command=lambda: insertar_valores(entry_terminos, entry_registros, combobox, id_usuario),
                             bg="#00afb9", fg="white", relief="raised")
    btn_insertar.grid(row=0, column=0, padx=5)

    btn_graficar = tk.Button(frame_botones, text="Graficar", 
                             command=lambda: graficar_serie(id_usuario, combobox.get(), frame_grafica),
                             bg="#f4a261", fg="white", relief="raised")
    btn_graficar.grid(row=0, column=1, padx=5)


# Ventana de inicio de sesión
def ventanaInicioSesion():
    global root
    root = tk.Tk()
    root.title("Inicio de Sesión")
    root.geometry("500x350")
    root.configure(bg="#f2e9e4")  # Color de fondo

    tk.Label(root, text="Inicio de Sesión", font=("Arial", 16, "bold"), bg="#f2e9e4").pack(pady=10)

    tk.Label(root, text="Nombre:", bg="#f2e9e4",font=("Arial", 10, "bold")).pack(pady=5)
    global entry_nombre
    entry_nombre = tk.Entry(root, width=30, bg="#FFFFFF", bd=2, relief="groove")
    entry_nombre.pack(pady=5)

    tk.Label(root, text="Correo Electrónico:", bg="#f2e9e4",font=("Arial", 10, "bold")).pack(pady=5)
    global entry_email
    entry_email = tk.Entry(root, width=30, bg="#FFFFFF", bd=2, relief="groove")
    entry_email.pack(pady=5)

    tk.Button(root, text="Iniciar Sesión", command=verificar, 
              bg="#00afb9", fg="white", font=("Arial", 12), relief="raised").pack(pady=10)
    tk.Button(root, text="Registrar Nuevo Usuario", command=ventanaRegistro, 
              bg="#0081a7", fg="white", font=("Arial", 12), relief="raised").pack(pady=30)
    
    root.mainloop()
ventanaInicioSesion()






