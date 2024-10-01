import mysql.connector
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from interfazLogin import id_usuario

# Función para conectar a la base de datos
def conectar():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",  # Cambia por tu usuario
        password="",  # Cambia por tu contraseña
        database="bd_series_trigonometricas"
    )
    return conexion

# Función para limpiar el canvas actual (si existe un gráfico previo)
def limpiar_canvas():
    for widget in frame_canvas.winfo_children():
        widget.destroy()

# Función para obtener datos filtrados por serie y usuario
def obtener_datos_serie(tipo_serie):
    try:
        conexion = conectar()
        cursor = conexion.cursor()

        # Consulta SQL para obtener los datos según tipo de serie y id_usuario
        sql = """
        SELECT valor_calculado, valor_con_ruido, error 
        FROM registros 
        WHERE tipo_serie = %s AND id_usuario = %s
        """
        cursor.execute(sql, (tipo_serie, id_usuario))
        resultados = cursor.fetchall()

        cursor.close()
        conexion.close()

        return resultados

    except Exception as e:
        messagebox.showerror("Error", str(e))
        return None
    
# Función para calcular el porcentaje de error absoluto medio (MAPE)
def calcular_mape(valores_calculados, valores_con_ruido):
    total_error = 0
    n = len(valores_calculados)
    
    for calculado, ruido in zip(valores_calculados, valores_con_ruido):
        if calculado != 0:  # Evitar división por cero
            total_error += abs((calculado - ruido) / calculado) * 100
    
    mape = total_error / n
    return mape

# Función para graficar la serie seleccionada con el cálculo del % de error
def graficar_datos_serie():
    try:
        # Limpiar el canvas antes de dibujar el nuevo gráfico
       if frame_canvas.winfo_children():
        limpiar_canvas()


        tipo_serie = combobox_serie.get()

        if not tipo_serie:
            messagebox.showwarning("Advertencia", "Por favor selecciona una serie.")
            return

        # Obtener datos desde la base de datos
        resultados = obtener_datos_serie(tipo_serie)

        if not resultados:
            messagebox.showinfo("Sin Datos", "No hay datos para graficar.")
            return

        # Listas para almacenar los datos
        n = list(range(1, len(resultados) + 1))  # ID ficticio para los datos
        valores_calculados = []
        valores_con_ruido = []
        errores = []

        # Procesar los resultados
        for fila in resultados:
            valores_calculados.append(fila[0])   # Valor calculado
            valores_con_ruido.append(fila[1])    # Valor con ruido
            errores.append(fila[2])              # Error

        # Calcular el porcentaje de error absoluto medio (MAPE)
        mape = calcular_mape(valores_calculados, valores_con_ruido)

        # Crear figura de matplotlib
        fig, ax = plt.subplots(figsize=(8, 6))

        # Graficar valores calculados y con ruido
        ax.plot(n, valores_calculados, label=f"Serie ({tipo_serie})", marker='o')
        ax.plot(n, valores_con_ruido, label=f"Con ruido ({tipo_serie})", marker='x')

        # Graficar error
        ax.plot(n, errores, label="Error", linestyle='--', color='red')

        # Personalización del gráfico
        ax.set_title(f"SERIE DE {tipo_serie.upper()} - MAPE: {mape:.2f}%")
        ax.set_xlabel("ID (n)")
        ax.set_ylabel("Valores de La Serie")
        ax.legend()
        ax.grid(True)

        # Mostrar el gráfico en la interfaz
        canvas = FigureCanvasTkAgg(fig, master=frame_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack()

    except Exception as e:
        messagebox.showerror("Error", str(e))



                             

# Crear la ventana principal con Tkinter
root = Tk()
root.title("Dashboard Series")
root.geometry("800x600")

# Frame para selección de serie
frame_serie = Frame(root)
frame_serie.pack(pady=10)

# Etiqueta y combobox para seleccionar el tipo de serie
Label(frame_serie, text="Selecciona la serie").grid(row=0, column=0, padx=5, pady=5)
combobox_serie = StringVar()
series_options = ["coseno", "seno", "fourier"]
combobox = OptionMenu(frame_serie, combobox_serie, *series_options)
combobox.grid(row=0, column=1, padx=5, pady=5)

# Frame para los botones
frame_botones = Frame(root)
frame_botones.pack(pady=10)

# Botón para graficar datos
btn_graficar = Button(frame_botones, text="Graficar Serie", command=graficar_datos_serie)
btn_graficar.grid(row=0, column=0, padx=5)

# Frame para gráficos
frame_canvas = Frame(root)
frame_canvas.pack(pady=20)

# Ejecutar la aplicación
root.mainloop()
