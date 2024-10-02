from flask import Flask, render_template, jsonify
import mysql.connector
import plotly.graph_objs as go
import plotly.io as pio
from datetime import datetime

# Inicializar la aplicación Flask
app = Flask(__name__)

# Función para conectar a la base de datos
def conectar():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",  # Cambia por tu usuario
        password="",  # Cambia por tu contraseña
        database="bd_series_trigonometricas"
    )
    return conexion

# Función para obtener los datos más recientes de la tabla registros
def obtener_datos(tipo_serie, id_usuario):
    conexion = conectar()
    cursor = conexion.cursor()

    # Consulta SQL para obtener los datos
    sql = "SELECT * FROM registros WHERE id_usuario = %s AND tipo_serie = %s ORDER BY id_registro"
    cursor.execute(sql, (id_usuario, tipo_serie))
    resultados = cursor.fetchall()

    # Listas para almacenar los datos
    original_vals = []
    ruido_vals = []
    error_vals = []

    for fila in resultados:
        original_vals.append(fila[1])
        ruido_vals.append(fila[2])
        error_vals.append(fila[3])

    cursor.close()
    conexion.close()

    return original_vals, ruido_vals, error_vals

# Ruta principal que carga el dashboard
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para actualizar los datos del gráfico
@app.route('/datos_grafico/<tipo_serie>/<int:id_usuario>', methods=['GET'])
def datos_grafico(tipo_serie, id_usuario):
    original_vals, ruido_vals, error_vals = obtener_datos(tipo_serie, id_usuario)

    # Crear la gráfica usando Plotly
    trace1 = go.Scatter(x=list(range(len(original_vals))), y=original_vals, mode='lines+markers', name='Original')
    trace2 = go.Scatter(x=list(range(len(ruido_vals))), y=ruido_vals, mode='lines+markers', name='Con Ruido')
    trace3 = go.Scatter(x=list(range(len(error_vals))), y=error_vals, mode='lines', name='Error', line=dict(color='red', dash='dash'))

    layout = go.Layout(
        title=f'Gráfico en tiempo real - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        xaxis_title='ID Registro',
        yaxis_title='Valores de la serie',
        legend=dict(x=0, y=1),
        margin=dict(l=40, r=40, t=40, b=40)
    )

    fig = go.Figure(data=[trace1, trace2, trace3], layout=layout)

    # Convertir la gráfica a JSON
    graph_json = pio.to_json(fig)

    return jsonify(graph_json)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)