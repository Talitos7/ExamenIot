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
        database="bd_series_trigonometricas"  # Cambia a tu base de datos correcta
    )
    return conexion

# Función para obtener los datos según el tipo de serie y el id_usuario
def obtener_datos_serie(tipo_serie, id_usuario):
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
        print(f"Error al obtener los datos: {str(e)}")
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

# Ruta principal que carga el dashboard
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para obtener los datos del gráfico según el tipo de serie
@app.route('/datos_grafico/<tipo_serie>/<id_usuario>', methods=['GET'])
def datos_grafico(tipo_serie, id_usuario):
    resultados = obtener_datos_serie(tipo_serie, id_usuario)

    if not resultados:
        return jsonify({"error": "No hay datos para mostrar"})

    # Listas para almacenar los datos
    n = list(range(1, len(resultados) + 1))  # ID ficticio para los datos
    valores_calculados = []
    valores_con_ruido = []
    errores = []

    for fila in resultados:
        valores_calculados.append(fila[0])
        valores_con_ruido.append(fila[1])
        errores.append(fila[2])

    # Calcular el porcentaje de error absoluto medio (MAPE)
    mape = calcular_mape(valores_calculados, valores_con_ruido)

    # Crear la gráfica usando Plotly
    trace1 = go.Scatter(x=n, y=valores_calculados, mode='lines+markers', name=f'Serie original ({tipo_serie})')
    trace2 = go.Scatter(x=n, y=valores_con_ruido, mode='lines+markers', name=f'Serie con ruido ({tipo_serie})')
    trace3 = go.Scatter(x=n, y=errores, mode='lines', name='Error', line=dict(color='red', dash='dash'))

    layout = go.Layout(
        title=f'Serie de {tipo_serie.capitalize()} - MAPE: {mape:.2f}%',
        xaxis_title='ID (n)',
        yaxis_title='Valores de la Serie',
        legend=dict(x=0, y=1),
        margin=dict(l=40, r=40, t=40, b=40)
    )

    fig = go.Figure(data=[trace1, trace2, trace3], layout=layout)

    # Convertir la gráfica a JSON
    graph_json = pio.to_json(fig)

    return jsonify(graph_json)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
