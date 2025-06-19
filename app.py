import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.utils import secure_filename
import pandas as pd

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- Simple user system (for demo, not production) ---
USERS = {
    "admin": os.getenv("ADMIN_PASSWORD", "admin123"),
    "visitante": "visitante"  # Permite acceso inmediato con usuario y contraseña visitante
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if username in USERS and USERS[username] == password:
        session['user'] = username
        session['premium'] = True if username == "admin" else False
        return redirect(url_for('menu'))  # <--- AHORA VA AL MENÚ PRINCIPAL
    return render_template('login.html', error="Usuario o contraseña incorrectos.")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html', premium=session.get('premium', False))

@app.route('/procesar', methods=['POST'])
def procesar():
    if 'user' not in session:
        return jsonify({"success": False, "error": "No autorizado"}), 401

    if 'excel' not in request.files:
        return jsonify({"success": False, "error": "No se envió archivo"}), 400

    file = request.files['excel']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({"success": False, "error": "Archivo no permitido"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        df = pd.read_excel(filepath)
        # Espera columnas: nombre, telefono (opcional)
        results = []
        for _, row in df.iterrows():
            nombre = str(row.get('nombre', 'Cliente')).strip()
            telefono = str(row.get('telefono', '')).strip()
            copy = generar_copy(nombre, request.form.get('copy_type'), request.form.get('tone'))
            results.append({
                "nombre": nombre,
                "telefono": telefono if telefono else None,
                "copy": copy
            })
        os.remove(filepath)
        return jsonify({"success": True, "results": results, "premium": session.get('premium', False)})
    except Exception as e:
        return jsonify({"success": False, "error": f"Error al procesar archivo: {str(e)}"}), 500

def generar_copy(nombre, tipo, tono):
    # Ejemplo simple, puedes mejorar con IA o plantillas
    base = {
        "promocion": "¡Hola {nombre}! Aprovecha nuestra promo especial solo para ti: 2x1 en tu próxima visita.",
        "cumpleaños": "¡Feliz cumpleaños, {nombre}! Ven a celebrar con un postre gratis.",
        "bienvenida": "¡Bienvenido, {nombre}! Descubre el sabor único de nuestro restaurante con un 10% de descuento."
    }
    tono_dict = {
        "formal": "Estimado/a {nombre}, queremos invitarle a disfrutar de nuestras promociones exclusivas.",
        "divertido": "¡Hey {nombre}! ¿Listo para saborear algo increíble? 😋",
        "agresivo": "¡{nombre}, no dejes pasar esta oferta o te arrepentirás!"
    }
    plantilla = base.get(tipo, base["promocion"])
    mensaje = plantilla.format(nombre=nombre)
    if tono in tono_dict:
        mensaje = tono_dict[tono].replace("{nombre}", nombre) + " " + mensaje
    return mensaje

@app.route('/resultados')
def resultados():
    if 'user' not in session:
        return redirect(url_for('index'))
    # Aquí podrías mostrar resultados previos si los guardas
    return render_template('resultados.html')

@app.route('/menu', methods=['GET', 'POST'])
def menu():
    if 'user' not in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        # Aquí puedes guardar los datos del restaurante si quieres
        nombre = request.form.get('nombre_rest')
        direccion = request.form.get('direccion_rest')
        horario = request.form.get('horario_rest')
        whatsapp = request.form.get('whatsapp_rest')
        # Puedes guardar estos datos en una base de datos o variable de sesión
        # Por ahora solo los imprimimos
        print("Datos restaurante:", nombre, direccion, horario, whatsapp)
        return redirect(url_for('menu'))
    return render_template('menu.html')

@app.route('/registro_restaurante', methods=['GET', 'POST'])
def registro_restaurante():
    if 'user' not in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        nombre = request.form.get('nombre_rest')
        direccion = request.form.get('direccion_rest')
        horario = request.form.get('horario_rest')
        whatsapp = request.form.get('whatsapp_rest')
        # Aquí puedes guardar los datos
        print("Datos restaurante:", nombre, direccion, horario, whatsapp)
        return redirect(url_for('menu'))
    return render_template('registro_restaurante.html')

if __name__ == '__main__':
    app.run(debug=True)