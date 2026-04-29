from openpyxl import Workbook

def generar_excel_respuestas(path, respuestas):

    wb = Workbook()
    ws = wb.active
    ws.title = "Respuestas"

    ws.append(["Asignacion", "Pregunta", "Valor"])

    for r in respuestas:
        ws.append([
            str(r.asignacion_id),
            str(r.pregunta_id),
            r.valor
        ])

    wb.save(path)