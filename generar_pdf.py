from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import mm, inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from textwrap import wrap
import tempfile
import os

def generar_documento(
    nombre_postulante, 
    datos_integrantes,
    titulo_proceso="PROCESO SELECCIÓN PERSONAL SUPLENCIA N° 002-2025-LORETO\nBAJO LOS ALCANCES DEL DECRETO LEGISLATIVO N° 728 DETERMINADO BAJO LA MODALIDAD DE SUPLENCIA",
    dependencia="Módulo Penal Central"
):
    """
    Genera un documento PDF profesional para evaluación de entrevistas.
    
    Args:
        nombre_postulante (str): Nombre completo del postulante
        datos_integrantes (list): Lista de diccionarios con datos de integrantes
        titulo_proceso (str): Título del proceso de selección
        dependencia (str): Nombre de la dependencia
    
    Returns:
        str: Ruta del archivo PDF generado
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(temp_file.name, pagesize=letter)
    width, height = letter
    
    # Configuración de fuentes y estilos mejorados
    fonts = {
        'title': ("Helvetica-Bold", 14),
        'subtitle': ("Helvetica-Bold", 12),
        'header': ("Helvetica-Bold", 11),
        'body': ("Helvetica-Bold", 10),
        'cell_header': ("Helvetica-Bold", 9),
        'cell_bold': ("Helvetica-Bold", 8),
        'cell_normal': ("Helvetica", 8),
        'small': ("Helvetica", 7)
    }
    
    # Configuración de colores
    colors_config = {
        'header_bg': colors.lightgrey,
        'border': colors.black,
        'text': colors.black
    }
    
    # Criterios de evaluación con mejor formato
    criterios = [
        ["1", "Seguridad (convicción y coherencia en la expresión de sus ideas)", "0", "1.5", ""],
        ["2", "Genera confianza y credibilidad en el ámbito técnico requerido para el puesto", "0", "3", ""],
        ["3", "Conocimientos generales y específicos relacionados al perfil de puesto y/o funciones en la entidad", "0", "5", ""],
        ["4", "Conocimientos técnicos de las funciones", "0", "4", ""],
        ["5", "Evidencia vocación de Servicio", "0", "1.5", ""],
        ["6", "Acciones de éxito (logros obtenidos en sus puestos o trabajos anteriores, siempre que haya obtenido en ellos intervención directa)", "0", "5", ""],
        ["", "TOTAL", "", "20", ""]
    ]
    
    # Textos que van en fuente normal (no bold)
    no_bold = {
        "Seguridad (convicción y coherencia en la expresión de sus ideas)",
        "Genera confianza y credibilidad en el ámbito técnico requerido para el puesto",
        "Conocimientos generales y específicos relacionados al perfil de puesto y/o funciones en la entidad",
        "Conocimientos técnicos de las funciones",
        "Evidencia vocación de Servicio",
        "Acciones de éxito (logros obtenidos en sus puestos o trabajos anteriores, siempre que haya obtenido en ellos intervención directa)"
    }
    
    def draw_header(canvas, y_start):
        """Dibuja el encabezado del documento con mejor espaciado"""
        c.setFont(*fonts['title'])
        
        # Título principal
        headers = [
            "ANEXO 10 - B",
            "FORMATO DE CALIFICACIÓN POR CRITERIOS EN LA ENTREVISTA PERSONAL",
            "CORTE SUPERIOR DE JUSTICIA DE LORETO"
        ]
        
        y_pos = y_start
        for header in headers:
            c.drawCentredString(width / 2, y_pos, header)
            y_pos -= 20
        
        # Procesar título del proceso con mejor formato
        c.setFont(*fonts['subtitle'])
        titulo_lines = format_title(titulo_proceso)
        
        y_pos -= 10  # Espacio adicional antes del título del proceso
        for line in titulo_lines:
            c.drawCentredString(width / 2, y_pos, line)
            y_pos -= 18
            
        return y_pos - 20
    
    def format_title(titulo):
        """Formatea el título dividiéndolo en líneas apropiadas"""
        max_chars = 60  # Límite de caracteres por línea
        words = titulo.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = f"{current_line} {word}".strip()
            if len(test_line) <= max_chars:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
            
        return lines
    
    def draw_details(canvas, y_start, codigo_siga, cargo, nombre_postulante, integrante):
        """Dibuja los detalles del proceso con mejor formato"""
        c.setFont(*fonts['body'])
        
        details = [
            f"Código de puesto (SIGA): {codigo_siga}",
            f"Nombre de la Posición o Cargo: {cargo}",
            f"Dependencia: {dependencia}",
            f"Nombre del Postulante: {nombre_postulante}",
            f"Apellidos y Nombres del Integrante del Comité: {integrante}"
        ]
        
        y_pos = y_start
        margin_left = 50
        
        for detail in details:
            c.drawString(margin_left, y_pos, detail)
            y_pos -= 15
            
        # Campos de fecha y hora con mejor espaciado
        y_pos -= 10
        c.drawString(margin_left, y_pos, "Fecha: ___________________")
        c.drawString(margin_left + 280, y_pos, "Hora de inicio entrevista: ___________________")
        
        return y_pos - 50
    
    def draw_evaluation_table(canvas, y_start):
        """Dibuja la tabla de evaluación combinando lo mejor de ambos códigos"""
        # Configuración de la tabla mejorada
        table_x = 50
        table_y = y_start
        col_widths = [30, 300, 50, 70, 80]  # Anchos optimizados del segundo código
        row_height = 40  # Altura consistente
        
        # Headers de la tabla
        headers = ["N°", "Criterio", "Puntaje\nMínimo", "Puntaje\nMáximo", "Puntaje otorgado\n(Decimales)"]
        
        # Dibujar headers
        c.setFont(*fonts['cell_header'])
        for j, htext in enumerate(headers):
            x = table_x + sum(col_widths[:j])
            c.rect(x, table_y, col_widths[j], row_height, stroke=1, fill=0)
            
            # Dividir texto en líneas para headers
            lines = htext.split('\n')
            line_height = fonts['cell_header'][1] + 2
            
            for k, line in enumerate(lines):
                y_line = table_y + row_height - (k + 1) * line_height - 5
                c.drawCentredString(x + col_widths[j] / 2, y_line, line)
        
        # Dibujar filas de criterios
        for i, fila in enumerate(criterios, start=1):
            y = table_y - i * row_height
            
            for j, celda in enumerate(fila):
                x = table_x + sum(col_widths[:j])
                
                # Aplicar fondo gris para la fila TOTAL
                if fila[1] == "TOTAL":
                    c.setFillColor(colors_config['header_bg'])
                    c.rect(x, y, col_widths[j], row_height, stroke=1, fill=1)
                    c.setFillColor(colors_config['text'])
                else:
                    c.rect(x, y, col_widths[j], row_height, stroke=1, fill=0)
                
                text = celda or ""
                
                # Determinar fuente según el contenido
                if text in no_bold:
                    font_name, font_size = fonts['cell_normal']
                else:
                    font_name, font_size = fonts['cell_bold']
                
                c.setFont(font_name, font_size)
                
                # Para la columna de criterios (columna 1), usar wrap
                if j == 1 and text:
                    max_w = col_widths[j] - 8
                    max_chars = int(max_w / (font_size * 0.5))
                    wrapped = wrap(text, max_chars)
                    max_lines = int(row_height / (font_size + 2))
                    
                    for k, line in enumerate(wrapped[:max_lines]):
                        text_x = x + 4
                        text_y = y + row_height - (k + 1) * (font_size + 2) - 4
                        c.drawString(text_x, text_y, line)
                else:
                    # Para otras columnas, centrar el texto
                    if text:
                        if j == 0 or j >= 2:  # Números y puntajes centrados
                            c.drawCentredString(x + col_widths[j] / 2, y + row_height / 2 - 4, text)
                        else:
                            text_x = x + 4
                            text_y = y + row_height / 2 - 4
                            c.drawString(text_x, text_y, text)
        
        return table_y - (len(criterios) + 1) * row_height - 20
    
    def draw_signature(canvas, y_pos):
        """Dibuja la sección de firma con mejor formato"""
        c.setFont(*fonts['body'])
        
        # Línea de firma más elegante
        c.drawCentredString(width / 2, y_pos, "__________________________________")
        
        # Texto de la firma
        c.drawCentredString(width / 2, y_pos - 15, "Firma del Integrante del Comité")
        
        return y_pos - 50
    
    # Generar documento para cada integrante
    for integrante_datos in datos_integrantes:
        integrante = integrante_datos["nombre"]
        codigo_siga = integrante_datos["codigo_siga"]
        cargo = integrante_datos["cargo"]
        
        # Dibujar encabezado
        y_pos = draw_header(c, height - 50)
        
        # Dibujar detalles
        y_pos = draw_details(c, y_pos, codigo_siga, cargo, nombre_postulante, integrante)
        
        # Dibujar tabla de evaluación
        y_pos = draw_evaluation_table(c, y_pos)
        
        # Dibujar firma
        draw_signature(c, y_pos)
        
        # Nueva página para el siguiente integrante
        c.showPage()
    
    # Guardar el documento
    c.save()
    return temp_file.name

# Función auxiliar para testing
def test_generar_documento():
    """Función de prueba para el generador de documentos"""
    datos_test = [
        {
            "nombre": "Dr. Juan Carlos Pérez López",
            "codigo_siga": "12345-2024",
            "cargo": "Especialista Legal Senior"
        },
        {
            "nombre": "Lic. María Elena González Díaz", 
            "codigo_siga": "12345-2024",
            "cargo": "Especialista Legal Senior"
        }
    ]
    
    archivo_pdf = generar_documento(
        nombre_postulante="Ana María Rodríguez Vásquez",
        datos_integrantes=datos_test
    )
    
    print(f"PDF generado exitosamente: {archivo_pdf}")
    return archivo_pdf

if __name__ == "__main__":
    test_generar_documento()