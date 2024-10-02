import tkinter as tk
from tkinter import ttk
import mysql.connector

# Conexión a la base de datos
def obtener_datos():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="bd_series_trigonometricas"
        )
        cursor = conexion.cursor()
        cursor.execute("SELECT id_registro, valor_calculado, valor_con_ruido, error, id_usuario, tipo_serie FROM registros")
        datos = cursor.fetchall()
        columnas = ['id_registro', 'valor_calculado', 'valor_con_ruido', 'error', 'id_usuario', 'tipo_serie']
        conexion.close()
        return columnas, datos
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None, None

# Crear la ventana principal del Dashboard
def ventana_dashboard():
    root = tk.Tk()
    root.title("Dashboard - Tabla de Datos")
    root.geometry("1000x600")

    # Frame para la tabla de registros
    frame_tabla = tk.Frame(root)
    frame_tabla.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Obtener los datos de la base de datos
    columnas, registros = obtener_datos()

    if columnas and registros:
        # Crear tabla con los datos de la base de datos
        tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=20)

        # Configurar las cabeceras de la tabla
        for col in columnas:
            tabla.heading(col, text=col)
            tabla.column(col, width=150, anchor='center')  # Ajustar el ancho de cada columna

        # Insertar los datos en la tabla
        for fila in registros:
            tabla.insert("", tk.END, values=fila)

        tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
        tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill="y")

    # Botón para cerrar
    btn_salir = tk.Button(root, text="Salir", command=root.destroy)
    btn_salir.pack(pady=10)

    root.mainloop()

# Ejecutar el dashboard
ventana_dashboard()
