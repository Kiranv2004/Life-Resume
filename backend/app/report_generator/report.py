from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def generate_report(user_email: str, metrics: dict, personality: dict) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("Life Resume Report")

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(72, 750, "Life Resume Personality Report")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(72, 735, f"Generated for: {user_email}")
    pdf.drawString(72, 720, f"Generated at: {datetime.utcnow().isoformat()}Z")

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(72, 690, "Behavior Metrics")
    y = 675
    pdf.setFont("Helvetica", 10)
    for key, value in metrics.items():
        pdf.drawString(72, y, f"{key.replace('_', ' ').title()}: {value:.2f}")
        y -= 14

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(72, y - 10, "Personality Traits")
    y -= 25
    pdf.setFont("Helvetica", 10)
    for key, value in personality.items():
        pdf.drawString(72, y, f"{key.replace('_', ' ').title()}: {value:.2f}")
        y -= 14

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(72, y - 10, "Narrative Summary")
    y -= 25
    summary = (
        "This developer demonstrates structured reasoning with measurable adaptability. "
        "Collaboration signals are present across reviews and issue participation, "
        "while persistence is reflected by consistent follow-through. "
        "The profile indicates a balance of analytical depth and experimentation."
    )
    for line in wrap_text(summary, 80):
        pdf.drawString(72, y, line)
        y -= 14

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer.read()


def wrap_text(text: str, width: int) -> list[str]:
    words = text.split()
    lines = []
    current = []
    count = 0
    for word in words:
        if count + len(word) + 1 > width:
            lines.append(" ".join(current))
            current = [word]
            count = len(word)
        else:
            current.append(word)
            count += len(word) + 1
    if current:
        lines.append(" ".join(current))
    return lines
