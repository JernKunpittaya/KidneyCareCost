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
