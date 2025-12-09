# exportacion/exporters.py
import openpyxl
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from django.http import HttpResponse
from django.utils import timezone

# ==============================================================================
# 1. Exportación a Excel (usando openpyxl)
# ==============================================================================

def exportar_a_excel(elementos):
    """
    Genera un archivo Excel (.xlsx) con los datos del inventario.
    Devuelve un objeto HttpResponse con el archivo adjunto.
    """
    # 1. Crear un libro de trabajo y una hoja de cálculo
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Inventario Tecnológico"

    # 2. Definir los encabezados (Headers)
    columnas = [
        "SERIAL", "TIPO", "MARCA", "MODELO", "UBICACIÓN", "ESTADO", 
        "ADQUISICIÓN", "PRECIO", "REGISTRADO POR", "DESCRIPCIÓN"
    ]
    ws.append(columnas)
    
    # Aplicar formato básico a los encabezados
    header_font = openpyxl.styles.Font(bold=True)
    for cell in ws[1]:
        cell.font = header_font

    # 3. Llenar los datos de los elementos
    for elemento in elementos:
        fila = [
            elemento.serial,
            elemento.tipo_dispositivo.nombre if elemento.tipo_dispositivo else "N/A",
            elemento.marca,
            elemento.modelo,
            elemento.localizacion,
            elemento.estado.nombre if elemento.estado else "N/A",
            elemento.fecha_adquisicion.strftime('%Y-%m-%d'),
            float(elemento.precio) if elemento.precio is not None else 0.0,
            elemento.usuario_registro.email if elemento.usuario_registro else "Anónimo",
            elemento.descripcion,
        ]
        ws.append(fila)

    # 4. Ajustar el ancho de las columnas (opcional)
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter # Obtener la letra de la columna
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width

    # 5. Guardar el libro de trabajo en memoria
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    # 6. Crear y devolver la respuesta HTTP
    response = HttpResponse(
        output.read(), 
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    nombre_archivo = f"Inventario_Exportado_{timezone.now().strftime('%Y%m%d_%H%M')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    
    return response

# ==============================================================================
# 2. Exportación a PDF (usando reportlab)
# ==============================================================================

def exportar_a_pdf(elementos):
    """
    Genera un archivo PDF con la lista resumida del inventario.
    Devuelve un objeto HttpResponse con el archivo adjunto.
    """
    # 1. Preparar el buffer y el documento
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # 2. Título del Documento
    titulo = f"Inventario Tecnológico - Reporte {timezone.now().strftime('%Y-%m-%d')}"
    story.append(Paragraph(titulo, styles['Title']))
    story.append(Paragraph("<br/>", styles['Normal'])) # Espacio

    # 3. Preparar los datos de la tabla
    # Columnas a incluir en el PDF (resumidas)
    data = [
        ['Serial', 'Tipo', 'Marca', 'Modelo', 'Ubicación', 'Estado']
    ]
    for elemento in elementos:
        data.append([
            elemento.serial,
            elemento.tipo_dispositivo.nombre if elemento.tipo_dispositivo else "N/A",
            elemento.marca,
            elemento.modelo,
            elemento.localizacion,
            elemento.estado.nombre if elemento.estado else "N/A",
        ])

    # 4. Crear la tabla y aplicar estilos
    table = Table(data)
    
    # Definir el estilo de la tabla
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#CCCCCC')), # Encabezado gris
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    table.setStyle(style)
    
    story.append(table)

    # 5. Construir el documento
    doc.build(story)

    # 6. Crear y devolver la respuesta HTTP
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    nombre_archivo = f"Inventario_Exportado_{timezone.now().strftime('%Y%m%d_%H%M')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    
    return response