from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER
from datetime import datetime


def generar_pdf_empresa(data, archivo="reporte_empresa_nom035.pdf"):

    doc = SimpleDocTemplate(
        archivo,
        pagesize=A4,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )

    styles = getSampleStyleSheet()

    titulo = ParagraphStyle(
        name="Titulo",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20
    )

    subtitulo = ParagraphStyle(
        name="Subtitulo",
        parent=styles["Heading2"],
        fontSize=13,
        spaceBefore=12
    )

    normal = ParagraphStyle(
        name="Normal",
        parent=styles["Normal"],
        fontSize=10,
        leading=14
    )

    centro = ParagraphStyle(
        name="Centro",
        parent=styles["Normal"],
        alignment=TA_CENTER
    )

    c = []

    # =========================
    # 🧾 PORTADA
    # =========================
    c.append(Paragraph("REPORTE EJECUTIVO NOM-035", titulo))
    c.append(Paragraph(f"{datetime.now().strftime('%d/%m/%Y')}", centro))
    c.append(Spacer(1, 20))
    c.append(HRFlowable(width="100%"))

    # =========================
    # 📊 RESUMEN
    # =========================
    c.append(Paragraph("Resumen Ejecutivo", subtitulo))
    c.append(Paragraph(data["resumen"], normal))

    # =========================
    # 📊 KPI
    # =========================
    g = data["resultados_generales"]

    tabla = Table([
        ["Indicador", "Valor"],
        ["Nivel", g["nivel"]],
        ["Puntaje", f"{round(g['puntaje'],2)}%"],  # 🔥 FIX
        ["Score bruto", round(g["score_bruto"], 2)],
        ["Dominio crítico", g["dominio_critico"]],
        ["Empleados", g["empleados"]],
    ])

    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.black),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey)
    ]))

    c.append(tabla)

    # =========================
    # 📊 DOMINIOS
    # =========================
    c.append(Paragraph("Análisis por Dominio", subtitulo))

    for d in data["analisis_dominios"]:
        c.append(Paragraph(
            f"<b>{d['nombre']}</b> — {d['nivel']} | Puntaje: {round(d['puntaje'],2)}%",  # 🔥 FIX
            normal
        ))

        # opcional: dejar score técnico pequeño
        if d.get("score_bruto") is not None:
            c.append(Paragraph(
                f"<font size=8 color=gray>Score técnico: {round(d['score_bruto'],2)}</font>",
                normal
            ))

        c.append(Paragraph(f"Acción: {d['accion']}", normal))
        c.append(Spacer(1, 8))

    # =========================
    # 🛠️ PLAN
    # =========================
    c.append(Paragraph("Plan de Acción Detallado", subtitulo))

    for p in data["plan"]:
        c.append(Paragraph(
            f"<b>{p['dominio']}</b> — {p['nivel']} ({p['prioridad']})",
            normal
        ))

        c.append(Paragraph(f"Acción: {p['accion']}", normal))
        c.append(Paragraph(f"Responsable: {p['responsable']}", normal))
        c.append(Paragraph(f"Plazo: {p['plazo']}", normal))
        c.append(Paragraph(f"KPI: {p['kpi']}", normal))
        c.append(Paragraph(f"Evidencia: {p['evidencia']}", normal))

        c.append(Spacer(1, 10))

    # =========================
    # ⚠️ CONCLUSIÓN
    # =========================
    c.append(Paragraph("Conclusión", subtitulo))
    c.append(Paragraph(data["conclusion"], normal))

    doc.build(c)