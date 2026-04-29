from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from datetime import datetime


# =========================
# 📄 PDF EJECUTIVO PRO
# =========================
def generar_pdf_ejecutivo(
    path,
    empresa,
    evaluacion_id,
    promedio,
    interpretacion,
    dominios,
    total_respuestas,
    chart_path,
    plan_ia
):

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(path, pagesize=A4)

    content = []

    # =========================
    # 🧾 PORTADA
    # =========================
    content.append(Paragraph("REPORTE EJECUTIVO NOM-035", styles["Title"]))
    content.append(Spacer(1, 20))

    content.append(Paragraph(f"Empresa: <b>{empresa}</b>", styles["Normal"]))
    content.append(Paragraph(f"Fecha: {datetime.now().strftime('%Y-%m-%d')}", styles["Normal"]))
    content.append(Paragraph(f"Evaluación ID: {evaluacion_id}", styles["Normal"]))

    content.append(Spacer(1, 30))

    # =========================
    # 📊 RESUMEN
    # =========================
    content.append(Paragraph("Resumen Ejecutivo", styles["Heading2"]))
    content.append(Spacer(1, 10))

    content.append(Paragraph(
        f"El análisis de factores de riesgo psicosocial arroja un nivel de "
        f"<b>{interpretacion}</b> con un puntaje promedio de "
        f"<b>{round(promedio,2)}</b>.",
        styles["Normal"]
    ))

    content.append(Spacer(1, 20))

    # =========================
    # 📊 KPI
    # =========================
    tabla = Table([
        ["Indicador", "Valor"],
        ["Promedio General", round(promedio, 2)],
        ["Nivel de Riesgo", interpretacion],
        ["Total Respuestas", total_respuestas]
    ])

    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.black),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold")
    ]))

    content.append(tabla)
    content.append(Spacer(1, 25))

    # =========================
    # 📈 DOMINIOS
    # =========================
    content.append(Paragraph("Resultados por Dominio", styles["Heading2"]))
    content.append(Spacer(1, 10))

    tabla_dominios = [["Dominio", "Puntaje"]]

    for nombre, valor in dominios.items():
        tabla_dominios.append([nombre, round(valor, 2)])

    tabla2 = Table(tabla_dominios)

    tabla2.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID", (0,0), (-1,-1), 0.5, colors.black)
    ]))

    content.append(tabla2)
    content.append(Spacer(1, 25))

    # =========================
    # 📊 GRÁFICA
    # =========================
    content.append(Paragraph("Visualización de Resultados", styles["Heading2"]))
    content.append(Spacer(1, 10))

    if chart_path:
        content.append(Image(chart_path, width=450, height=250))

    content.append(Spacer(1, 25))

    # =========================
    # 🧠 INTERPRETACIÓN
    # =========================
    content.append(Paragraph("Interpretación", styles["Heading2"]))
    content.append(Spacer(1, 10))
    content.append(Paragraph(interpretacion, styles["Normal"]))

    content.append(Spacer(1, 25))

    # =========================
    # 🤖 PLAN IA
    # =========================
    content.append(Paragraph("Recomendaciones Estratégicas", styles["Heading2"]))
    content.append(Spacer(1, 10))

    content.append(Paragraph(
        plan_ia[:1500],  # evita romper PDF
        styles["Normal"]
    ))

    doc.build(content)