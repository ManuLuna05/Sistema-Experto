# Parche de compatibilidad para Python 3.10+
import collections
if not hasattr(collections, "Mapping"):
    import collections.abc
    collections.Mapping = collections.abc.Mapping
    collections.MutableMapping = collections.abc.MutableMapping
    collections.Sequence = collections.abc.Sequence
    collections.Iterable = collections.abc.Iterable

from experta import *

# HECHOS
class Jugador(Fact):
    """
    Atributos físicos medibles en una primera evaluación de cantera.

    altura_cm: talla en centímetros
    peso_kg: peso en kilogramos
    velocidad_ms: velocidad máxima en m/s
    salto_long_cm: longitud de salto horizontal en cm
    salto_alt_cm: altura de salto vertical en cm
    reaccion_ms: tiempo de reacción en milisegundos obtenido de la distancia de caída de regla: t = sqrt(2·d/g), d en metros)
    potencia_tiro: velocidad del balón al disparar km/h
    """
    pass


# MOTOR
class SistemaPosiciones(KnowledgeEngine):

    def __init__(self): # Constructor
        super().__init__() # Llama al constructor de la clase base
        self.scores = {} # Diccionario para acumular puntuaciones por posición
        self.reglas_activadas = [] # Lista para registrar las reglas que se activan durante la evaluación

    # Método auxiliar para acumular puntuaciones y registrar reglas
    def _score(self, posicion, peso, descripcion):
        self.scores[posicion] = self.scores.get(posicion, 0) + peso # Acumula el peso para la posición dada
        self.reglas_activadas.append(descripcion) # Registra la descripción de la regla activada



    # ============ PORTERO (POR) ==================
    @Rule(Jugador(
        reaccion_ms = P(lambda x: x <= 160), # Reacción muy rápida
        salto_alt_cm = P(lambda x: x >= 55), # Gran salto vertical
        altura_cm = P(lambda x: x >= 182) # Altura mínima de portero
    ))
    # Función que se ejecuta cuando se cumplen las condiciones de la regla para portero de élite
    def regla_por_elite(self): # Regla para portero de élite
        self._score("POR", 3.5, # Puntuación alta para portero de élite
            "R01 - Reacción <=160 ms + salto vertical >=55 cm + altura ≥182 cm")

    @Rule(Jugador(
        reaccion_ms = P(lambda x: x <= 175),
        altura_cm = P(lambda x: x >= 178)
    ))
    # Función que se ejecuta para portero con buen perfil físico pero reacción no tan rápida
    def regla_por_base(self):
        self._score("POR", 1.5,
            "R02 - Reacción <=175 ms + altura >=178 cm (perfil portero)")
        



    # ============ CENTRAL (DFC) ==================
    @Rule(Jugador(
        altura_cm = P(lambda x: x >= 183),
        peso_kg = P(lambda x: x >= 75),
        salto_alt_cm = P(lambda x: x >= 50)
    ))
    # Función que se ejecuta para central con perfil físico destacado
    def regla_dfc_1(self):
        self._score("DFC", 3.0, # Puntuación alta para central con perfil físico destacado
            "R03 - Altura >=183 cm + peso >=75 kg + salto vertical >=50 cm")

    @Rule(Jugador(
        altura_cm = P(lambda x: x >= 180),
        salto_long_cm = P(lambda x: x >= 210),
        velocidad_ms = P(lambda x: x < 8.0) # No necesita ser muy veloz
    ))
    # Función que se ejecuta para central con buen perfil de salto y altura pero velocidad moderada
    def regla_dfc_2(self):
        self._score("DFC", 1.5,
            "R04 - Altura >=180 cm + salto largo >=210 cm + velocidad moderada")
        




    # ============ LATERAL (LD / LI) ==================
    @Rule(Jugador(
        velocidad_ms = P(lambda x: x >= 8.0),
        salto_long_cm = P(lambda x: x >= 215),
        altura_cm = P(lambda x: x < 183) # laterales no muy altos
    ))
    def regla_ld(self):
        self._score("LD", 2.5,
            "R05 - Velocidad >=8.0 m/s + salto largo >=215 cm + altura <183 cm")

    @Rule(Jugador(
        velocidad_ms = P(lambda x: x >= 8.0),
        salto_long_cm = P(lambda x: x >= 215),
        altura_cm = P(lambda x: x < 183)
    ))
    def regla_li(self):
        self._score("LI", 2.5,
            "R06 - Perfil equivalente de lateral izquierdo")

    @Rule(Jugador(
        velocidad_ms = P(lambda x: x >= 7.5),
        reaccion_ms = P(lambda x: x <= 190)
    ))
    def regla_lateral_reaccion(self):
        self._score("LD", 1.0,
            "R07 - Velocidad ≥7.5 m/s + buena reacción (lateral reactivo)")
        self._score("LI", 1.0,
            "R07b - Ídem para lateral derecho")
        



    # ============ MEDIOCENTRO DEFENSIVO (MCD) ==================
    @Rule(Jugador(
        altura_cm = P(lambda x: x >= 178),
        peso_kg = P(lambda x: x >= 72),
        salto_alt_cm = P(lambda x: x >= 48),
        velocidad_ms = P(lambda x: x < 8.5)
    ))
    def regla_mcd_1(self):
        self._score("MCD", 2.5,
            "R08 - Altura >=178 cm + peso >=72 kg + salto >=48 cm + vel. moderada")

    @Rule(Jugador(
        peso_kg = P(lambda x: x >= 70),
        salto_long_cm = P(lambda x: x >= 205),
        reaccion_ms = P(lambda x: x <= 185)
    ))
    def regla_mcd_2(self):
        self._score("MCD", 1.5,
            "R09 - Peso >=70 kg + salto largo >=205 cm + reacción <=185 ms")
        




    # ============ MEDIOCENTRO (MC) ==================
    @Rule(Jugador(
        velocidad_ms = P(lambda x: 7.5 <= x <= 9.0),
        salto_long_cm = P(lambda x: x >= 210),
        salto_alt_cm = P(lambda x: x >= 45),
        reaccion_ms = P(lambda x: x <= 190)
    ))
    def regla_mc_equilibrado(self):
        self._score("MC", 3.0,
            "R10 - Perfil físico equilibrado: vel. 7.5–9.0 m/s + saltos + reacción")

    @Rule(Jugador(
        salto_long_cm = P(lambda x: x >= 220),
        salto_alt_cm = P(lambda x: x >= 50),
        reaccion_ms = P(lambda x: x <= 185)
    ))
    def regla_mc_explosivo(self):
        self._score("MC", 1.5,
            "R11 - Explosividad muscular alta: ambos saltos superiores + reacción")
        



    # ============ BANDA (MD / MI) ==================
    @Rule(Jugador(
        velocidad_ms = P(lambda x: x >= 8.5),
        salto_long_cm = P(lambda x: x >= 225),
        reaccion_ms = P(lambda x: x <= 180)
    ))
    def regla_md(self):
        self._score("MD", 2.5,
            "R12 - Velocidad >=8.5 m/s + salto largo >=225 cm + reacción <=180 ms")

    @Rule(Jugador(
        velocidad_ms = P(lambda x: x >= 8.5),
        salto_long_cm = P(lambda x: x >= 225),
        reaccion_ms = P(lambda x: x <= 180)
    ))
    def regla_mi(self):
        self._score("MI", 2.5,
            "R13 - Perfil equivalente de banda izquierda")
        



    # ============ MEDIAPUNTA (MCO) ==================
    @Rule(Jugador(
        velocidad_ms = P(lambda x: x >= 8.0),
        reaccion_ms = P(lambda x: x <= 170), # reacción excelente
        potencia_tiro = P(lambda x: x >= 75)
    ))
    def regla_mco_1(self):
        self._score("MCO", 3.0,
            "R14 - Vel. >=8.0 m/s + reacción <=170 ms + potencia tiro >=75 km/h")

    @Rule(Jugador(
        reaccion_ms = P(lambda x: x <= 175),
        salto_long_cm = P(lambda x: x >= 218),
        potencia_tiro = P(lambda x: x >= 70)
    ))
    def regla_mco_2(self):
        self._score("MCO", 1.5,
            "R15 - Reacción <=175 ms + salto largo >=218 cm + tiro >=70 km/h")
        



    # ============ EXTREMO (ED / EI) ==================
    @Rule(Jugador(
        velocidad_ms = P(lambda x: x >= 9.0), # Muy rápido
        reaccion_ms = P(lambda x: x <= 170),
        salto_long_cm = P(lambda x: x >= 230)
    ))
    def regla_ed(self):
        self._score("ED", 3.5,
            "R16 - Velocidad >=9.0 m/s + reacción <=170 ms + salto largo >=230 cm")

    @Rule(Jugador(
        velocidad_ms = P(lambda x: x >= 9.0),
        reaccion_ms = P(lambda x: x <= 170),
        salto_long_cm = P(lambda x: x >= 230)
    ))
    def regla_ei(self):
        self._score("EI", 3.5,
            "R17 - Perfil equivalente de extremo izquierdo")

    @Rule(Jugador(
        velocidad_ms = P(lambda x: x >= 9.5) # Velocidad excepcional
    ))
    def regla_extremo_velocidad(self):
        self._score("EI", 1.5,
            "R18 - Velocidad excepcional ≥9.5 m/s (extremo natural)")
        self._score("ED", 1.5,
            "R18b - Ídem extremo derecho")
        



    # ============ DELANTERO CENTRO (DC) ==================
    @Rule(Jugador(
        potencia_tiro = P(lambda x: x >= 85), # Gran potencia de disparo
        salto_alt_cm = P(lambda x: x >= 55),
        altura_cm = P(lambda x: x >= 178)
    ))
    def regla_dc_1(self):
        self._score("DC", 3.0,
            "R19 - Potencia tiro >=85 km/h + salto vertical >=55 cm + altura >=178 cm")

    @Rule(Jugador(
        potencia_tiro = P(lambda x: x >= 78),
        velocidad_ms = P(lambda x: x >= 8.5)
    ))
    def regla_dc_2(self):
        self._score("DC", 2.0,
            "R20 - Tiro >=78 km/h + velocidad >=8.5 m/s (9 de área + velocidad)")

    @Rule(Jugador(
        altura_cm = P(lambda x: x >= 185),
        peso_kg = P(lambda x: x >= 78),
        salto_alt_cm = P(lambda x: x >= 52),
        potencia_tiro = P(lambda x: x >= 65)
    ))
    def regla_dc_3(self):
        self._score("DC", 1.5,
            "R21 - Delantero físico: altura >=185 + peso >=78 + salto >=52 + tiro")



    # FALLBACK
    @Rule(Jugador())
    # Si no se cumple ninguna de las reglas anteriores, esta regla se activará para asignar un perfil genérico de centrocampista
    def regla_fallback(self):
        self._score("MC", 0.5,
            "R22 - Regla por defecto: perfil genérico de centrocampista")



