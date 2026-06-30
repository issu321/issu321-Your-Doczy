import pandas as pd
from pathlib import Path
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

def convert_excel_to_pdf(input_path, output_path):
    """Convert Excel file to PDF with formatted tables."""
    df = pd.read_excel(input_path)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=landscape(A4),
        rightMargin=36, leftMargin=36,
        topMargin=36, bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=20,
        alignment=1  # center
    )

    story = []

    # Title
    filename = Path(input_path).stem
    story.append(Paragraph(f"Excel Export: {filename}", title_style))
    story.append(Spacer(1, 12))

    # Prepare table data
    headers = [str(col) for col in df.columns]
    data = [headers]

    for _, row in df.iterrows():
        data.append([str(val) if pd.notna(val) else "" for val in row])

    # Limit rows for PDF readability
    if len(data) > 51:
        data = data[:51]
        data.append(["... (truncated)"] * len(headers))

    # Calculate column widths
    page_width = landscape(A4)[0] - 72
    col_width = page_width / len(headers)
    col_widths = [min(col_width, 150)] * len(headers)

    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4facfe')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor('#eef2f7')]),
    ]))

    story.append(table)
    doc.build(story)
