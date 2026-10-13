import os
from datetime import datetime
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from flask import current_app

def generate_billing_pdf(worker, start_date, end_date, productions, total_earnings, company_profit, advance_deducted=0.0, net_payout=None):
    """
    Generates a beautifully structured PDF Invoice for a worker's production period
    using ReportLab. Returns the relative URL path to the generated PDF.
    """
    if net_payout is None:
        net_payout = total_earnings
    # 1. Prepare file paths
    pdf_filename = f"bill_{worker.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    pdf_dir = current_app.config['PDF_FOLDER']
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_filepath = os.path.join(pdf_dir, pdf_filename)
    
    # 2. Setup document geometry
    doc = SimpleDocTemplate(
        pdf_filepath,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    # 3. Create elements array
    elements = []
    
    # 4. Custom Styles setup
    styles = getSampleStyleSheet()
    
    # Define color palette (Charcoal, Emerald Accent, Slate Details)
    primary_color = colors.HexColor('#0f172a')   # slate-900
    accent_color = colors.HexColor('#10b981')    # emerald-500
    text_color = colors.HexColor('#334155')      # slate-700
    border_color = colors.HexColor('#cbd5e1')    # slate-300
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=primary_color,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=accent_color,
        spaceAfter=15
    )
    
    meta_label_style = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        textColor=primary_color
    )
    
    meta_val_style = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=12,
        textColor=text_color
    )
    
    table_hdr_style = ParagraphStyle(
        'TableHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white,
        alignment=1 # Center aligned
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=text_color,
        alignment=1 # Center
    )
    
    table_cell_left = ParagraphStyle(
        'TableCellLeft',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=text_color,
        alignment=0 # Left
    )
    
    # 5. Header Branding
    elements.append(Paragraph("SHRI NEELAKANTESHWAR SAREES", title_style))
    elements.append(Paragraph("OFFICIAL WORKER STATEMENT & EARNINGS RECEIPT", subtitle_style))
    elements.append(Spacer(1, 10))
    
    # 6. Metadata Layout Table (Invoice details & Worker info side-by-side)
    metadata = [
        [
            Paragraph("<b>Worker Details:</b>", meta_label_style), "",
            Paragraph("<b>Invoice Metadata:</b>", meta_label_style), ""
        ],
        [
            Paragraph("Name:", meta_label_style), Paragraph(worker.name, meta_val_style),
            Paragraph("Invoice ID:", meta_label_style), Paragraph(f"SPM-{worker.id}-{datetime.now().strftime('%m%Y')}", meta_val_style)
        ],
        [
            Paragraph("Phone:", meta_label_style), Paragraph(worker.phone, meta_val_style),
            Paragraph("Date Issued:", meta_label_style), Paragraph(datetime.now().strftime('%d-%b-%Y %I:%M %p'), meta_val_style)
        ],
        [
            Paragraph("Address:", meta_label_style), Paragraph(worker.address or "N/A", meta_val_style),
            Paragraph("Statement Period:", meta_label_style), Paragraph(f"{start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}", meta_val_style)
        ]
    ]
    
    meta_table = Table(metadata, colWidths=[65, 200, 100, 175])
    meta_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),
        ('SPAN', (2, 0), (3, 0)),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (1, 0), 1, primary_color),
        ('LINEBELOW', (2, 0), (3, 0), 1, primary_color),
    ]))
    
    elements.append(meta_table)
    elements.append(Spacer(1, 20))
    
    # 7. Production details table
    # Columns: Date, Saree Name, Category, Labor Rate, Quantity, Earnings
    production_headers = [
        Paragraph("Date", table_hdr_style),
        Paragraph("Saree Product", table_hdr_style),
        Paragraph("Category", table_hdr_style),
        Paragraph("Labor Rate", table_hdr_style),
        Paragraph("Quantity", table_hdr_style),
        Paragraph("Earnings", table_hdr_style)
    ]
    
    production_data = [production_headers]
    
    total_qty = 0
    for p in productions:
        total_qty += p.quantity
        row = [
            Paragraph(p.date.strftime('%d-%b-%Y'), table_cell_style),
            Paragraph(f"{escape(p.saree.name)} — {escape(p.saree.color)}", table_cell_left),
            Paragraph(p.saree.category, table_cell_style),
            Paragraph(f"INR {p.saree.worker_payment:,.2f}", table_cell_style),
            Paragraph(str(p.quantity), table_cell_style),
            Paragraph(f"INR {p.worker_earnings:,.2f}", table_cell_style)
        ]
        production_data.append(row)
    
    # Grand Total row
    production_data.append([
        Paragraph("<b>Grand Total</b>", table_cell_left),
        "", "", "",
        Paragraph(f"<b>{total_qty} Items</b>", table_cell_style),
        Paragraph(f"<b>INR {total_earnings:,.2f}</b>", table_cell_style)
    ])
    
    col_widths = [75, 175, 75, 80, 55, 80]
    prod_table = Table(production_data, colWidths=col_widths)
    
    # Generate table styles: Alternating backgrounds, bold total row, custom cell boundaries
    t_style = [
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -2), 0.5, border_color),
        ('SPAN', (0, -1), (3, -1)), # Span total label
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e2e8f0')), # Shaded total row
        ('LINEABOVE', (0, -1), (-1, -1), 1.5, primary_color),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 8),
        ('TOPPADDING', (0, -1), (-1, -1), 8),
    ]
    
    # Alternating row colors
    for i in range(1, len(productions) + 1):
        if i % 2 == 0:
            t_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f8fafc')))
            
    prod_table.setStyle(TableStyle(t_style))
    elements.append(prod_table)
    elements.append(Spacer(1, 25))
    
    # 8. Financial Summary Block (Profit / Earnings overview)
    summary_hdr_style = ParagraphStyle(
        'SumHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=13,
        textColor=colors.white
    )
    
    summary_label_style = ParagraphStyle(
        'SumLbl',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        textColor=primary_color
    )
    
    summary_val_style = ParagraphStyle(
        'SumVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=12,
        textColor=text_color
    )
    
    summary_data = [
        [Paragraph("<b>FINANCIAL SUMMARY</b>", summary_hdr_style), ""],
        [Paragraph("Gross Weaver Earnings:", summary_label_style), Paragraph(f"INR {total_earnings:,.2f}", summary_val_style)],
        [Paragraph("Deductions (Advance Payouts):", summary_label_style), Paragraph(f"- INR {advance_deducted:,.2f}", ParagraphStyle('RedText', parent=summary_val_style, textColor=colors.HexColor('#ef4444')))],
        [Paragraph("Net Weaver Payout (To be Paid):", summary_label_style), Paragraph(f"INR {net_payout:,.2f}", ParagraphStyle('BoldNet', parent=summary_val_style, fontName='Helvetica-Bold', textColor=accent_color))],
        [Paragraph("Invoice Status:", summary_label_style), Paragraph("<b>PAID</b> (Bank Transfer / Cash)", ParagraphStyle('GreenText', parent=summary_val_style, textColor=accent_color))]
    ]
    
    summary_table = Table(summary_data, colWidths=[240, 300])
    summary_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc'))
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 45))
    
    # 9. Signatures Block
    sig_style = ParagraphStyle(
        'Sig',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=primary_color,
        alignment=1 # Center
    )
    
    sig_data = [
        [
            Paragraph("_____________________________<br/>Worker's Signature", sig_style),
            Paragraph("_____________________________<br/>Factory Manager's Signature", sig_style)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[270, 270])
    elements.append(sig_table)
    
    # 10. Build Document
    doc.build(elements)
    
    # Return relative URL path
    return f"static/invoices/{pdf_filename}"


def num_to_words(number):
    """Converts a floating-point number into Indian Rupees in Words (Indian numbering system)."""
    number = int(round(number))
    if number == 0:
        return "Rupees Zero Only"
        
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", 
            "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    
    def convert_chunk(n):
        chunk_str = ""
        if n >= 100:
            chunk_str += ones[n // 100] + " Hundred "
            n %= 100
        if n >= 20:
            chunk_str += tens[n // 10] + " "
            n %= 10
        if n > 0:
            chunk_str += ones[n] + " "
        return chunk_str.strip()

    words = ""
    # Indian numbering system: Crores, Lakhs, Thousands, Hundreds/Ones
    crores = number // 10000000
    number %= 10000000
    
    lakhs = number // 100000
    number %= 100000
    
    thousands = number // 1000
    number %= 1000
    
    if crores > 0:
        words += convert_chunk(crores) + " Crore "
    if lakhs > 0:
        words += convert_chunk(lakhs) + " Lakh "
    if thousands > 0:
        words += convert_chunk(thousands) + " Thousand "
    if number > 0:
        words += convert_chunk(number)
        
    return f"Rupees {words.strip()} Only"


def generate_sales_invoice_pdf(invoice):
    """
    Generates a beautifully structured PDF Sales Invoice matching the
    physical paper invoice layout of SHRI NEELAKANTESHWAR SAREES.
    """
    import shutil
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import Image as RLImage
    
    # --- A. KANNADA FONT REGISTRATION ---
    kannada_font_registered = False
    possible_fonts = [
        r"C:\Windows\Fonts\tunga.ttf",
        r"C:\Windows\Fonts\Tunga.ttf",
        r"C:\Windows\Fonts\Nirmala.ttf",
        r"C:\Windows\Fonts\nirmala.ttf",
        r"C:\Windows\Fonts\Hubballi-Regular.ttf"
    ]
    for fp in possible_fonts:
        if os.path.exists(fp):
            try:
                pdfmetrics.registerFont(TTFont('KannadaFont', fp))
                kannada_font_registered = True
                break
            except Exception:
                pass

    # --- B. COPY GENERATED DEITY LOGOS ---
    static_img_dir = os.path.join(current_app.root_path, 'static', 'images')
    os.makedirs(static_img_dir, exist_ok=True)
    
    left_target = os.path.join(static_img_dir, 'left_logo.png')
    right_target = os.path.join(static_img_dir, 'right_logo.png')
    
    user_provided_img = r"c:\xampp\htdocs\saree\neelakandeshwar.jpeg"
    orig_left = r"C:\Users\ADC\.gemini\antigravity\brain\913e501e-89c1-4cbb-a45e-2ee4a906e687\left_logo_1779702477688.png"
    orig_right = r"C:\Users\ADC\.gemini\antigravity\brain\913e501e-89c1-4cbb-a45e-2ee4a906e687\right_logo_1779702503864.png"
    
    # Overwrite right logo with actual image if provided by the user
    if os.path.exists(user_provided_img):
        try:
            shutil.copy(user_provided_img, right_target)
        except Exception:
            pass
    elif os.path.exists(orig_right) and not os.path.exists(right_target):
        try:
            shutil.copy(orig_right, right_target)
        except Exception:
            pass
            
    if os.path.exists(orig_left) and not os.path.exists(left_target):
        try:
            shutil.copy(orig_left, left_target)
        except Exception:
            pass

    # 1. Prepare file paths
    pdf_filename = f"invoice_{invoice.invoice_number.replace('/', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    pdf_dir = os.path.join(current_app.root_path, 'static', 'invoices', 'sales')
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_filepath = os.path.join(pdf_dir, pdf_filename)
    
    # 2. Setup document geometry
    doc = SimpleDocTemplate(
        pdf_filepath,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Define physical printed slip theme color (Deep Magenta/Purple)
    purple_color = colors.HexColor('#920058')
    charcoal_color = colors.HexColor('#1e293b')
    light_bg = colors.HexColor('#fcf4fa')
    
    # Typographic styles
    header_title_style = ParagraphStyle(
        'HeaderTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=22,
        textColor=purple_color,
        alignment=1, # Center
        spaceAfter=1
    )
    
    header_subtitle_style = ParagraphStyle(
        'HeaderSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=10,
        textColor=charcoal_color,
        alignment=1,
        spaceAfter=1
    )
    
    header_kannada_style = ParagraphStyle(
        'HeaderKan',
        parent=styles['Normal'],
        fontName='KannadaFont' if kannada_font_registered else 'Helvetica-Bold',
        fontSize=12,
        leading=14,
        textColor=purple_color,
        alignment=1,
        spaceAfter=2
    )
    
    gst_cell_style = ParagraphStyle(
        'GstCell',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=purple_color
    )
    
    invoice_title_style = ParagraphStyle(
        'InvTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        textColor=purple_color,
        alignment=1
    )
    
    meta_label_style = ParagraphStyle(
        'MetaLbl',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=purple_color
    )
    
    meta_val_style = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=charcoal_color
    )
    
    table_hdr_style = ParagraphStyle(
        'TblHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white,
        alignment=1
    )
    
    table_cell_center = ParagraphStyle(
        'TblCellCenter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=charcoal_color,
        alignment=1
    )
    
    table_cell_left = ParagraphStyle(
        'TblCellLeft',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=charcoal_color,
        alignment=0
    )
    
    table_cell_right = ParagraphStyle(
        'TblCellRight',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=charcoal_color,
        alignment=2
    )
    
    bank_style = ParagraphStyle(
        'BankStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=charcoal_color
    )
    
    words_style = ParagraphStyle(
        'WordsStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=10,
        textColor=charcoal_color
    )
    
    totals_label_style = ParagraphStyle(
        'TotalsLabel',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=purple_color
    )
    
    totals_label_bold = ParagraphStyle(
        'TotalsLabelBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        textColor=purple_color
    )
    
    totals_val_style = ParagraphStyle(
        'TotalsVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=charcoal_color,
        alignment=2
    )
    
    totals_val_bold = ParagraphStyle(
        'TotalsValBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        textColor=charcoal_color,
        alignment=2
    )
    
    terms_hdr_style = ParagraphStyle(
        'TermsHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=purple_color
    )
    
    terms_body_style = ParagraphStyle(
        'TermsBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9,
        textColor=charcoal_color
    )
    
    # 3. Build Header Panel (Dynamic 3-Column Deity & Branding layout)
    left_img = None
    if os.path.exists(left_target):
        try:
            left_img = RLImage(left_target, width=65, height=75)
        except Exception:
            pass
            
    right_img = None
    if os.path.exists(right_target):
        try:
            right_img = RLImage(right_target, width=60, height=60)
        except Exception:
            pass
            
    gst_line_style = ParagraphStyle(
        'GstLineStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=purple_color,
        alignment=1
    )
    
    top_meta_data = [
        [
            Paragraph("<b>GSTIN: 29AIRPH3656G1ZU</b>", ParagraphStyle('GstL', parent=gst_line_style, alignment=0)),
            Paragraph("Subject to Banhatti Jurisdiction<br/>II Shri Neelkhanteshwar Prasanna II", header_subtitle_style),
            Paragraph("<b>Cell: 9632371493</b>", ParagraphStyle('CellR', parent=gst_line_style, alignment=2))
        ]
    ]
    top_meta_table = Table(top_meta_data, colWidths=[130, 160, 110])
    top_meta_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    
    center_elements = [
        top_meta_table,
        Spacer(1, 3),
        Paragraph("SHRI NEELAKANTESHWAR SAREES", header_title_style),
        Paragraph("Sadashiv Nagar, Near Old Water Tank, Dist Bagalkot, BANHATTI-587311. (State Karnataka)", header_subtitle_style),
        Paragraph("Prop: Shankar Irappa Hipparagi", header_subtitle_style),
        Paragraph("ಶ್ರೀ ನೀಲಕಂಠೇಶ್ವರ ಸಾರೀಜ, ಬನಹಟ್ಟಿ.", header_kannada_style)
    ]
    
    main_header_data = [
        [left_img or "", center_elements, right_img or ""]
    ]
    
    # Total print canvas width is 540
    main_header_table = Table(main_header_data, colWidths=[70, 400, 70])
    main_header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    elements.append(main_header_table)
    elements.append(Spacer(1, 4))
    
    # 4. Tax Invoice Header Box
    inv_header_data = [
        [Paragraph("<b>TAX INVOICE<br/>CASH/CREDIT MEMO</b>", invoice_title_style)]
    ]
    inv_header_table = Table(inv_header_data, colWidths=[540])
    inv_header_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1.5, purple_color),
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    elements.append(inv_header_table)
    elements.append(Spacer(1, 6))
    
    # 5. Metadata Block (Sold To, Invoice Date, Lorry No, eWay Bill, GSTIN)
    meta_rows = [
        [
            Paragraph("Sold To:", meta_label_style), Paragraph(invoice.customer.name, meta_val_style),
            Paragraph("Invoice No.:", meta_label_style), Paragraph(invoice.invoice_number, ParagraphStyle('BoldVal', parent=meta_val_style, fontName='Helvetica-Bold'))
        ],
        [
            Paragraph("Invoice Date:", meta_label_style), Paragraph(invoice.date.strftime('%d-%b-%Y'), meta_val_style),
            Paragraph("Place of Supply:", meta_label_style), Paragraph(invoice.place_of_supply or "Banhatti", meta_val_style)
        ],
        [
            Paragraph("Lorry No.:", meta_label_style), Paragraph(invoice.lorry_no or "N/A", meta_val_style),
            Paragraph("State / Code:", meta_label_style), Paragraph(f"{invoice.customer.state} / {invoice.customer.state_code}", meta_val_style)
        ],
        [
            Paragraph("e Way Bill No.:", meta_label_style), Paragraph(invoice.eway_bill_no or "N/A", meta_val_style),
            Paragraph("Party's GSTIN:", meta_label_style), Paragraph(invoice.customer.gstin or "N/A", meta_val_style)
        ]
    ]
    meta_table = Table(meta_rows, colWidths=[90, 240, 95, 115])
    meta_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, purple_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, purple_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 6))
    
    # 6. Core Particulars Table
    headers = [
        Paragraph("<b>PARTICULARS</b>", table_hdr_style),
        Paragraph("<b>COLOR</b>", table_hdr_style),
        Paragraph("<b>HSN Code</b>", table_hdr_style),
        Paragraph("<b>Mtrs</b>", table_hdr_style),
        Paragraph("<b>Qty.</b>", table_hdr_style),
        Paragraph("<b>RATE (Rs.)</b>", table_hdr_style),
        Paragraph("<b>AMOUNT (Rs.)</b>", table_hdr_style)
    ]
    
    table_data = [headers]
    items_count = len(invoice.items)
    if items_count > 0:
        for item in invoice.items:
            table_data.append([
                Paragraph(escape(item.saree.name), table_cell_left),
                Paragraph(escape(item.saree.color), table_cell_center),
                Paragraph(item.hsn_code or "5007", table_cell_center),
                Paragraph(f"{item.meters:.1f}" if item.meters else "-", table_cell_center),
                Paragraph(str(item.quantity), table_cell_center),
                Paragraph(f"{item.rate:,.2f}", table_cell_right),
                Paragraph(f"{item.amount:,.2f}", table_cell_right)
            ])
    else:
        # Fallback for historic statements created without line-item detail records
        table_data.append([
            Paragraph("Saree Consignment (As per ledger)", table_cell_left),
            Paragraph("-", table_cell_center),
            Paragraph("5007", table_cell_center),
            Paragraph("-", table_cell_center),
            Paragraph("1", table_cell_center),
            Paragraph(f"{invoice.taxable_value:,.2f}", table_cell_right),
            Paragraph(f"{invoice.taxable_value:,.2f}", table_cell_right)
        ])
        items_count = 1
        
    # Pad table with blank rows to retain structured pre-printed sheet layout height
    padding_rows = max(1, 8 - items_count)
    for _ in range(padding_rows):
        table_data.append([
            Paragraph("", table_cell_left),
            Paragraph("", table_cell_center),
            Paragraph("", table_cell_center),
            Paragraph("", table_cell_center),
            Paragraph("", table_cell_center),
            Paragraph("", table_cell_right),
            Paragraph("", table_cell_right)
        ])
        
    col_widths = [150, 60, 65, 50, 50, 75, 90]
    prod_table = Table(table_data, colWidths=col_widths)
    prod_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1, 0), purple_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 1, purple_color),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(prod_table)
    elements.append(Spacer(1, 6))
    
    # 7. Summary & Totals Block (Bank Left, Calculations Right)
    bank_and_words = [
        [Paragraph("<b>Bank of Baroda</b> : Branch: Banhatti<br/><b>A/c. No.</b> 82970200000031<br/><b>IFS Code</b> BARB0VJBANH", bank_style)],
        [Spacer(1, 8)],
        [Paragraph(f"<b>Rupees in words:</b><br/><i>{num_to_words(invoice.grand_total)}</i>", words_style)]
    ]
    left_table = Table(bank_and_words, colWidths=[290])
    left_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    
    right_data = [
        [Paragraph("Taxable Value", totals_label_style), Paragraph(f"{invoice.taxable_value:,.2f}", totals_val_style)],
        [Paragraph(f"SGST &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {invoice.sgst_rate}%", totals_label_style), Paragraph(f"{invoice.sgst_amount:,.2f}", totals_val_style)],
        [Paragraph(f"CGST &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {invoice.cgst_rate}%", totals_label_style), Paragraph(f"{invoice.cgst_amount:,.2f}", totals_val_style)],
        [Paragraph(f"IGST &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {invoice.igst_rate}%", totals_label_style), Paragraph(f"{invoice.igst_amount:,.2f}", totals_val_style)],
        [Paragraph("Round off", totals_label_style), Paragraph(f"{invoice.round_off:,.2f}", totals_val_style)],
        [Paragraph("<b>G. TOTAL</b>", totals_label_bold), Paragraph(f"<b>{invoice.grand_total:,.2f}</b>", totals_val_bold)]
    ]
    right_table = Table(right_data, colWidths=[130, 110])
    right_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, purple_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BACKGROUND', (0, -1), (-1, -1), light_bg),
    ]))
    
    summary_data = [[left_table, right_table]]
    summary_table = Table(summary_data, colWidths=[295, 245])
    summary_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 8))
    
    # 8. Footer (Terms & Signatures)
    terms_box = [
        [Paragraph("<b>TERMS & CONDITIONS:</b>", terms_hdr_style)],
        [Paragraph("1. Our responsibility ceases once the goods leave our godown.", terms_body_style)],
        [Paragraph("2. We are not responsible for any damage in transit.", terms_body_style)],
        [Paragraph("3. Goods once sold cannot be taken back.", terms_body_style)],
        [Paragraph("4. Interest will be charged @ 18% if Amount not paid within 15 days.", terms_body_style)]
    ]
    terms_table = Table(terms_box, colWidths=[280])
    terms_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('TOPPADDING', (0,0), (-1,-1), 1),
    ]))
    
    sig_block_data = [
        [
            Paragraph("<i>For, Shri Neelakanteshwar Sarees</i>", ParagraphStyle('RightItalic', parent=meta_label_style, fontSize=8, alignment=2)),
        ],
        [Spacer(1, 20)],
        [
            Paragraph("Party's Signature", ParagraphStyle('SigL', parent=meta_label_style, fontSize=8.5, alignment=0)),
            Paragraph("Authorised Signature", ParagraphStyle('SigR', parent=meta_label_style, fontSize=8.5, alignment=2))
        ]
    ]
    sig_block_table = Table(sig_block_data, colWidths=[120, 130])
    sig_block_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    
    footer_data = [[terms_table, sig_block_table]]
    footer_table = Table(footer_data, colWidths=[290, 250])
    footer_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, purple_color),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(footer_table)
    
    # 9. Build PDF
    doc.build(elements)
    
    # Return relative static URL
    return f"static/invoices/sales/{pdf_filename}"
