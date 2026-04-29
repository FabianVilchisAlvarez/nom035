from sqlalchemy.orm import Session

from app.models.cuestionario import Cuestionario
from app.models.pregunta import Pregunta
from app.models.opcion_respuesta import OpcionRespuesta


# =====================================================
# 🔹 ESCALAS
# =====================================================
ESCALA_LIKERT = [
    ("Siempre", 4),
    ("Casi siempre", 3),
    ("Algunas veces", 2),
    ("Casi nunca", 1),
    ("Nunca", 0),
]

ESCALA_BINARIA = [
    ("Sí", 1),
    ("No", 0),
]


# =====================================================
# 🔹 HELPERS
# =====================================================
def crear_opciones(db: Session, pregunta_id, escala):
    db.add_all([
        OpcionRespuesta(
            pregunta_id=pregunta_id,
            texto=texto,
            valor=valor
        )
        for texto, valor in escala
    ])


def crear_cuestionario(db, tipo, nombre, descripcion, preguntas, escala):

    try:
        existe = db.query(Cuestionario).filter(
            Cuestionario.tipo == tipo
        ).first()

        if existe:
            print(f"✔ {tipo} ya existe")
            return

        cuestionario = Cuestionario(
            tipo=tipo,
            nombre=nombre,
            descripcion=descripcion
        )

        db.add(cuestionario)
        db.flush()

        for i, p in enumerate(preguntas):
            pregunta = Pregunta(
                cuestionario_id=cuestionario.id,
                texto=p["texto"],
                dominio=p["dominio"],
                categoria=p["categoria"],
                es_invertida=p["invertida"],
                orden=i + 1
            )

            db.add(pregunta)
            db.flush()

            crear_opciones(db, pregunta.id, escala)

        db.commit()
        print(f"🔥 Cuestionario {tipo} cargado")

    except Exception as e:
        db.rollback()
        print(f"❌ Error en {tipo}: {e}")


