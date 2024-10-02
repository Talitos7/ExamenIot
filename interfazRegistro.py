import tkinter as tk
from tkinter import messagebox
import mysql.connector
import interfazGrafica

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
                root.destroy()  # Cerrar la ventana de registro
                interfazGrafica.ventanaPrincipal(id_usuario)  # Abrir la ventana principal y pasar el id_usuario

            cursor.close()
            conexion.close()

        except mysql.connector.Error as error:
            messagebox.showerror("Error", f"No se pudo conectar a la base de datos: {error}")

def ventanaRegistro():
    global entry_nombre, entry_email, root
    # Interfaces con librería tkinter
    root = tk.Tk()
    root.title("Registro de Usuario")
    root.geometry("300x250")

    label_titulo = tk.Label(root, text="Formulario de Registro", font=("Arial", 14))
    label_titulo.pack(pady=10)

    label_nombre = tk.Label(root, text="Nombre:")
    label_nombre.pack(pady=5)
    entry_nombre = tk.Entry(root, width=30)
    entry_nombre.pack(pady=5)

    label_email = tk.Label(root, text="Correo Electrónico:")
    label_email.pack(pady=5)
    entry_email = tk.Entry(root, width=30)
    entry_email.pack(pady=5)

    button_registrar = tk.Button(root, text="Registrar", command=registrar_usuario)
    button_registrar.pack(pady=20)

    root.mainloop()
