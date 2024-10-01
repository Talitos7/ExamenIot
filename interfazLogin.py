import tkinter as tk
from tkinter import messagebox
import mysql.connector

global id_usuario
id_usuario = None

def verificar():
    global id_usuario 
    nombre = entry_nombre.get()
    email = entry_email.get()
    
    if nombre == "" or email == "":
        messagebox.showerror("Error", "Por favor, complete todos los campos.")
    else:
        try:
            conexion = mysql.connector.connect(
                host="localhost",       
                user="root",           
                password="...", 
                database="..." 
            )
            cursor = conexion.cursor()

            consulta = "SELECT id_usuario FROM usuario WHERE nombre = %s AND correo = %s"
            cursor.execute(consulta, (nombre, email))
            resultado = cursor.fetchone()

            if resultado:
                id_usuario = resultado[0]  
                messagebox.showinfo("Inicio de sesión", f"Bienvenido/a {nombre}. Tu ID es: {id_usuario}")
            else:
                messagebox.showerror("Error", "Usuario no encontrado. Verifique los datos.")
            
            cursor.close()
            conexion.close()

        except mysql.connector.Error as error:
            messagebox.showerror("Error", f"No se pudo conectar a la base de datos: {error}")

root = tk.Tk()
root.title("Inicio de Sesión")
root.geometry("300x200")

label_nombre = tk.Label(root, text="Nombre:")
label_nombre.pack(pady=10)
entry_nombre = tk.Entry(root, width=30)
entry_nombre.pack(pady=5)

label_email = tk.Label(root, text="Correo Electrónico:")
label_email.pack(pady=10)
entry_email = tk.Entry(root, width=30)
entry_email.pack(pady=5)

button_login = tk.Button(root, text="Iniciar Sesión", command=verificar)
button_login.pack(pady=20)

root.mainloop()

