import matplotlib
matplotlib.use("Agg")

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload

import os
import tempfile
import zipfile

import matplotlib.pyplot as plt
from openpyxl import Workbook

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

from app.api.deps import get_db, get_current_user
from app.models.usuario import Usuario
from app.models.asignacion import Asignacion
from app.models.respuesta import Respuesta
from app.models.pregunta import Pregunta
from app.models.evaluacion import Evaluacion
from app.models.cuestionario import Cuestionario

from app.services.calculo_nom035 import calcular_resultados
from app.services.pdf_empresa_nom035 import generar_pdf_empresa
from app.services.interpretacion_nom035 import interpretar_resultados
from app.services.cuestionarios_service import generar_cuestionario_pdf
from app.services.cuestionarios_blanco_service import generar_cuestionario_blanco
from app.services.reporte_ejecutivo_nom035 import generar_reporte_ejecutivo

from app.services.docx_service import generar_politicas_docx, generar_plan_docx, generar_entregables_nom035

router = APIRouter()

# =========================
# 🎯 PRIORIDAD POR NIVEL (FIX AUDITORÍA)
# =========================
def obtener_prioridad(nivel):

    nivel = str(nivel).strip().lower()  # 🔥 NORMALIZACIÓN CLAVE

    if nivel in ["muy alto", "alto"]:
        return "Alta"
    elif nivel == "medio":
        return "Media"
    else:
        return "Baja"

# =========================
# 🎨 FIX COLOR REPORTLAB
# =========================
def color_hex(nivel):
    if nivel in ["Muy alto", "Alto"]:
        return "#FF0000"
    elif nivel == "Medio":
        return "#FFA500"
    else:
        return "#008000"

