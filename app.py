from flask import Flask, render_template, request, jsonify
import pymysql

app = Flask(__name__)

# Configurar la conexión a la base de datos
connection = pymysql.connect(
    host='localhost',
    user='casa',
    password='contraseña',
    database='guests_db'
)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/guest_info', methods=['POST'])
def get_guest_info():
    try:
        with connection.cursor() as cursor:
            # Obtener las dos últimas filas de la tabla guest_info
            sql = "SELECT * FROM guest_info ORDER BY id DESC LIMIT 2"
            cursor.execute(sql)
            result = cursor.fetchall()

            print(result)

        # Devolver los datos de los huéspedes en formato JSON
        response = jsonify(result)
        # Agregar cabeceras para evitar el almacenamiento en caché
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'

        return response

    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run()
