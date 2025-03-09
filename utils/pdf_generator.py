from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO

def generate_report(answers, costs):
    """Generate a PDF report with treatment comparisons and recommendations."""
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Title
    elements.append(Paragraph("Dialysis Treatment Cost Report", styles['Title']))
    elements.append(Spacer(1, 20))
    
    # Patient Information
    elements.append(Paragraph("Patient Information", styles['Heading1']))
    patient_data = [
        ["Employment Status:", answers.get('employment', 'N/A')],
        ["Monthly Income:", f"฿{answers.get('income', 0):,.2f}"],
        ["Caregiver Need:", answers.get('caregiver_needs', 'N/A')],
        ["Distance to Center:", f"{answers.get('distance', 0)} km"]
    ]
    
    t = Table(patient_data, colWidths=[200, 300])
    t.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))
    
    # Cost Comparison
    elements.append(Paragraph("Monthly Cost Comparison", styles['Heading1']))
    cost_data = [
        ["Treatment Type", "Monthly Cost"],
        ["Hemodialysis", f"฿{costs['hd']:,.2f}"],
        ["Peritoneal Dialysis", f"฿{costs['pd']:,.2f}"],
        ["Palliative Care", f"฿{costs['palliative']:,.2f}"]
    ]
    
    t = Table(cost_data, colWidths=[200, 300])
    t.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t)
    
    # Build and return PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit

def generate_report(answers, costs):
    """Generate a PDF report with the user's inputs and calculated costs"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Set up fonts
    try:
        pdfmetrics.registerFont(TTFont('THSarabun', 'assets/THSarabun.ttf'))
        font = 'THSarabun'
    except:
        font = 'Helvetica'
    
    # Title
    c.setFont(font, 24)
    c.drawCentredString(width/2, height-50, "Kidney Dialysis Cost Report")
    
    # User information section
    c.setFont(font, 12)
    y = height-100
    
    c.drawString(50, y, "User Information:")
    y -= 20
    
    for key, value in answers.items():
        if y < 100:  # Check if we need a new page
            c.showPage()
            y = height-50
        
        text = f"{key}: {value}"
        for line in simpleSplit(text, font, 12, width-100):
            c.drawString(70, y, line)
            y -= 15
    
    # Cost comparison section
    y -= 30
    c.drawString(50, y, "Monthly Cost Comparison:")
    y -= 20
    
    for treatment, cost in costs.items():
        c.drawString(70, y, f"{treatment.upper()}: ฿{cost:,.2f}")
        y -= 15
    
    # Recommendations section
    y -= 30
    c.drawString(50, y, "Recommendations:")
    y -= 20
    
    # Find least expensive option
    least_expensive = min(costs, key=costs.get)
    c.drawString(70, y, f"Based on your inputs, {least_expensive.upper()} appears to be the most economical option.")
    
    # Finalize PDF
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
