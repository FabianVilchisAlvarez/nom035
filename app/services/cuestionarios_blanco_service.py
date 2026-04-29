from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from sqlalchemy.orm import Session
from reportlab.lib.styles import ParagraphStyle

from app.models.cuestionario import Cuestionario
from app.models.pregunta import Pregunta


def generar_cuestionario_blanco(path, tipo, db: Session):

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(path, pagesize=A4)

    contenido = []

    # =========================
    # 🔍 OBTENER CUESTIONARIO
    # =========================
    cuestionario = db.query(Cuestionario).filter(
        Cuestionario.tipo == tipo
    ).first()

    if not cuestionario:
        raise Exception(f"No existe cuestionario tipo {tipo}")

    preguntas = db.query(Pregunta).filter(
        Pregunta.cuestionario_id == cuestionario.id
    ).order_by(Pregunta.orden).all()

    # =========================
    # 🧾 HEADER
    # =========================
    contenido.append(Paragraph(f"CUESTIONARIO NOM-035 - {tipo}", styles["Title"]))
    contenido.append(Spacer(1, 10))

    contenido.append(Paragraph("Nombre del trabajador: ____________________", styles["Normal"]))
    contenido.append(Paragraph("Fecha: ____________________", styles["Normal"]))
    contenido.append(Spacer(1, 15))

    # =========================
    # 🧠 DEFINIR ESCALA
    # =========================
    if tipo == "I":
        headers = ["Pregunta", "Sí", "No"]
        col_widths = [350, 80, 80]
    else:
        headers = ["Pregunta", "Nunca", "Casi nunca", "Algunas veces", "Casi siempre", "Siempre"]
        col_widths = [260, 60, 60, 60, 60, 60]

    tabla = [headers]

    # =========================
    # 🎨 ESTILO PARA PREGUNTAS (FIX WRAP)
    # =========================
    style_pregunta = ParagraphStyle(
        "pregunta",
        fontSize=8,
        leading=10
    )

    # =========================
    # 📄 PREGUNTAS
    # =========================
    for p in preguntas:
        fila = [Paragraph(p.texto, style_pregunta)]

        if tipo == "I":
            fila += ["", ""]
        else:
            fila += ["", "", "", "", ""]

        tabla.append(fila)

    # =========================
    # 🧱 TABLA
    # =========================
    table = Table(tabla, colWidths=col_widths, repeatRows=1)

    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.3, colors.black),

        # Header
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),

        # Texto
        ("FONTSIZE", (0,0), (-1,-1), 8),

        # 🔥 FIX CLAVE
        ("VALIGN", (0,0), (-1,-1), "TOP"),

        # 🔥 ESPACIADO PRO
        ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))

    contenido.append(table)

    doc.build(contenido)