from flask import Flask, jsonify, render_template, request
import matplotlib.pyplot as plt
import numpy as np
import os
import sqlite3
import json

app = Flask(__name__)

# Configura la conexión a la base de datos SQLite
DATABASE = 'tu_base_de_datos.db'  # Cambia esto al nombre de tu base de datos

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Ruta para renderizar la página principal (si es necesario)
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para generar y guardar el gráfico
@app.route('/graficar_datos', methods=['POST'])
def graficar_datos():
    data = request.json
    original_vals = data.get('original_vals')
    ruido_vals = data.get('ruido_vals')
    tipo_serie = data.get('tipo_serie')

    plt.figure()
    plt.plot(original_vals, label='Valores Originales')
    plt.plot(ruido_vals, label='Valores con Ruido')
    plt.title(f'Gráfico de {tipo_serie}')
    plt.xlabel('Índice')
    plt.ylabel('Valor')
    plt.legend()
    
    # Guarda la figura en un archivo
    grafico_path = f'static/graficos/{tipo_serie}.png'
    plt.savefig(grafico_path)
    plt.close()

    return jsonify({'success': True, 'grafico_path': grafico_path})

# Ruta para obtener los datos del gráfico
@app.route('/datos_grafico/<tipo_serie>/<int:id_usuario>', methods=['GET'])
def datos_grafico(tipo_serie, id_usuario):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Consulta a la base de datos para obtener los datos del gráfico
    cursor.execute("SELECT * FROM tu_tabla WHERE tipo_serie = ? AND id_usuario = ?", (tipo_serie, id_usuario))
    datos = cursor.fetchall()
    conn.close()

    # Formato de los datos a retornar
    datos_response = []
    for row in datos:
        datos_response.append(dict(row))

    return jsonify(datos_response)

if __name__ == '__main__':
    # Asegúrate de que el directorio está creado para guardar gráficos
    os.makedirs('static/graficos', exist_ok=True)
    app.run(debug=True)