# =====================================================
# 🔥 FUNCIÓN PRINCIPAL
# =====================================================
def seed_nom035(db: Session):

    # =====================================================
    # 🟢 GUÍA I (OFICIAL - BINARIA)
    # =====================================================
    preguntas_I = [

        # 🔹 SECCIÓN I
        {"texto": "¿Ha presenciado o sufrido un accidente con muerte, pérdida de miembro o lesión grave?", "dominio": "Acontecimiento traumático", "categoria": "Acontecimiento traumático", "invertida": False},
        {"texto": "¿Ha sufrido asaltos en el trabajo?", "dominio": "Acontecimiento traumático", "categoria": "Acontecimiento traumático", "invertida": False},
        {"texto": "¿Ha presenciado actos violentos con lesiones graves?", "dominio": "Acontecimiento traumático", "categoria": "Acontecimiento traumático", "invertida": False},
        {"texto": "¿Ha sido víctima de secuestro?", "dominio": "Acontecimiento traumático", "categoria": "Acontecimiento traumático", "invertida": False},
        {"texto": "¿Ha recibido amenazas en el trabajo?", "dominio": "Acontecimiento traumático", "categoria": "Acontecimiento traumático", "invertida": False},
        {"texto": "¿Ha vivido otro evento que pusiera en riesgo su vida o salud o la de otras personas?", "dominio": "Acontecimiento traumático", "categoria": "Acontecimiento traumático", "invertida": False},

        # 🔹 SECCIÓN II
        {"texto": "¿Ha tenido recuerdos recurrentes del acontecimiento que le provocan malestar?", "dominio": "Recuerdos persistentes", "categoria": "Recuerdos", "invertida": False},
        {"texto": "¿Ha tenido sueños recurrentes sobre el acontecimiento que le producen malestar?", "dominio": "Recuerdos persistentes", "categoria": "Recuerdos", "invertida": False},

        # 🔹 SECCIÓN III
        {"texto": "¿Ha evitado pensamientos, sentimientos o conversaciones relacionadas con el evento?", "dominio": "Evitación", "categoria": "Evitación", "invertida": False},
        {"texto": "¿Ha evitado actividades, lugares o personas que le recuerdan el evento?", "dominio": "Evitación", "categoria": "Evitación", "invertida": False},
        {"texto": "¿Tiene dificultad para recordar partes importantes del evento?", "dominio": "Evitación", "categoria": "Evitación", "invertida": False},
        {"texto": "¿Ha disminuido su interés en sus actividades cotidianas?", "dominio": "Evitación", "categoria": "Evitación", "invertida": False},
        {"texto": "¿Se ha sentido distante o alejado de los demás?", "dominio": "Evitación", "categoria": "Evitación", "invertida": False},
        {"texto": "¿Tiene dificultad para expresar sus sentimientos?", "dominio": "Evitación", "categoria": "Evitación", "invertida": False},
        {"texto": "¿Siente que su vida será más corta o su futuro es limitado?", "dominio": "Evitación", "categoria": "Evitación", "invertida": False},

        # 🔹 SECCIÓN IV
        {"texto": "¿Ha tenido dificultades para dormir?", "dominio": "Afectación", "categoria": "Afectación", "invertida": False},
        {"texto": "¿Ha estado irritable o ha tenido arranques de enojo?", "dominio": "Afectación", "categoria": "Afectación", "invertida": False},
        {"texto": "¿Ha tenido dificultad para concentrarse?", "dominio": "Afectación", "categoria": "Afectación", "invertida": False},
        {"texto": "¿Ha estado nervioso o en constante alerta?", "dominio": "Afectación", "categoria": "Afectación", "invertida": False},
        {"texto": "¿Se sobresalta fácilmente?", "dominio": "Afectación", "categoria": "Afectación", "invertida": False},
    ]

    # =====================================================
    # 🟡 GUÍA II (LIKERT)
    # =====================================================
    preguntas_II = [

    # =========================
    # 🔹 AMBIENTE DE TRABAJO
    # =========================
    {"texto": "Mi trabajo me exige hacer mucho esfuerzo físico", "dominio": "Ambiente de trabajo", "categoria": "Condiciones deficientes", "invertida": False}, #1
    {"texto": "Me preocupa sufrir un accidente en mi trabajo", "dominio": "Ambiente de trabajo", "categoria": "Condiciones peligrosas", "invertida": False}, #2
    {"texto": "Considero que las actividades que realizo son peligrosas", "dominio": "Ambiente de trabajo", "categoria": "Trabajos peligrosos", "invertida": False}, #3

    # =========================
    # 🔹 CARGA DE TRABAJO
    # =========================
    {"texto": "Por la cantidad de trabajo que tengo debo quedarme tiempo adicional a mi turno", "dominio": "Carga de trabajo", "categoria": "Cargas cuantitativas", "invertida": False}, #4
    {"texto": "Por la cantidad de trabajo que tengo debo trabajar sin parar", "dominio": "Carga de trabajo", "categoria": "Ritmo", "invertida": False}, #5
    {"texto": "Considero que es necesario mantener un ritmo de trabajo acelerado", "dominio": "Carga de trabajo", "categoria": "Ritmo", "invertida": False}, #6
    {"texto": "Mi trabajo exige que esté muy concentrado", "dominio": "Carga de trabajo", "categoria": "Carga mental", "invertida": False}, #7
    {"texto": "Mi trabajo requiere que memorice mucha información", "dominio": "Carga de trabajo", "categoria": "Carga mental", "invertida": False}, #8
    {"texto": "Mi trabajo exige que atienda varios asuntos al mismo tiempo", "dominio": "Carga de trabajo", "categoria": "Cargas cuantitativas", "invertida": False}, #9

    {"texto": "En mi trabajo soy responsable de cosas de mucho valor", "dominio": "Carga de trabajo", "categoria": "Responsabilidad", "invertida": False}, #10
    {"texto": "Respondo ante mi jefe por los resultados de toda mi área de trabajo", "dominio": "Carga de trabajo", "categoria": "Responsabilidad", "invertida": False}, #11
    {"texto": "En mi trabajo me dan órdenes contradictorias", "dominio": "Carga de trabajo", "categoria": "Demandas contradictorias", "invertida": False}, #12
    {"texto": "Considero que en mi trabajo me piden hacer cosas innecesarias", "dominio": "Carga de trabajo", "categoria": "Demandas contradictorias", "invertida": False}, #13

    # =========================
    # 🔹 ORGANIZACIÓN DEL TIEMPO
    # =========================
    {"texto": "Trabajo horas extras más de tres veces a la semana", "dominio": "Jornada de trabajo", "categoria": "Jornada", "invertida": False}, #14
    {"texto": "Mi trabajo me exige laborar en días de descanso, festivos o fines de semana", "dominio": "Jornada de trabajo", "categoria": "Jornada", "invertida": False}, #15
    {"texto": "Considero que el tiempo en el trabajo es mucho y perjudica mis actividades familiares o personales", "dominio": "Interferencia trabajo-familia", "categoria": "Interferencia", "invertida": False}, #16
    {"texto": "Pienso en las actividades familiares o personales cuando estoy en mi trabajo", "dominio": "Interferencia trabajo-familia", "categoria": "Interferencia", "invertida": False}, #17

    # =========================
    # 🔹 CONTROL (INVERTIDAS)
    # =========================
    {"texto": "Mi trabajo permite que desarrolle nuevas habilidades", "dominio": "Control del trabajo", "categoria": "Desarrollo", "invertida": True}, #18
    {"texto": "En mi trabajo puedo aspirar a un mejor puesto", "dominio": "Control del trabajo", "categoria": "Desarrollo", "invertida": True}, #19
    {"texto": "Durante mi jornada de trabajo puedo tomar pausas cuando las necesito", "dominio": "Control del trabajo", "categoria": "Autonomía", "invertida": True}, #20
    {"texto": "Puedo decidir la velocidad a la que realizo mis actividades en mi trabajo", "dominio": "Control del trabajo", "categoria": "Autonomía", "invertida": True}, #21
    {"texto": "Puedo cambiar el orden de las actividades que realizo en mi trabajo", "dominio": "Control del trabajo", "categoria": "Autonomía", "invertida": True}, #22

    # =========================
    # 🔹 LIDERAZGO
    # =========================
    {"texto": "Me informan con claridad cuáles son mis funciones", "dominio": "Liderazgo", "categoria": "Claridad", "invertida": True}, #23
    {"texto": "Me explican claramente los resultados que debo obtener en mi trabajo", "dominio": "Liderazgo", "categoria": "Claridad", "invertida": True}, #24
    {"texto": "Me informan con quién puedo resolver problemas o asuntos de trabajo", "dominio": "Liderazgo", "categoria": "Claridad", "invertida": True}, #25

    {"texto": "Me permiten asistir a capacitaciones relacionadas con mi trabajo", "dominio": "Control del trabajo", "categoria": "Capacitación", "invertida": True}, #26
    {"texto": "Recibo capacitación útil para hacer mi trabajo", "dominio": "Control del trabajo", "categoria": "Capacitación", "invertida": True}, #27

    {"texto": "Mi jefe tiene en cuenta mis puntos de vista y opiniones", "dominio": "Liderazgo", "categoria": "Liderazgo", "invertida": True}, #28
    {"texto": "Mi jefe ayuda a solucionar los problemas que se presentan en el trabajo", "dominio": "Liderazgo", "categoria": "Liderazgo", "invertida": True}, #29

    # =========================
    # 🔹 RELACIONES
    # =========================
    {"texto": "Puedo confiar en mis compañeros de trabajo", "dominio": "Relaciones", "categoria": "Relaciones", "invertida": True}, #30
    {"texto": "Cuando tenemos que realizar trabajo de equipo los compañeros colaboran", "dominio": "Relaciones", "categoria": "Relaciones", "invertida": True}, #31
    {"texto": "Mis compañeros de trabajo me ayudan cuando tengo dificultades", "dominio": "Relaciones", "categoria": "Relaciones", "invertida": True}, #32

    # =========================
    # 🔹 VIOLENCIA
    # =========================
    {"texto": "En mi trabajo puedo expresarme libremente sin interrupciones", "dominio": "Violencia", "categoria": "Violencia laboral", "invertida": True}, #33
    {"texto": "Recibo críticas constantes a mi persona y/o trabajo", "dominio": "Violencia", "categoria": "Violencia laboral", "invertida": False}, #34
    {"texto": "Recibo burlas, humillaciones o ridiculizaciones", "dominio": "Violencia", "categoria": "Violencia laboral", "invertida": False}, #35
    {"texto": "Se ignora mi presencia o se me excluye de reuniones", "dominio": "Violencia", "categoria": "Violencia laboral", "invertida": False}, #36
    {"texto": "Se manipulan situaciones para hacerme parecer mal trabajador", "dominio": "Violencia", "categoria": "Violencia laboral", "invertida": False}, #37
    {"texto": "Se ignoran mis éxitos laborales y se atribuyen a otros", "dominio": "Violencia", "categoria": "Violencia laboral", "invertida": False}, #38
    {"texto": "Me bloquean oportunidades de ascenso", "dominio": "Violencia", "categoria": "Violencia laboral", "invertida": False}, #39
    {"texto": "He presenciado actos de violencia en mi centro de trabajo", "dominio": "Violencia", "categoria": "Violencia laboral", "invertida": False}, #40

    # =========================
    # 🔹 CLIENTES
    # =========================
    {"texto": "Atiendo clientes o usuarios muy enojados", "dominio": "Carga de trabajo", "categoria": "Carga emocional", "invertida": False}, #41
    {"texto": "Mi trabajo me exige atender personas muy necesitadas o enfermas", "dominio": "Carga de trabajo", "categoria": "Carga emocional", "invertida": False}, #42
    {"texto": "Debo demostrar sentimientos distintos a los míos", "dominio": "Carga de trabajo", "categoria": "Carga emocional", "invertida": False}, #43

    # =========================
    # 🔹 SUPERVISIÓN
    # =========================
    {"texto": "Comunican tarde los asuntos de trabajo", "dominio": "Relaciones", "categoria": "Supervisión", "invertida": False}, #44
    {"texto": "Dificultan el logro de los resultados del trabajo", "dominio": "Relaciones", "categoria": "Supervisión", "invertida": False}, #45
    {"texto": "Ignoran sugerencias para mejorar el trabajo", "dominio": "Relaciones", "categoria": "Supervisión", "invertida": False}, #46
]
    
    # =====================================================
    # 🟡 GUÍA II (LIKERT)
    # =====================================================
    preguntas_III = [

    # =========================
    # 🔹 AMBIENTE DE TRABAJO
    # =========================
    {"texto": "El espacio donde trabajo me permite realizar mis actividades de manera segura e higiénica", "dominio": "Ambiente", "categoria": "Condiciones", "invertida": True}, #1
    {"texto": "Mi trabajo me exige hacer mucho esfuerzo físico", "dominio": "Ambiente", "categoria": "Condiciones", "invertida": False}, #2
    {"texto": "Me preocupa sufrir un accidente en mi trabajo", "dominio": "Ambiente", "categoria": "Condiciones", "invertida": False}, #3
    {"texto": "Considero que en mi trabajo se aplican las normas de seguridad y salud", "dominio": "Ambiente", "categoria": "Condiciones", "invertida": True}, #4
    {"texto": "Considero que las actividades que realizo son peligrosas", "dominio": "Ambiente", "categoria": "Condiciones", "invertida": False}, #5

    # =========================
    # 🔹 CARGA DE TRABAJO
    # =========================
    {"texto": "Debo quedarme tiempo adicional a mi turno", "dominio": "Carga", "categoria": "Cuantitativa", "invertida": False}, #6
    {"texto": "Debo trabajar sin parar", "dominio": "Carga", "categoria": "Ritmo", "invertida": False}, #7
    {"texto": "Debo mantener un ritmo acelerado", "dominio": "Carga", "categoria": "Ritmo", "invertida": False}, #8

    {"texto": "Mi trabajo exige mucha concentración", "dominio": "Carga", "categoria": "Mental", "invertida": False}, #9
    {"texto": "Debo memorizar mucha información", "dominio": "Carga", "categoria": "Mental", "invertida": False}, #10
    {"texto": "Debo tomar decisiones difíciles rápidamente", "dominio": "Carga", "categoria": "Mental", "invertida": False}, #11
    {"texto": "Debo atender varios asuntos al mismo tiempo", "dominio": "Carga", "categoria": "Cuantitativa", "invertida": False}, #12

    {"texto": "Soy responsable de cosas de mucho valor", "dominio": "Carga", "categoria": "Responsabilidad", "invertida": False}, #13
    {"texto": "Respondo por los resultados de toda mi área", "dominio": "Carga", "categoria": "Responsabilidad", "invertida": False}, #14
    {"texto": "Recibo órdenes contradictorias", "dominio": "Carga", "categoria": "Contradicciones", "invertida": False}, #15
    {"texto": "Me piden hacer cosas innecesarias", "dominio": "Carga", "categoria": "Contradicciones", "invertida": False}, #16

    # =========================
    # 🔹 TIEMPO DE TRABAJO
    # =========================
    {"texto": "Trabajo horas extras frecuentemente", "dominio": "Jornada", "categoria": "Tiempo", "invertida": False}, #17
    {"texto": "Trabajo en días de descanso o fines de semana", "dominio": "Jornada", "categoria": "Tiempo", "invertida": False}, #18
    {"texto": "El trabajo afecta mis actividades personales", "dominio": "Interferencia", "categoria": "Trabajo-familia", "invertida": False}, #19
    {"texto": "Debo atender asuntos de trabajo en casa", "dominio": "Interferencia", "categoria": "Trabajo-familia", "invertida": False}, #20
    {"texto": "Pienso en asuntos personales en el trabajo", "dominio": "Interferencia", "categoria": "Trabajo-familia", "invertida": False}, #21
    {"texto": "Mis responsabilidades familiares afectan mi trabajo", "dominio": "Interferencia", "categoria": "Trabajo-familia", "invertida": False}, #22

    # =========================
    # 🔹 CONTROL (INVERTIDAS)
    # =========================
    {"texto": "Mi trabajo permite desarrollar habilidades", "dominio": "Control", "categoria": "Desarrollo", "invertida": True}, #23
    {"texto": "Puedo aspirar a un mejor puesto", "dominio": "Control", "categoria": "Desarrollo", "invertida": True}, #24
    {"texto": "Puedo tomar pausas cuando lo necesito", "dominio": "Control", "categoria": "Autonomía", "invertida": True}, #25
    {"texto": "Puedo decidir cuánto trabajo realizo", "dominio": "Control", "categoria": "Autonomía", "invertida": True}, #26
    {"texto": "Puedo decidir la velocidad de mi trabajo", "dominio": "Control", "categoria": "Autonomía", "invertida": True}, #27
    {"texto": "Puedo cambiar el orden de mis actividades", "dominio": "Control", "categoria": "Autonomía", "invertida": True}, #28

    {"texto": "Los cambios en el trabajo dificultan mi labor", "dominio": "Control", "categoria": "Cambio", "invertida": False}, #29
    {"texto": "Se consideran mis ideas en los cambios", "dominio": "Control", "categoria": "Cambio", "invertida": True}, #30

    # =========================
    # 🔹 LIDERAZGO
    # =========================
    {"texto": "Me informan claramente mis funciones", "dominio": "Liderazgo", "categoria": "Claridad", "invertida": True}, #31
    {"texto": "Me explican los resultados que debo lograr", "dominio": "Liderazgo", "categoria": "Claridad", "invertida": True}, #32
    {"texto": "Me explican los objetivos de mi trabajo", "dominio": "Liderazgo", "categoria": "Claridad", "invertida": True}, #33
    {"texto": "Sé con quién resolver problemas de trabajo", "dominio": "Liderazgo", "categoria": "Claridad", "invertida": True}, #34

    {"texto": "Me permiten capacitarme", "dominio": "Control", "categoria": "Capacitación", "invertida": True}, #35
    {"texto": "Recibo capacitación útil", "dominio": "Control", "categoria": "Capacitación", "invertida": True}, #36

    {"texto": "Mi jefe organiza bien el trabajo", "dominio": "Liderazgo", "categoria": "Liderazgo", "invertida": True}, #37
    {"texto": "Mi jefe considera mis opiniones", "dominio": "Liderazgo", "categoria": "Liderazgo", "invertida": True}, #38
    {"texto": "Mi jefe comunica información a tiempo", "dominio": "Liderazgo", "categoria": "Liderazgo", "invertida": True}, #39
    {"texto": "La orientación de mi jefe me ayuda", "dominio": "Liderazgo", "categoria": "Liderazgo", "invertida": True}, #40
    {"texto": "Mi jefe resuelve problemas laborales", "dominio": "Liderazgo", "categoria": "Liderazgo", "invertida": True}, #41

    # =========================
    # 🔹 RELACIONES
    # =========================
    {"texto": "Confío en mis compañeros", "dominio": "Relaciones", "categoria": "Relaciones", "invertida": True}, #42
    {"texto": "Resolvemos problemas con respeto", "dominio": "Relaciones", "categoria": "Relaciones", "invertida": True}, #43
    {"texto": "Me siento parte del grupo", "dominio": "Relaciones", "categoria": "Relaciones", "invertida": True}, #44
    {"texto": "Colaboramos en equipo", "dominio": "Relaciones", "categoria": "Relaciones", "invertida": True}, #45
    {"texto": "Mis compañeros me ayudan", "dominio": "Relaciones", "categoria": "Relaciones", "invertida": True}, #46

    # =========================
    # 🔹 ENTORNO ORGANIZACIONAL
    # =========================
    {"texto": "Me informan sobre mi desempeño", "dominio": "Entorno", "categoria": "Reconocimiento", "invertida": True}, #47
    {"texto": "La evaluación me ayuda a mejorar", "dominio": "Entorno", "categoria": "Reconocimiento", "invertida": True}, #48
    {"texto": "Me pagan a tiempo", "dominio": "Entorno", "categoria": "Reconocimiento", "invertida": True}, #49
    {"texto": "Mi salario es justo", "dominio": "Entorno", "categoria": "Reconocimiento", "invertida": True}, #50
    {"texto": "Reconocen mi buen trabajo", "dominio": "Entorno", "categoria": "Reconocimiento", "invertida": True}, #51
    {"texto": "Puedo crecer laboralmente", "dominio": "Entorno", "categoria": "Reconocimiento", "invertida": True}, #52
    {"texto": "Mi trabajo es estable", "dominio": "Entorno", "categoria": "Estabilidad", "invertida": True}, #53
    {"texto": "Hay mucha rotación de personal", "dominio": "Entorno", "categoria": "Estabilidad", "invertida": False}, #54
    {"texto": "Siento orgullo de trabajar aquí", "dominio": "Entorno", "categoria": "Pertenencia", "invertida": True}, #55
    {"texto": "Estoy comprometido con mi trabajo", "dominio": "Entorno", "categoria": "Pertenencia", "invertida": True}, #56

    # =========================
    # 🔹 VIOLENCIA
    # =========================
    {"texto": "Puedo expresarme libremente", "dominio": "Violencia", "categoria": "Violencia", "invertida": True}, #57
    {"texto": "Recibo críticas constantes", "dominio": "Violencia", "categoria": "Violencia", "invertida": False}, #58
    {"texto": "Recibo burlas o humillaciones", "dominio": "Violencia", "categoria": "Violencia", "invertida": False}, #59
    {"texto": "Me excluyen de reuniones", "dominio": "Violencia", "categoria": "Violencia", "invertida": False}, #60
    {"texto": "Manipulan situaciones para perjudicarme", "dominio": "Violencia", "categoria": "Violencia", "invertida": False}, #61
    {"texto": "Ignoran mis logros", "dominio": "Violencia", "categoria": "Violencia", "invertida": False}, #62
    {"texto": "Bloquean mi crecimiento", "dominio": "Violencia", "categoria": "Violencia", "invertida": False}, #63
    {"texto": "He presenciado violencia laboral", "dominio": "Violencia", "categoria": "Violencia", "invertida": False}, #64

    # =========================
    # 🔹 CLIENTES
    # =========================
    {"texto": "Atiendo clientes enojados", "dominio": "Carga", "categoria": "Emocional", "invertida": False}, #65
    {"texto": "Atiendo personas necesitadas o enfermas", "dominio": "Carga", "categoria": "Emocional", "invertida": False}, #66
    {"texto": "Debo ocultar mis emociones", "dominio": "Carga", "categoria": "Emocional", "invertida": False}, #67
    {"texto": "Atiendo situaciones de violencia", "dominio": "Carga", "categoria": "Emocional", "invertida": False}, #68

    # =========================
    # 🔹 SUPERVISIÓN
    # =========================
    {"texto": "Comunican tarde asuntos de trabajo", "dominio": "Relaciones", "categoria": "Supervisión", "invertida": False}, #69
    {"texto": "Dificultan resultados del trabajo", "dominio": "Relaciones", "categoria": "Supervisión", "invertida": False}, #70
    {"texto": "Cooperan poco cuando se necesita", "dominio": "Relaciones", "categoria": "Supervisión", "invertida": False}, #71
    {"texto": "Ignoran sugerencias de mejora", "dominio": "Relaciones", "categoria": "Supervisión", "invertida": False}, #72
]

    # =====================================================
    # 🔴 CREACIÓN
    # =====================================================
    crear_cuestionario(
        db,
        "I",
        "Guía I - Acontecimientos traumáticos severos",
        "Detección de eventos traumáticos conforme a NOM-035",
        preguntas_I,
        ESCALA_BINARIA
    )

    crear_cuestionario(
        db,
        "II",
        "Guía II - Factores de riesgo psicosocial",
        "Centros de trabajo de 16 a 50 trabajadores",
        preguntas_II,
        ESCALA_LIKERT
    )

    crear_cuestionario(
    db,
    "III",
    "Guía III - Factores de riesgo psicosocial",
    "Centros de trabajo de 51 o más trabajadores",
    preguntas_III,
    ESCALA_LIKERT
)
    
    if __name__ == "__main__":
        from app.database.connection import SessionLocal

        db = SessionLocal()

        seed_nom035(db)

        db.close()