from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO

def generate_report(answers, costs):
    """
    Generate a PDF report of the cost analysis.

    Args:
        answers: Dictionary of user answers
        costs: Dictionary of calculated costs

    Returns:
        PDF bytes
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from io import BytesIO

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    flowables = []

    # Title
    title = Paragraph("Kidney Dialysis Cost Report", styles['Title'])
    flowables.append(title)
    flowables.append(Spacer(1, 12))

    # Summary
    summary = Paragraph("Monthly Cost Summary", styles['Heading2'])
    flowables.append(summary)
    flowables.append(Spacer(1, 6))

    # Cost Table
    data = [
        ["Treatment Type", "Monthly Cost (THB)"],
        ["Hemodialysis (HD)", f"฿{costs.get('hd', 0):,.2f}"],
        ["Peritoneal Dialysis (CAPD)", f"฿{costs.get('pd', 0):,.2f}"],
        ["Automated Peritoneal Dialysis (APD)", f"฿{costs.get('apd', 0):,.2f}"],
        ["Conservative Care (CCC)", f"฿{costs.get('ccc', 0):,.2f}"]
    ]

    t = Table(data, colWidths=[300, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (1, 0), 12),
        ('BACKGROUND', (0, 1), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    flowables.append(t)
    flowables.append(Spacer(1, 12))

    # Notes
    notes = Paragraph("Notes:", styles['Heading3'])
    flowables.append(notes)
    flowables.append(Spacer(1, 6))

    note1 = Paragraph("• Costs are estimates and may vary based on actual circumstances", styles['Normal'])
    note2 = Paragraph("• Actual costs may be lower based on your healthcare coverage", styles['Normal'])
    note3 = Paragraph("• Please consult healthcare professionals for more information", styles['Normal'])

    flowables.append(note1)
    flowables.append(note2)
    flowables.append(note3)

    # Build PDF
    doc.build(flowables)
    pdf = buffer.getvalue()
    buffer.close()

    return pdf