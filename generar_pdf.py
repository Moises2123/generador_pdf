
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from textwrap import wrap
import tempfile
import os

def generar_documento(
    nombre_postulante, 
    datos_integrantes,
    titulo_proceso="PROCESO SELECCIÓN PERSONAL SUPLENCIA N° 002-2025-LORETO\nBAJO LOS ALCANCES DEL DECRETO LEGISLATIVO N° 728 DETERMINADO BAJO LA MODALIDAD DE SUPLENCIA",
    dependencia="Módulo Penal Central"
):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(temp_file.name, pagesize=letter)
    width, height = letter

    header_font = ("Helvetica-Bold", 10)
    detail_font = ("Helvetica-Bold", 10)
    cell_header_font = ("Helvetica-Bold", 9)
    cell_font_bold = ("Helvetica-Bold", 8)
    cell_font = ("Helvetica", 8)
    no_bold = {
        "Seguridad (convicción y coherencia en la expresión de sus ideas)",
        "Genera confianza y credibilidad en el ámbito técnico requerido para el puesto",
        "Conocimientos generales y específicos relacionados al perfil de puesto y/o funciones en la entidad.",
        "Conocimientos técnicos de las funciones",
        "Evidencia vocación de Servicio",
        "Acciones de éxito (logros obtenidos en sus puestos o trabajos anteriores, siempre que haya obtenido en ellos intervención directa)."
    }

    criterios = [
        ["1", "Seguridad (convicción y coherencia en la expresión de sus ideas)", "0", "1.5", ""],
        ["2", "Genera confianza y credibilidad en el ámbito técnico requerido para el puesto", "0", "3", ""],
        ["3", "Conocimientos generales y específicos relacionados al perfil de puesto y/o funciones en la entidad.", "0", "5", ""],
        ["4", "Conocimientos técnicos de las funciones", "0", "4", ""],
        ["5", "Evidencia vocación de Servicio", "0", "1.5", ""],
        ["6", "Acciones de éxito (logros obtenidos en sus puestos o trabajos anteriores, siempre que haya obtenido en ellos intervención directa).", "0", "5", ""],
        ["", "Total", "", "20", ""]
    ]

    # Dividir el título en líneas si es demasiado largo
    titulo_completo = titulo_proceso.strip()
    # Establecer un límite de caracteres por línea (ajusta según sea necesario)
    max_chars_per_line = 60
    
    for integrante_datos in datos_integrantes:
        integrante = integrante_datos["nombre"]
        codigo_siga = integrante_datos["codigo_siga"]
        cargo = integrante_datos["cargo"]
        
        # Dividir el título en múltiples líneas si es necesario
        titulo_lineas = []
        if len(titulo_completo) > max_chars_per_line:
            palabras = titulo_completo.split()
            linea_actual = ""
            
            for palabra in palabras:
                if len(linea_actual + " " + palabra) <= max_chars_per_line:
                    if linea_actual:
                        linea_actual += " " + palabra
                    else:
                        linea_actual = palabra
                else:
                    titulo_lineas.append(linea_actual)
                    linea_actual = palabra
            
            # Agregar la última línea
            if linea_actual:
                titulo_lineas.append(linea_actual)
        else:
            titulo_lineas = [titulo_completo]
        
        encabezado = [
            "ANEXO 10 - B",
            "FORMATO DE CALIFICACIÓN POR CRITERIOS EN LA ENTREVISTA PERSONAL",
            "CORTE SUPERIOR DE JUSTICIA DE LORETO"
        ]
        
        # Añadir las líneas del título al encabezado
        encabezado.extend(titulo_lineas)
        
        c.setFont(*header_font)
        for i, linea in enumerate(encabezado):
            y = height - 50 - i * 15
            c.drawCentredString(width / 2, y, linea)

        detalles = [
            f"Código de puesto (SIGA): {codigo_siga}",
            f"Nombre de la Posición o Cargo: {cargo}",
            f"Dependencia: {dependencia}",
            f"Nombre del Postulante: {nombre_postulante}",
            f"Apellidos y Nombres del Integrante del Comité: {integrante}"
        ]
        
        # Ajustar la posición vertical según la cantidad de líneas en el título
        ajuste_y = len(titulo_lineas) - 1  # -1 porque una línea ya está considerada en el diseño original
        x0, y0 = 50, height - 150 - (ajuste_y * 15)
        
        c.setFont(*detail_font)
        for linea in detalles:
            c.drawString(x0, y0, linea)
            y0 -= 15

        c.drawString(x0, y0 - 20, "Fecha: _____________")
        c.drawString(x0 + 250, y0 - 20, "Hora de inicio entrevista: ______________")

        table_x, table_y = 50, y0 - 80
        col_widths = [30, 300, 50, 70, 80]
        row_h = 40

        headers = ["N°", "Criterio", "Puntaje Mínimo", "Puntaje Máximo", "Puntaje otorgado (Decimales)"]
        c.setFont(*cell_header_font)
        for j, htext in enumerate(headers):
            x = table_x + sum(col_widths[:j])
            c.rect(x, table_y, col_widths[j], row_h, stroke=1, fill=0)
            max_w = col_widths[j] - 8
            max_chars = int(max_w / (cell_header_font[1] * 0.5))
            lines = wrap(htext, max_chars)
            max_lines = int(row_h / (cell_header_font[1] + 2))
            for k, line in enumerate(lines[:max_lines]):
                y_line = table_y + row_h - (k + 1) * (cell_header_font[1] + 2) - 2
                c.drawCentredString(x + col_widths[j] / 2, y_line, line)

        for i, fila in enumerate(criterios, start=1):
            y = table_y - i * row_h
            for j, celda in enumerate(fila):
                x = table_x + sum(col_widths[:j])
                c.rect(x, y, col_widths[j], row_h, stroke=1, fill=0)
                text = celda or ""
                font_name, font_size = (cell_font_bold if text not in no_bold else cell_font)
                c.setFont(font_name, font_size)
                max_w = col_widths[j] - 8
                max_chars = int(max_w / (font_size * 0.5))
                wrapped = wrap(text, max_chars)
                max_lines = int(row_h / (font_size + 2))
                for k, line in enumerate(wrapped[:max_lines]):
                    text_x = x + 4
                    text_y = y + row_h - (k + 1) * (font_size + 2) - 4
                    c.drawString(text_x, text_y, line)

        y_firma = table_y - (len(criterios) + 1) * row_h - 20
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(width / 2, y_firma, "__________________________________")
        c.drawCentredString(width / 2, y_firma - 15, "Firma Integrante del Comité")

        c.showPage()

    c.save()
    return temp_file.name