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


def generate_invoice_pdf(invoice):
    """Profesyonel fatura PDF'i oluştur."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm,
                            leftMargin=2*cm, rightMargin=2*cm)
    elements = []
    styles = getSampleStyleSheet()

    # Custom styles
    company_style = ParagraphStyle('company', parent=styles['Normal'],
                                   fontSize=18, leading=22, fontName='Helvetica-Bold',
                                   textColor=colors.HexColor('#e67e22'))
    subtitle_style = ParagraphStyle('subtitle', parent=styles['Normal'],
                                    fontSize=10, leading=13, textColor=colors.grey)
    normal_style = ParagraphStyle('normal_custom', parent=styles['Normal'],
                                  fontSize=10, leading=14)
    bold_style = ParagraphStyle('bold_custom', parent=styles['Normal'],
                                fontSize=10, leading=14, fontName='Helvetica-Bold')
    right_style = ParagraphStyle('right', parent=styles['Normal'],
                                 fontSize=10, leading=14, alignment=2)  # TA_RIGHT=2
    right_bold = ParagraphStyle('right_bold', parent=styles['Normal'],
                                fontSize=12, leading=16, fontName='Helvetica-Bold', alignment=2)
    center_style = ParagraphStyle('center_inv', parent=styles['Normal'],
                                  alignment=TA_CENTER, fontSize=9, leading=11, textColor=colors.grey)

    # ===== HEADER =====
    # Company info + Invoice info side by side
    header_data = [
        [Paragraph("BASAK YEMEK CATERING", company_style),
         Paragraph(f"FATURA", ParagraphStyle('inv_title', parent=styles['Normal'],
                   fontSize=22, leading=26, fontName='Helvetica-Bold', alignment=2,
                   textColor=colors.HexColor('#2c3e50')))],
        [Paragraph("Yemek Uretim ve Catering Hizmetleri", subtitle_style),
         Paragraph(f"No: {invoice.get('invoice_number', '-')}", right_style)],
        [Paragraph("Ankara, Turkiye", subtitle_style),
         Paragraph(f"Tarih: {invoice.get('date', '-')}", right_style)],
    ]
    header_table = Table(header_data, colWidths=[10*cm, 7*cm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.3*cm))

    # Divider line
    divider = Table([['']],  colWidths=[17*cm])
    divider.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 2, colors.HexColor('#e67e22')),
    ]))
    elements.append(divider)
    elements.append(Spacer(1, 0.5*cm))

    # ===== CUSTOMER INFO =====
    customer_name = invoice.get('customer_name', '-')
    customer_address = invoice.get('customer_address', '') or ''
    customer_phone = invoice.get('customer_phone', '') or ''
    customer_contact = invoice.get('customer_contact', '') or ''

    cust_info = [
        [Paragraph("<b>FATURA EDILEN:</b>", normal_style), ''],
        [Paragraph(f"<b>{customer_name}</b>", bold_style), ''],
    ]
    if customer_contact:
        cust_info.append([Paragraph(f"Yetkili: {customer_contact}", normal_style), ''])
    if customer_address:
        cust_info.append([Paragraph(f"Adres: {customer_address}", normal_style), ''])
    if customer_phone:
        cust_info.append([Paragraph(f"Tel: {customer_phone}", normal_style), ''])

    period_start = invoice.get('period_start', '')
    period_end = invoice.get('period_end', '')
    if period_start and period_end:
        cust_info.append([Paragraph(f"<b>Donem:</b> {period_start} - {period_end}", normal_style), ''])

    cust_table = Table(cust_info, colWidths=[10*cm, 7*cm])
    cust_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))
    elements.append(cust_table)
    elements.append(Spacer(1, 0.8*cm))

    # ===== INVOICE DETAILS TABLE =====
    unit_price = float(invoice.get('unit_price', 0) or 0)
    total_portions = int(invoice.get('total_portions', 0) or 0)
    subtotal = float(invoice.get('total_amount', 0) or 0)
    tax_amount = float(invoice.get('tax_amount', 0) or 0)
    grand_total = subtotal + tax_amount

    detail_header = ['Aciklama', 'Miktar', 'Birim Fiyat', 'Tutar']
    detail_row = [
        'Yemek Hizmeti (Porsiyon)',
        str(total_portions),
        f"{unit_price:.2f} TL",
        f"{subtotal:.2f} TL"
    ]

    detail_data = [detail_header, detail_row]
    detail_table = Table(detail_data, colWidths=[7*cm, 3*cm, 3.5*cm, 3.5*cm])
    detail_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWHEIGHT', (0, 0), (-1, -1), 0.8*cm),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(detail_table)
    elements.append(Spacer(1, 0.5*cm))

    # ===== TOTALS =====
    totals_data = [
        ['', '', 'Ara Toplam:', f"{subtotal:.2f} TL"],
        ['', '', 'KDV (%10):', f"{tax_amount:.2f} TL"],
        ['', '', 'GENEL TOPLAM:', f"{grand_total:.2f} TL"],
    ]
    totals_table = Table(totals_data, colWidths=[7*cm, 3*cm, 3.5*cm, 3.5*cm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (2, 2), (-1, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (2, 2), (-1, 2), 12),
        ('LINEABOVE', (2, 2), (-1, 2), 1.5, colors.HexColor('#2c3e50')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 1.5*cm))

    # ===== NOTES =====
    notes = invoice.get('notes', '')
    if notes:
        elements.append(Paragraph(f"<b>Not:</b> {notes}", normal_style))
        elements.append(Spacer(1, 0.5*cm))

    # ===== FOOTER =====
    elements.append(Spacer(1, 1*cm))
    footer_divider = Table([['']],  colWidths=[17*cm])
    footer_divider.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    elements.append(footer_divider)
    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph("Basak Yemek Catering | Ankara, Turkiye | info@basakyemek.com", center_style))
    elements.append(Paragraph("Bu fatura elektronik ortamda olusturulmustur.", center_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer
