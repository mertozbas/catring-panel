import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER


def generate_menu_pdf(menu, menu_data, day_names):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm)
    elements = []
    styles = getSampleStyleSheet()

    center_style = ParagraphStyle('center', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9, leading=11)
    title_style = ParagraphStyle('title_center', parent=styles['Normal'], alignment=TA_CENTER, fontSize=16, leading=20, spaceAfter=10)
    header_style = ParagraphStyle('header_small', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8, leading=10, textColor=colors.grey)
    item_style = ParagraphStyle('item', parent=styles['Normal'], alignment=TA_CENTER, fontSize=11, leading=14, fontName='Helvetica-Bold')

    elements.append(Paragraph("MENÜLERİMİZ HER HAFTA YENİLENMEKTEDİR.", header_style))
    elements.append(Paragraph("KİŞİ BAŞI BİR ÖĞÜN ORTALAMA 1000 KALORİ ÜZERİDİR.", header_style))
    elements.append(Paragraph("YEMEKLERİMİZ HİJYENİK ORTAMDA, MARKALI VE KALİTELİ MALZEMELERLE ÜRETİLMEKTEDİR.", header_style))
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph("HAFTALIK YEMEK LİSTESİ", title_style))
    elements.append(Spacer(1, 0.5*cm))

    # First row: Mon-Wed
    header_row1 = [day_names[i] for i in range(3)]
    data_row1 = []
    for day in range(3):
        items = menu_data.get(day, [])
        cell_text = '<br/>'.join([item.upper() for item in items]) if items else '-'
        data_row1.append(Paragraph(cell_text, item_style))

    table1 = Table([header_row1, data_row1], colWidths=[6*cm, 6*cm, 6*cm])
    table1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 2, colors.black),
        ('ROWHEIGHT', (0, 1), (-1, 1), 4*cm),
    ]))
    elements.append(table1)
    elements.append(Spacer(1, 0.5*cm))

    # Second row: Thu-Sat
    header_row2 = [day_names[i] for i in range(3, 6)]
    data_row2 = []
    for day in range(3, 6):
        items = menu_data.get(day, [])
        cell_text = '<br/>'.join([item.upper() for item in items]) if items else '-'
        data_row2.append(Paragraph(cell_text, item_style))

    table2 = Table([header_row2, data_row2], colWidths=[6*cm, 6*cm, 6*cm])
    table2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 2, colors.black),
        ('ROWHEIGHT', (0, 1), (-1, 1), 4*cm),
    ]))
    elements.append(table2)
    elements.append(Spacer(1, 1*cm))
    elements.append(Paragraph("BAŞAK YEMEK CATERİNG - Afiyet Olsun!", center_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer
