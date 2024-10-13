import tkinter as tk
from tkinter import messagebox
import mysql.connector
import numpy as np
import math
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk
import plotly.graph_objs as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import threading

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
        
#Funcion para borrar datos
def borrar_datos(combobox, id_usuario):
    try:
        tipo_serie = combobox.get()
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


# Función para obtener datos en tiempo real del usuario y tipo de serie
def obtener_datos(id_usuario, tipo_serie):
    try:
        conexion = conectar()
        cursor = conexion.cursor()

        consulta = "SELECT valor_calculado, valor_con_ruido FROM registros WHERE id_usuario = %s AND tipo_serie = %s"
        cursor.execute(consulta, (id_usuario, tipo_serie))

        datos = np.array(cursor.fetchall())

        cursor.close()
        conexion.close()

        return datos

    except mysql.connector.Error as error:
        print(f"Error al conectar con la base de datos: {error}")
        return np.array([])

# Función para iniciar la aplicación Dash en un hilo
def run_dash(id_usuario, tipo_serie):
    app = dash.Dash(__name__)

    app.layout = html.Div([
        html.H1("Gráficas en Tiempo Real"),
        dcc.Dropdown(
            id='tipo-serie-dropdown',
            options=[
                {'label': 'Seno', 'value': 'seno'},
                {'label': 'Coseno', 'value': 'coseno'},
                {'label': 'Fourier', 'value': 'fourier'},
            ],
            value='seno'  # Valor por defecto
        ),
        dcc.Graph(id='live-graph'),
        dcc.Interval(id='interval-component', interval=1000, n_intervals=0)  # Actualiza cada segundo
    ])

    @app.callback(
        Output('live-graph', 'figure'),
        Input('interval-component', 'n_intervals'),
        Input('tipo-serie-dropdown', 'value')
    )
    def update_graph(n, tipo_serie):
        datos = obtener_datos(id_usuario, tipo_serie)

        if datos.size == 0:
            return {'data': [], 'layout': go.Layout(title='No hay datos para el usuario')}

        x = np.arange(len(datos))  # Generar el eje x
        y = datos[:, 1]  # Valor con ruido

        return {
            'data': [go.Scatter(x=x, y=y, mode='lines', name='Datos')],
            'layout': go.Layout(title=f'Gráfico para el usuario: {id_usuario}, Serie: {tipo_serie.capitalize()}', xaxis=dict(title='Registro'), yaxis=dict(title='Valor'))
        }

    app.run_server(debug=False, use_reloader=False)


# Función para mostrar la ventana del Dashboard y cerrar la ventana principal
def abrir_ventana_dashboard(ventana):
    ventana.destroy()  # Cerrar la ventana principal
    ventanaDashboard()

# Función para volver a la ventana principal desde la ventana Dashboard
def volver_a_ventana_principal(ventana_dashboard):
    ventana_dashboard.destroy()  # Cerrar la ventana del Dashboard
    ventanaPrincipal(id_usuario)
    
    