# =========================
# 📊 ENDPOINT PRINCIPAL
# =========================
@router.get("/empresa/reporte/{evaluacion_id}")
def generar_reporte(
    evaluacion_id: str,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user)
):

    # =========================
    # 🔒 VALIDAR
    # =========================
    evaluacion = db.query(Evaluacion).filter_by(
        id=evaluacion_id,
        empresa_id=user.empresa_id
    ).first()

    if not evaluacion:
        raise HTTPException(404, "Evaluación no encontrada")

    cuestionario = db.query(Cuestionario).filter_by(
        id=evaluacion.cuestionario_id
    ).first()

    if not cuestionario:
        raise HTTPException(404, "Cuestionario no encontrado")

    tipo_cuestionario = cuestionario.tipo
    tipo_escala = evaluacion.tipo_escala

    # =========================
    # 📊 RESPUESTAS
    # =========================
    respuestas = db.query(Respuesta)\
        .join(Asignacion)\
        .join(Pregunta)\
        .options(
            joinedload(Respuesta.pregunta),
            joinedload(Respuesta.asignacion)
        )\
        .filter(Asignacion.evaluacion_id == evaluacion_id)\
        .all()

    if not respuestas:
        raise HTTPException(404, "No hay respuestas válidas")

    # =========================
    # 📚 PREGUNTAS
    # =========================
    preguntas = db.query(Pregunta).all()

    preguntas_dict = {p.id: p for p in preguntas}

    # =========================
    # 🔥 CÁLCULO ÚNICO (FUENTE DE VERDAD)
    # =========================
    resultados = calcular_resultados(
        respuestas,
        preguntas_dict,
        tipo_cuestionario=tipo_cuestionario,
        tipo_escala=tipo_escala
    )

    interpretacion = interpretar_resultados(resultados)

    # 🔥 FORZAR consistencia con frontend
    nivel_global = resultados["global"]["nivel"]
    puntaje_global = round(resultados["global"]["puntaje"], 2)
    dominios = resultados["dominios"]

    total_empleados = db.query(Asignacion).filter_by(
        evaluacion_id=evaluacion_id
    ).count()

    dominios_ordenados = sorted(
        dominios.items(),
        key=lambda x: x[1]["puntaje"],
        reverse=True
    )

    dominio_critico = dominios_ordenados[0][0] if dominios_ordenados else "No disponible"

    # =========================
    # 🧠 PLAN
    # =========================
    plan_acciones = []

    for dominio, data in dominios_ordenados:

        prioridad = obtener_prioridad(data["nivel"])

        plan_acciones.append({
            "dominio": dominio,
            "nivel": data["nivel"],
            "prioridad": prioridad,  # 🔥 NUEVO (clave)
            "accion": interpretacion.get("dominios", {}).get(dominio, {}).get("recomendacion", "Sin recomendación disponible"),
            "responsable": "Recursos Humanos",

            # 🔥 lógica real tipo consultora
            "inicio": "Semana 1" if prioridad == "Alta" else "Mes 1",
            "fin": "Mes 3" if prioridad == "Alta" else "Mes 6",

            # 🔥 evidencia auditable
            "evidencia": "Actas firmadas / Reportes / Evidencia fotográfica / KPIs"
        })

    # =========================
    # 📁 ARCHIVOS
    # =========================
    temp_dir = tempfile.mkdtemp()

    carpeta_cuestionarios = os.path.join(temp_dir, "5_Cuestionarios")
    os.makedirs(carpeta_cuestionarios, exist_ok=True)

    chart_path = os.path.join(temp_dir, "grafica.png")
    pdf_path = os.path.join(temp_dir, "1_Reporte_Ejecutivo.pdf")
    dashboard_pdf = os.path.join(temp_dir, "2_Dashboard.pdf")
    excel_path = os.path.join(temp_dir, "3_Resultados.xlsx")
    base_path = os.path.join(temp_dir, "4_Base_Respuestas.xlsx")
    politicas_path = os.path.join(temp_dir, "7_Politicas_NOM035.docx")
    plan_path = os.path.join(temp_dir, "8_Plan_Accion.docx")
    evidencia_path = os.path.join(temp_dir, "6_Evidencia.txt")
    zip_path = os.path.join(temp_dir, "Reporte_NOM035.zip")
    entregables_dir = os.path.join(temp_dir, "9_Entregables")
    os.makedirs(entregables_dir, exist_ok=True)

    # =========================
    # 📈 GRÁFICA
    # =========================
    plt.figure()
    plt.bar(
        [d[0] for d in dominios_ordenados],
        [round(d[1]["puntaje"], 2) for d in dominios_ordenados]
    )
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    # =========================
    # 📄 PDF EJECUTIVO (SIN RECÁLCULO)
    # =========================
    reporte_pro = generar_reporte_ejecutivo(
        empresa=str(user.empresa_id),
        empleados=total_empleados,
        resultados=resultados,  # 🔥 misma data exacta
        interpretacion=interpretacion
    )

    generar_pdf_empresa(reporte_pro, archivo=pdf_path)

    # =========================
    # 📊 DASHBOARD EJECUTIVO PRO
    # =========================
    styles = getSampleStyleSheet()
    doc_dash = SimpleDocTemplate(dashboard_pdf, pagesize=A4)

    # 🔥 COLOR POR NIVEL
    def color_nivel(nivel):
        if nivel in ["Muy alto", "Alto"]:
            return colors.red
        elif nivel == "Medio":
            return colors.orange
        else:
            return colors.green

    color_global = color_nivel(nivel_global)

    # =========================
    # 🧠 MENSAJE EJECUTIVO
    # =========================
    if nivel_global in ["Alto", "Muy alto"]:
        mensaje = "Riesgo elevado: se requiere intervención inmediata a nivel organizacional."
    elif nivel_global == "Medio":
        mensaje = "Riesgo moderado: se recomienda implementar acciones preventivas."
    else:
        mensaje = "Riesgo bajo: mantener y fortalecer condiciones actuales."

    # =========================
    # 📊 TOP DOMINIOS CRÍTICOS
    # =========================
    top_dominios = dominios_ordenados[:3]

    tabla_top = [["Dominio", "Nivel", "Impacto (%)"]]

    for d, info in top_dominios:
        tabla_top.append([
            d,
            info["nivel"],
            f"{round(info['puntaje'],2)}%"
        ])

    tabla_top = Table(tabla_top)
    tabla_top.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.black),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey)
    ]))

    # =========================
    # 📊 SCORECARDS
    # =========================
    scorecards = [["Dominio", "Nivel", "Puntaje"]]

    for d, info in dominios_ordenados:
        scorecards.append([
            d,
            info["nivel"],
            f"{round(info['puntaje'],2)}%"
        ])

    tabla_scores = Table(scorecards)
    tabla_scores.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.black),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey)
    ]))

    # =========================
    # 🧾 CONTENIDO
    # =========================
    contenido_dash = [

        Paragraph("Dashboard Ejecutivo NOM-035", styles["Title"]),
        Spacer(1, 15),

        Paragraph(f"<b>Nivel de Riesgo Global:</b> <font color='{color_hex(nivel_global)}'>{nivel_global}</font>", styles["Heading2"]),
        Paragraph(f"<b>Puntaje:</b> {puntaje_global}%", styles["Normal"]),
        Paragraph(f"<b>Dominio crítico:</b> {dominio_critico}", styles["Normal"]),

        Spacer(1, 10),

        Paragraph(f"<b>Interpretación:</b> {mensaje}", styles["Normal"]),

        Spacer(1, 20),

        Image(chart_path, width=420, height=220),

        Spacer(1, 20),

        Paragraph("Principales focos de atención", styles["Heading2"]),
        tabla_top,

        Spacer(1, 20),

        Paragraph("Detalle por dominio", styles["Heading2"]),
        tabla_scores
    ]

    doc_dash.build(contenido_dash)

    # =========================
    # 📊 EXCEL
    # =========================
    wb = Workbook()
    ws = wb.active
    ws.append(["Dominio", "Nivel", "Puntaje"])

    for d, data in dominios.items():
        ws.append([d, data["nivel"], round(data["puntaje"], 2)])

    wb.save(excel_path)

    # =========================
    # 📊 BASE
    # =========================
    wb2 = Workbook()
    ws2 = wb2.active
    ws2.append(["Empleado", "Pregunta", "Dominio", "Respuesta"])

    for r in respuestas:
        ws2.append([
            f"EMP-{r.asignacion.id}",
            r.pregunta.texto,
            r.pregunta.dominio,
            r.valor
        ])

    wb2.save(base_path)

    # =========================
    # 📄 CUESTIONARIOS
    # =========================
    asignaciones = {}
    for r in respuestas:
        asignaciones.setdefault(r.asignacion_id, []).append(r)

    for asignacion_id, resps in asignaciones.items():

        respuestas_formateadas = [
            {"pregunta": r.pregunta.texto, "valor": r.valor}
            for r in resps
        ]

        generar_cuestionario_pdf(
            path=os.path.join(carpeta_cuestionarios, f"EMP-{asignacion_id}.pdf"),
            empleado=f"EMP-{asignacion_id}",
            respuestas=respuestas_formateadas
        )

    # =========================
    # 🧾 WORD
    # =========================
    generar_politicas_docx(politicas_path, str(user.empresa_id))
    generar_plan_docx(plan_path, plan_acciones, str(user.empresa_id))
    archivos_entregables = generar_entregables_nom035(
    entregables_dir,
    str(user.empresa_id),
    interpretacion
    )

    # =========================
    # 📁 EVIDENCIA
    # =========================
    with open(evidencia_path, "w") as f:
        f.write(f"""
EVIDENCIA NOM-035

Empresa: {user.empresa_id}
Nivel: {nivel_global}
Puntaje: {puntaje_global}
Empleados: {total_empleados}
""")

    # =========================
    # 📦 ZIP
    # =========================
    with zipfile.ZipFile(zip_path, 'w') as zipf:

        zipf.write(pdf_path, "1_Reporte_Ejecutivo.pdf")
        zipf.write(dashboard_pdf, "2_Dashboard.pdf")
        zipf.write(excel_path, "3_Resultados.xlsx")
        zipf.write(base_path, "4_Base_Respuestas.xlsx")
        zipf.write(evidencia_path, "6_Evidencia.txt")
        zipf.write(politicas_path, "7_Politicas_NOM035.docx")
        zipf.write(plan_path, "8_Plan_Accion.docx")
        # =========================
        # 📁 ENTREGABLES (PLUS)
        # =========================
        for file in os.listdir(entregables_dir):
            if not file.endswith(".docx"):
                continue
            zipf.write(
                os.path.join(entregables_dir, file),
                f"9_Entregables/{file}"
            )

        for file in os.listdir(carpeta_cuestionarios):
            if not file.endswith(".pdf"):
                continue
            zipf.write(
                os.path.join(carpeta_cuestionarios, file),
                f"5_Cuestionarios/{file}"
            )

    return FileResponse(zip_path, filename="Reporte_NOM035.zip")


# =========================
# 📄 CUESTIONARIOS EN BLANCO
# =========================
@router.get("/empresa/cuestionario/{tipo}")
def descargar_cuestionario(tipo: str, db: Session = Depends(get_db)):

    if tipo not in ["I", "II", "III"]:
        raise HTTPException(400, "Tipo inválido")

    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, f"Cuestionario_{tipo}.pdf")

    generar_cuestionario_blanco(file_path, tipo, db)

    return FileResponse(
        file_path,
        filename=f"Cuestionario_{tipo}.pdf",
        media_type="application/pdf"
    )