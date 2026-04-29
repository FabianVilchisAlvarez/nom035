from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
import os

from PIL import Image as PILImage


# 🔥 LOGO proporcional
def get_logo(logo_path, max_width=140):
    img = PILImage.open(logo_path)
    width, height = img.size
    aspect = height / width

    return Image(
        logo_path,
        width=max_width,
        height=(max_width * aspect)
    )


def generar_pdf_resultados(data, archivo="reporte_nom035.pdf", empresa="N/A", folio="N/A"):

    doc = SimpleDocTemplate(
        archivo,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # 🔥 ESTILOS PERSONALIZADOS
    titulo = ParagraphStyle(
        name="Titulo",
        parent=styles["Title"],
        alignment=TA_CENTER
    )

    subtitulo = ParagraphStyle(
        name="Subtitulo",
        parent=styles["Normal"],
        alignment=TA_CENTER
    )

    seccion = styles["Heading2"]
    normal = styles["Normal"]

    contenido = []

    # 🔹 LOGO CENTRADO
    logo_path = os.path.join("app", "assets", "logo.png")

    if os.path.exists(logo_path):
        logo = get_logo(logo_path)
        logo.hAlign = "CENTER"
        contenido.append(logo)

    contenido.append(Spacer(1, 15))

    # 🔥 ENCABEZADO LIMPIO (SIN DUPLICADOS)
    contenido.append(Paragraph(f"<b>Empresa:</b> {empresa}", normal))
    contenido.append(Paragraph(f"<b>Folio:</b> {folio}", normal))
    contenido.append(
        Paragraph(
            f"<b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y')}",
            normal
        )
    )

    contenido.append(Spacer(1, 10))

    # 🔥 TÍTULO
    contenido.append(
        Paragraph(
            "Evaluación de factores de riesgo psicosocial",
            subtitulo
        )
    )

    contenido.append(Spacer(1, 10))

    # 🔥 LÍNEA DIVISORIA
    contenido.append(HRFlowable(width="100%", thickness=1))
    contenido.append(Spacer(1, 15))

    # 🔹 RESULTADO GLOBAL
    contenido.append(Paragraph("1. Resultado Global", seccion))
    contenido.append(Spacer(1, 5))

    contenido.append(
        Paragraph(
            f"Puntaje total: <b>{data['global']['puntaje']}</b><br/>"
            f"Nivel de riesgo: <b>{data['global']['nivel']}</b>",
            normal
        )
    )

    contenido.append(Spacer(1, 20))

    # 🔹 DOMINIOS
    contenido.append(Paragraph("2. Resultados por Dominio", seccion))
    contenido.append(Spacer(1, 5))

    for dominio, info in data["dominios"].items():
        contenido.append(
            Paragraph(
                f"• <b>{dominio}</b>: {info['puntaje']} puntos (Nivel {info['nivel']})",
                normal
            )
        )

    contenido.append(Spacer(1, 20))

    # 🔹 INTERPRETACIÓN
    contenido.append(Paragraph("3. Interpretación", seccion))
    contenido.append(Spacer(1, 5))

    contenido.append(
        Paragraph(data["interpretacion"], normal)
    )

    contenido.append(Spacer(1, 20))

    # 🔹 CONCLUSIÓN
    contenido.append(Paragraph("4. Conclusión", seccion))
    contenido.append(Spacer(1, 5))

    contenido.append(
        Paragraph(
            "Con base en los resultados obtenidos, se recomienda implementar acciones preventivas y correctivas conforme a la NOM-035-STPS, así como dar seguimiento continuo a los factores detectados.",
            normal
        )
    )

    contenido.append(Spacer(1, 30))

    # 🔥 FOOTER
    contenido.append(HRFlowable(width="100%", thickness=1))
    contenido.append(Spacer(1, 5))

    contenido.append(
        Paragraph(
            "Reporte generado automáticamente por sistema NOM-035 SaaS",
            subtitulo
        )
    )

    # 🔹 GENERAR PDF
    doc.build(contenido)

    return archivo