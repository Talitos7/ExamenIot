import tkinter as tk
from tkinter import messagebox
import mysql.connector
import interfazRegistro

global id_usuario
id_usuario = None
global root
  
def verificar():
    global id_usuario 
    global root
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

            consulta = "SELECT id_usuario FROM usuario WHERE nombre = %s AND correo = %s"
            cursor.execute(consulta, (nombre, email))
            resultado = cursor.fetchone()

            if resultado:
                id_usuario = resultado[0]  
                messagebox.showinfo("Inicio de sesión", f"Bienvenido/a {nombre}. Tu ID es: {id_usuario}")
                root.destroy()  # Cerrar la ventana principal
                
                import interfazGrafica
                interfazGrafica.ventanaPrincipal(id_usuario)  # Llamada a la siguiente ventana
            else:
                messagebox.showerror("Error", "Usuario no encontrado. Verifique los datos.")
            
            cursor.close()
            conexion.close()

        except mysql.connector.Error as error:
            messagebox.showerror("Error", f"No se pudo conectar a la base de datos: {error}")

def abrir_registro():
    global root
    root.destroy()  # Cerrar la ventana actual
    interfazRegistro.ventanaRegistro()  # Abrir la ventana de registro

def ventanaInicioSesion():
    global root
    # Interfaces con la librería tkinter
    root = tk.Tk()
    root.title("Inicio de Sesión")
    root.geometry("300x250")

    # Label para título
    label_titulo = tk.Label(root, text="Inicio de Sesión", font=("Arial", 14))
    label_titulo.pack(pady=10)

    # Campo de nombre
    label_nombre = tk.Label(root, text="Nombre:")
    label_nombre.pack(pady=5)
    global entry_nombre  # Necesitamos que sea accesible en otras funciones
    entry_nombre = tk.Entry(root, width=30)
    entry_nombre.pack(pady=5)

    # Campo de correo electrónico
    label_email = tk.Label(root, text="Correo Electrónico:")
    label_email.pack(pady=5)
    global entry_email  # Necesitamos que sea accesible en otras funciones
    entry_email = tk.Entry(root, width=30)
    entry_email.pack(pady=5)

    # Botón para iniciar sesión
    button_login = tk.Button(root, text="Iniciar Sesión", command=verificar)
    button_login.pack(pady=10)
    
    # Botón para registrarse
    button_register = tk.Button(root, text="Registrarse", command=abrir_registro)
    button_register.pack(pady=10)

    root.mainloop()

# Para iniciar la aplicación
ventanaInicioSesion()