import pandas as pd
from fpdf import FPDF
import io
import os
from datetime import datetime

# Directorio de exportación
EXPORT_DIR = 'exports'

def export_to_excel(df, cliente_nombre):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Limpiar nombre del cliente para evitar caracteres inválidos en archivos
    clean_nombre = "".join([c if c.isalnum() else "_" for c in cliente_nombre])
    filename = f"{EXPORT_DIR}/Cliente_{clean_nombre}_{timestamp}.xlsx"
    
    # Guardar en archivo
    df.to_excel(filename, index=False, engine='xlsxwriter')
    
    # Crear buffer para descarga en Streamlit
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine='xlsxwriter')
    buffer.seek(0)
    
    return buffer, filename

def export_to_pdf(df, cliente_nombre):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_nombre = "".join([c if c.isalnum() else "_" for c in cliente_nombre])
    filename = f"{EXPORT_DIR}/Cliente_{clean_nombre}_{timestamp}.pdf"
    
    # Crear PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Movimientos de {cliente_nombre}", ln=True, align='C')
    
    # Encabezados
    pdf.set_font("Arial", 'B', size=10)
    header = "Fecha | Comp. | Detalle | Debe | Haber"
    pdf.cell(200, 10, txt=header, ln=True, align='L')
    
    # Datos
    pdf.set_font("Arial", size=10)
    for _, row in df.iterrows():
        line = f"{str(row['Fecha'])} | {str(row['NroComprobante'])} | {str(row['Detalle'])} | {str(row['Debe'])} | {str(row['Haber'])}"
        pdf.cell(200, 10, txt=line, ln=True, align='L')
    
    # Guardar archivo
    pdf.output(filename)
    
    # Leer para buffer de descarga
    with open(filename, "rb") as f:
        buffer = io.BytesIO(f.read())
        
    return buffer, filename
