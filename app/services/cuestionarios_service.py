from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime


def generar_cuestionario_pdf(path, empleado, respuestas):

    doc = SimpleDocTemplate(path, pagesize=A4)
    styles = getSampleStyleSheet()

    # 🔥 estilo para texto largo
    estilo_pregunta = ParagraphStyle(
        "pregunta",
        parent=styles["Normal"],
        fontSize=8,
        leading=10
    )

    estilo_respuesta = ParagraphStyle(
        "respuesta",
        parent=styles["Normal"],
        alignment=1  # centrado
    )

    contenido = []

    # =========================
    # 🧾 HEADER
    # =========================
    contenido.append(Paragraph("CUESTIONARIO NOM-035-STPS", styles["Title"]))
    contenido.append(Spacer(1, 10))

    contenido.append(Paragraph(f"<b>Empleado:</b> {empleado}", styles["Normal"]))
    contenido.append(Paragraph(f"<b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y')}", styles["Normal"]))
    contenido.append(Spacer(1, 15))

    # =========================
    # 📋 TABLA
    # =========================
    tabla = [
        [
            Paragraph("<b>Pregunta</b>", styles["Normal"]),
            Paragraph("<b>Respuesta</b>", styles["Normal"])
        ]
    ]

    for r in respuestas:
        tabla.append([
            Paragraph(r["pregunta"], estilo_pregunta),
            Paragraph(str(r["valor"]), estilo_respuesta)
        ])

    table = Table(
        tabla,
        colWidths=[420, 80],   # 🔥 MÁS ESPACIO A PREGUNTA
        repeatRows=1
    )

    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.black),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("VALIGN", (0,0), (-1,-1), "TOP"),  # 🔥 CLAVE
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
    ]))

    contenido.append(table)
    contenido.append(Spacer(1, 30))

    # =========================
    # ✍️ FIRMA
    # =========================
    contenido.append(Paragraph("______________________________", styles["Normal"]))
    contenido.append(Paragraph("Firma del trabajador", styles["Normal"]))

    doc.build(contenido)