# CAPA DE USO
class SistemaExpertoFutbol:

    # Diccionario de descripciones para cada posición
    DESCRIPCIONES = {
        "POR": "Portero",
        "DFC": "Central",
        "LI": "Lateral Izquierdo",
        "LD": "Lateral Derecho",
        "MCD": "Mediocentro Defensivo",
        "MC": "Mediocentro",
        "MI": "Interior / Banda Izquierda",
        "MD": "Interior / Banda Derecha",
        "MCO": "Mediapunta",
        "EI": "Extremo Izquierdo",
        "ED": "Extremo Derecho",
        "DC": "Delantero Centro",
    }

    # Constructor
    def __init__(self):
        self.engine = SistemaPosiciones()

    # Método principal para analizar un jugador y obtener recomendaciones de posición
    def analizar_jugador(
        self,
        altura_cm: int,
        peso_kg: int,
        velocidad_ms: float,
        salto_long_cm: int,
        salto_alt_cm: int,
        reaccion_ms: int,
        potencia_tiro: int,
    ):
        self.engine = SistemaPosiciones() # Reinicia el motor para cada análisis
        self.engine.reset() # Limpia hechos y puntuaciones anteriores

        # Por aqui pasamos los datos del jugador para evaluarlos posteriomente con las reglas definidas en el motor
        self.engine.declare(Jugador(
            altura_cm = altura_cm,
            peso_kg = peso_kg,
            velocidad_ms = velocidad_ms,
            salto_long_cm = salto_long_cm,
            salto_alt_cm = salto_alt_cm,
            reaccion_ms = reaccion_ms,
            potencia_tiro = potencia_tiro,
        ))

        self.engine.run() # Ejecuta el motor para procesar las reglas y acumular puntuaciones

        # Genera un ranking de posiciones basado en las puntuaciones acumuladas por el motor
        ranking = sorted(
            self.engine.scores.items(), # Obtiene las posiciones y sus puntuaciones acumuladas
            key=lambda x: x[1], # Ordena por puntuación de mayor a menor
            reverse=True # Orden descendente para que la posición con mayor puntuación quede al principio
        )

        # Si no hay posiciones con puntuación, devolvemos None
        if not ranking:
            return None

        posicion_top, score_top = ranking[0] # La posición con la puntuación más alta es la recomendada
        total = sum(s for _, s in ranking) or 1 # Suma total de puntuaciones para calcular porcentajes, evita división por cero

        # Formatea el ranking para incluir nombre de posición, puntuación y porcentajes relativos
        ranking_formateado = [
            {
                "posicion": pos,
                "nombre": self.DESCRIPCIONES.get(pos, pos),
                "score": score,
                "confianza_relativa": round((score / score_top) * 100, 2) if score_top else 0,
                "peso_sobre_total": round((score / total) * 100, 2),
            }
            for pos, score in ranking if score > 0
        ]

        return { # Devuelve un diccionario con la posición recomendada, su nombre, puntuación y el ranking completo
            "posicion_recomendada": posicion_top,
            "nombre_posicion": self.DESCRIPCIONES.get(posicion_top, posicion_top),
            "score_top": score_top,
            "ranking": ranking_formateado,
            "reglas_activadas": self.engine.reglas_activadas,
        }