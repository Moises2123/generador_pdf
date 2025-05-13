# app.py
from flask import Flask, request, send_file, render_template, abort, redirect, url_for, session
from generar_pdf import generar_documento
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta'  # Necesaria para usar session

# Lista de integrantes disponibles
INTEGRANTES_COMITE = [
    "Abg. Andrea del Pilar Chuquipiondo Sánchez",
    "Lic. Adm. Gilda Eloisa Hidalgo Chávez",
    "Lic. Adm. Rosa Elena Pérez de Mori",
    "Presidente. Reynaldo Elías Cajamarca Porras"
]

@app.route("/")
def index():
    return render_template("index.html", integrantes=INTEGRANTES_COMITE)

@app.route("/generar_documento", methods=["POST"])
def generar_documento_route():
    nombre_postulante = request.form.get("nombre_postulante")
    seleccionados = request.form.getlist("integrantes")

    if not nombre_postulante or len(seleccionados) != 3:
        abort(400, "Debes completar todos los campos y seleccionar tres integrantes del comité.")

    try:
        archivo_pdf = generar_documento(nombre_postulante, seleccionados)
        session['pdf_path'] = archivo_pdf
        return redirect(url_for('descargar_pdf'))  # <--- Redirige directamente al PDF
    except Exception as e:
        return f"Error al generar el PDF: {str(e)}", 500
@app.route("/descargar_pdf")
def descargar_pdf():
    pdf_path = session.get('pdf_path')
    if not pdf_path or not os.path.exists(pdf_path):
        abort(404, "PDF no encontrado")
    return send_file(pdf_path, mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
