# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Christian Rivas y Jozafath Perez
# Descripción: Agente de referencia para comprobar el motor y el flujo de ejecución.
# ==============================

from tileup.agents.base import Agente, Resultado
import time
from tileup.engine.board import celdas_vacias, colocar, posicion, tablero_vacio

class PrimeraLibre(Agente):
    nombre = "trivial"
    unidad_esfuerzo = "colocaciones"

    def resolver(self, instancia, semilla, limite_s):
        n = instancia.n
        estado = tablero_vacio(n)
        colocaciones = []
        fin = time.perf_counter() + limite_s
        for ficha in instancia.fichas:
            if time.perf_counter() >= fin:
                break
            vacias = celdas_vacias(estado)
            if not vacias:
                break
            celda = vacias[0]
            estado = colocar(estado, n, ficha, celda)
            colocaciones.append(posicion(n, celda))
        return Resultado(colocaciones=colocaciones, esfuerzo=len(colocaciones))
