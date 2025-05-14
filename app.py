from flask import Flask, request, send_file, render_template, abort, redirect, url_for, session, make_response
from generar_pdf import generar_documento
import os
import io

app = Flask(__name__)
app.secret_key = 'clave_secreta'  # Necesaria para usar session

# Lista de integrantes disponibles (predefinidos)
INTEGRANTES_COMITE = [
    "Abg. Andrea del Pilar Chuquipiondo Sánchez",
    "Lic. Adm. Gilda Eloisa Hidalgo Chávez",
    "Lic. Adm. Rosa Elena Pérez de Mori",
    "Presidente. Reynaldo Elías Cajamarca Porras"
]

@app.route("/")
def index():
    # Verificar si hay integrantes personalizados en la sesión
    integrantes = session.get('integrantes_personalizados', INTEGRANTES_COMITE)
    return render_template("index.html", integrantes=integrantes)

@app.route("/agregar_integrante", methods=["POST"])
def agregar_integrante():
    nuevo_integrante = request.form.get("nuevo_integrante")

    if not nuevo_integrante:
        return "El nombre del integrante no puede estar vacío", 400

    # Obtener la lista actual de integrantes (de sesión o predeterminada)
    integrantes = session.get('integrantes_personalizados', INTEGRANTES_COMITE.copy())

    # Verificar si ya existe
    if nuevo_integrante not in integrantes:
        integrantes.append(nuevo_integrante)
        session['integrantes_personalizados'] = integrantes

    return redirect(url_for('index'))

@app.route("/eliminar_integrante", methods=["POST"])
def eliminar_integrante():
    integrante = request.form.get("integrante")

    if not integrante:
        return "Debes especificar el integrante a eliminar", 400

    # Obtener la lista actual y eliminar el integrante
    integrantes = session.get('integrantes_personalizados', INTEGRANTES_COMITE.copy())

    if integrante in integrantes:
        integrantes.remove(integrante)
        session['integrantes_personalizados'] = integrantes

    return redirect(url_for('index'))

@app.route("/generar_documento", methods=["POST"])
def generar_documento_route():
    nombre_postulante = request.form.get("nombre_postulante")
    seleccionados = request.form.getlist("integrantes")
    
    # Nuevo parámetro de título completo
    titulo_proceso = request.form.get("titulo_proceso", "PROCESO SELECCIÓN PERSONAL SUPLENCIA N° 002-2025-LORETO BAJO LOS ALCANCES DEL DECRETO LEGISLATIVO N° 728 DETERMINADO BAJO LA MODALIDAD DE SUPLENCIA")
    dependencia = request.form.get("dependencia", "Módulo Penal Central")
    
    # Recopilar información adicional para cada integrante seleccionado
    integrantes_con_datos = []
    for integrante in seleccionados:
        # Crear nombres de campo seguros para los formularios
        nombre_campo_siga = f"codigo_siga_{integrante.replace(' ', '_').replace('.', '')}"
        nombre_campo_cargo = f"cargo_{integrante.replace(' ', '_').replace('.', '')}"
        
        # Obtener valores, usar valores por defecto si no existen
        codigo_siga = request.form.get(nombre_campo_siga, "00415")
        cargo = request.form.get(nombre_campo_cargo, "Asistente jurisdiccional")
        
        integrantes_con_datos.append({
            "nombre": integrante,
            "codigo_siga": codigo_siga,
            "cargo": cargo
        })

    if not nombre_postulante or len(seleccionados) != 3:
        abort(400, "Debes completar todos los campos y seleccionar tres integrantes del comité.")

    try:
        # Pasar los datos al generador de PDF
        archivo_pdf = generar_documento(
            nombre_postulante,
            integrantes_con_datos,
            titulo_proceso,
            dependencia
        )
        
        # Leer el contenido del archivo PDF
        with open(archivo_pdf, 'rb') as pdf_file:
            pdf_content = pdf_file.read()
        os.remove(archivo_pdf)  # Borrar el archivo después de leerlo

        # Crear una respuesta de Flask con el PDF
        response = make_response(pdf_content)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename="documento.pdf"'
        return response
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