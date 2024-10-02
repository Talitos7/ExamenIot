from flask import Flask, jsonify, render_template, request
import os
import sqlite3
import matplotlib.pyplot as plt

app = Flask(__name__)
DATABASE = 'tu_base_de_datos.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/graficar_datos', methods=['POST'])
def graficar_datos():
    data = request.json
    original_vals = data['original_vals']
    ruido_vals = data['ruido_vals']
    tipo_serie = data['tipo_serie']
    url_dashboard = data.get('url_dashboard')  # Obtener el URL del dashboard si se proporciona

    plt.figure()
    plt.plot(original_vals, label='Valores Originales')
    plt.plot(ruido_vals, label='Valores con Ruido')
    plt.title(f'Gráfico de {tipo_serie}')
    plt.xlabel('Índice')
    plt.ylabel('Valor')
    plt.legend()

    grafico_path = f'static/graficos/{tipo_serie}.png'
    plt.savefig(grafico_path)
    plt.close()

    # Opcional: Puedes hacer algo con el URL del dashboard aquí
    print(f'URL del Dashboard: {url_dashboard}')  # Ejemplo de uso: imprimir en la consola

    return jsonify({'success': True, 'grafico_path': grafico_path})

if __name__ == '__main__':
    os.makedirs('static/graficos', exist_ok=True)
    app.run(debug=True, port=5000)