# Crear la ventana Dashboard
def ventanaDashboard():
    ventana_dashboard = tk.Tk()
    ventana_dashboard.title("Dashboard de Series Trigonométricas")
    ventana_dashboard.geometry("1000x600")

    # Función para cargar todos los datos en la tabla
    def cargar_todos_los_datos():
        conexion = conectar()
        cursor = conexion.cursor()

        # Obtener todos los registros
        consulta = """
            SELECT r.id_registro, u.nombre, r.tipo_serie, r.valor_calculado, r.valor_con_ruido, r.error
            FROM registros r
            JOIN usuario u ON r.id_usuario = u.id_usuario
        """
        cursor.execute(consulta)
        filas = cursor.fetchall()

        cursor.close()
        conexion.close()

        # Limpiar tabla antes de insertar nuevos datos
        for item in tree.get_children():
            tree.delete(item)

        # Insertar datos en la tabla
        for fila in filas:
            tree.insert("", "end", values=fila)

    # Botón para volver a la ventana principal
    boton_volver = tk.Button(ventana_dashboard, text="Volver a Ventana Principal", command=lambda: volver_a_ventana_principal(ventana_dashboard), 
                                  bg="#253342", fg="white", font=("Arial", 12), relief="raised")
    boton_volver.pack(side=tk.TOP, padx=10, pady=10)

    # Frame para los Combobox y filtros
    frame_filtros = tk.Frame(ventana_dashboard)
    frame_filtros.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

    # Label y Combobox para filtro por usuario
    label_usuario = tk.Label(frame_filtros, text="Filtrar por Usuario:")
    label_usuario.pack(side=tk.LEFT, padx=10, pady=10)
    combobox_usuario = ttk.Combobox(frame_filtros, state="readonly")
    combobox_usuario.pack(side=tk.LEFT, padx=10, pady=10)

    # Label y Combobox para filtro por serie
    label_serie = tk.Label(frame_filtros, text="Filtrar por Serie:")
    label_serie.pack(side=tk.LEFT, padx=10, pady=10)
    combobox_serie = ttk.Combobox(frame_filtros, state="readonly", values=["", "coseno", "seno", "fourier"])
    combobox_serie.pack(side=tk.LEFT, padx=10, pady=10)

    # Botón para aplicar los filtros
    boton_aplicar_filtro = tk.Button(frame_filtros, text="Aplicar Filtro", command=lambda: aplicar_filtro(combobox_usuario.get(), combobox_serie.get()), 
                                  bg="#23bac4", fg="white", font=("Arial", 12), relief="raised")
    boton_aplicar_filtro.pack(side=tk.LEFT, padx=10, pady=10)

    # Botón para limpiar los filtros
    boton_limpiar_filtro = tk.Button(frame_filtros, text="Limpiar Filtros", command=cargar_todos_los_datos, 
                                  bg="#e36b2c", fg="white", font=("Arial", 12), relief="raised")
    boton_limpiar_filtro.pack(side=tk.LEFT, padx=10, pady=10)

    # Frame para la tabla
    frame_tabla = tk.Frame(ventana_dashboard)
    frame_tabla.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Treeview para mostrar los datos en tabla
    tree = ttk.Treeview(frame_tabla, columns=("ID", "Usuario", "Serie", "Valor Calculado", "Valor Con Ruido", "Error"), show='headings')
    tree.pack(fill=tk.BOTH, expand=True)

    # Definir las columnas
    tree.heading("ID", text="ID Registro")
    tree.heading("Usuario", text="Usuario")
    tree.heading("Serie", text="Serie")
    tree.heading("Valor Calculado", text="Valor Calculado")
    tree.heading("Valor Con Ruido", text="Valor Con Ruido")
    tree.heading("Error", text="Error")

    # Función para aplicar el filtro seleccionado
    def aplicar_filtro(usuario, serie):
        conexion = conectar()
        cursor = conexion.cursor()

        # Consulta con filtros dinámicos
        consulta = """
            SELECT r.id_registro, u.nombre, r.tipo_serie, r.valor_calculado, r.valor_con_ruido, r.error
            FROM registros r
            JOIN usuario u ON r.id_usuario = u.id_usuario
            WHERE (%s = '' OR u.nombre = %s) 
            AND (%s = '' OR r.tipo_serie = %s)
        """
        cursor.execute(consulta, (usuario, usuario, serie, serie))
        filas = cursor.fetchall()

        cursor.close()
        conexion.close()

        # Limpiar tabla antes de insertar nuevos datos
        for item in tree.get_children():
            tree.delete(item)

        # Insertar datos filtrados en la tabla
        for fila in filas:
            tree.insert("", "end", values=fila)

    # Cargar datos al iniciar
    cargar_todos_los_datos()

    # Frame para el gráfico
    frame_grafico = tk.Frame(ventana_dashboard)
    frame_grafico.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    # Función para cargar y mostrar los datos en el gráfico automáticamente
    def mostrar_grafico_auto():
        conexion = conectar()
        cursor = conexion.cursor()

        # Consulta para obtener la cantidad de registros por usuario y serie
        consulta = """
            SELECT u.nombre, r.tipo_serie, COUNT(*) 
            FROM registros r
            JOIN usuario u ON r.id_usuario = u.id_usuario
            GROUP BY u.nombre, r.tipo_serie
        """
        cursor.execute(consulta)
        datos = cursor.fetchall()

        cursor.close()
        conexion.close()

        # Procesar los datos para gráfico apilado
        usuarios = list(set([dato[0] for dato in datos]))  # Usuarios únicos
        series = ["coseno", "seno", "fourier"]  # Series únicas
        conteos = {usuario: {serie: 0 for serie in series} for usuario in usuarios}

        for usuario, serie, conteo in datos:
            conteos[usuario][serie] = conteo

        # Crear el gráfico apilado
        fig, ax = plt.subplots()

        bottom = np.zeros(len(usuarios))
        for serie in series:
            serie_vals = [conteos[usuario][serie] for usuario in usuarios]
            ax.bar(usuarios, serie_vals, label=serie, bottom=bottom)
            bottom += np.array(serie_vals)

        ax.set_xlabel("Usuarios")
        ax.set_ylabel("Cantidad de Registros")
        ax.set_title("Cantidad de Registros por Usuario y Serie")
        ax.legend()

        # Limpiar el Frame de gráficos antes de agregar uno nuevo
        for widget in frame_grafico.winfo_children():
            widget.destroy()

        # Mostrar el gráfico en el Frame
        canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Llamar a la función para mostrar el gráfico automáticamente al cargar la ventana
    mostrar_grafico_auto()

    # Cargar todos los usuarios en el ComboBox
    def cargar_usuarios():
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT nombre FROM usuario")
        usuarios = cursor.fetchall()
        combobox_usuario["values"] = [usuario[0] for usuario in usuarios]
        cursor.close()
        conexion.close()

    cargar_usuarios()

    ventana_dashboard.mainloop()


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
    global ventana
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
    
    btn_eliminar = tk.Button(frame_botones, text="Borrar datos antiguos", 
                             command=lambda: borrar_datos(combobox, id_usuario),
                             bg="#c51d34", fg="white", relief="raised")
    btn_eliminar.grid(row=0, column=2, padx=5)
    
    btn_tiemReal = tk.Button(frame_botones, text="Grafica en tiempo real", 
                             command=lambda: threading.Thread(target=run_dash, args=(id_usuario, "seno")).start(),
                             bg="#bba9bb", fg="white", relief="raised")
    btn_tiemReal.grid(row=0, column=3, padx=5)
    
    btn_dashboard = tk.Button(frame_botones, text="Dashboard", 
                             command=lambda: abrir_ventana_dashboard(ventana),
                             bg="#6dc36d", fg="white", relief="raised")
    btn_dashboard.grid(row=0, column=4, padx=5)


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