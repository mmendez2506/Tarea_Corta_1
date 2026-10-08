# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Christian Rivas y Jozafath Perez
# Descripción: Agente de búsqueda en haz iterativa con poda por cota admisible.
# ==============================

import random
import time

from tileup.agents.base import Agente, Resultado
from tileup.engine.board import colocar, posicion, tablero_vacio, vecinos as vecinos_de

class AgenteBusqueda(Agente):
    nombre = "search"
    unidad_esfuerzo = "nodos"

    def __init__(self, ancho_max: int = 1024, presupuesto: int | None = None,
                 ritmo: float = 60_000, ventana: int = 10, tope: int = 2, peso_dobles: float = 0.0,
                 alfa: float = 0.0, simetrias: bool = False, margen: float = 0.9):
        self.ancho_max = ancho_max
        self.presupuesto = presupuesto
        self.ritmo = ritmo
        self.ventana = ventana
        self.tope = tope
        self.peso_dobles = peso_dobles
        self.alfa = alfa
        self.simetrias = simetrias
        self.margen = margen

    def resolver(self, instancia, semilla, limite_s):
        self._fin = time.perf_counter() + limite_s * self.margen
        self._n = n = instancia.n
        self._fichas = fichas = instancia.fichas
        self._vecinos = [tuple(vecinos_de(n, celda)) for celda in range(n * n)]
        self._expandidos = 0
        # Presupuesto determinista: depende solo del límite y de N, no del reloj.
        self._presupuesto = self.presupuesto
        if self._presupuesto is None:
            self._presupuesto = int(self.ritmo * limite_s / n)
        self._transformaciones = _simetrias(n) if self.simetrias else ()

        prioridad = list(range(n * n))
        random.Random(semilla).shuffle(prioridad)
        self._prioridad = prioridad

        # colores de las fichas restantes desde cada índice
        resto = [frozenset()] * (instancia.m + 1)
        for i in range(instancia.m - 1, -1, -1):
            resto[i] = resto[i + 1] | {fichas[i][0]}
        self._resto = resto
        cota_raiz = len(resto[0])

        mejor = (0, 0, ())
        ancho = 1
        while True:
            victoria = mejor[1] if mejor[0] == instancia.m else None
            solucion, cortado = self._haz(ancho, victoria)
            if _clave(solucion) > _clave(mejor):
                mejor = solucion
            if cortado or ancho >= self.ancho_max:
                break
            if mejor[0] == instancia.m and mejor[1] <= cota_raiz:
                break
            ancho *= 2

        return Resultado(colocaciones=list(mejor[2]), esfuerzo=self._expandidos)

    def _agotado(self):
        return self._expandidos >= self._presupuesto or time.perf_counter() >= self._fin

    def _haz(self, ancho, victoria):
        n, fichas, vecinos, prioridad = self._n, self._fichas, self._vecinos, self._prioridad
        m = len(fichas)
        haz = [(tablero_vacio(n), 0, ())]
        mejor = (0, 0, ())

        for i in range(m):
            color = fichas[i][0]
            candidatos = []
            for orden, (tablero, ocupadas, _) in enumerate(haz):
                if self._agotado():
                    return mejor, True
                self._expandidos += 1
                for celda, ficha in enumerate(tablero):
                    if ficha is not None:
                        continue
                    iguales = 0
                    for v in vecinos[celda]:
                        if tablero[v] is not None and tablero[v][0] == color:
                            iguales += 1
                    candidatos.append((ocupadas + 1 - iguales, orden, prioridad[celda], celda))
            if not candidatos:
                break

            candidatos.sort()
            resto = self._resto[i + 1]
            restantes = m - i - 1
            siguiente = []
            vistos = set()
            for numero, (ocupadas, orden, _, celda) in enumerate(candidatos):
                if len(siguiente) >= ancho * 4:
                    break
                if numero % 64 == 63 and time.perf_counter() >= self._fin:
                    return mejor, True
                tablero, _, colocaciones = haz[orden]
                hijo = colocar(tablero, n, fichas[i], celda)
                llave = tuple(0 if f is None else f[0] for f in hijo)
                unica = llave
                if self._transformaciones:
                    unica = min(tuple(llave[c] for c in t) for t in self._transformaciones)
                if unica in vistos:
                    continue
                vistos.add(unica)
                if victoria is not None:
                    distintos = len(resto.union(llave) - {0})
                    if max(distintos, ocupadas - 3 * restantes) >= victoria:
                        continue
                potencial = self._potencial(hijo, i + 1)
                if self.alfa:
                    clave = (ocupadas - self.alfa * potencial, 0)
                else:
                    clave = (ocupadas, -potencial)
                siguiente.append((
                    *clave, len(siguiente), ocupadas, hijo, colocaciones + (posicion(n, celda),),
                ))
            if not siguiente:
                break

            siguiente.sort(key=lambda nodo: nodo[:3])
            haz = [(hijo, ocupadas, colocaciones)
                   for _, _, _, ocupadas, hijo, colocaciones in siguiente[:ancho]]
            mejor = min(((i + 1, ocupadas, colocaciones) for _, ocupadas, colocaciones in haz),
                        key=lambda solucion: solucion[1])

        return mejor, False

    def _potencial(self, tablero, desde):
        proximas = self._fichas[desde:desde + self.ventana]
        if not proximas:
            return 0.0
        contactos = {color: {} for color, _ in proximas}
        for celda, ficha in enumerate(tablero):
            if ficha is not None and ficha[0] in contactos:
                cuenta = contactos[ficha[0]]
                for v in self._vecinos[celda]:
                    if tablero[v] is None:
                        cuenta[v] = cuenta.get(v, 0) + 1
        total = 0.0
        peso = 1.0
        for color, _ in proximas:
            cuenta = contactos[color]
            termino = min(len(cuenta), self.tope)
            if self.peso_dobles:
                termino += self.peso_dobles * sum(1 for c in cuenta.values() if c >= 2)
            total += peso * termino
            peso /= 2
        return total

def _clave(solucion):
    colocadas, ocupadas, _ = solucion
    return (colocadas, -ocupadas)

def _simetrias(n):
    def girar(p):
        return tuple(p[(n - 1 - c) * n + f] for f in range(n) for c in range(n))
    def reflejar(p):
        return tuple(p[f * n + (n - 1 - c)] for f in range(n) for c in range(n))
    base = tuple(range(n * n))
    resultado = []
    p = base
    for _ in range(4):
        resultado.extend([p, reflejar(p)])
        p = girar(p)
    return tuple(resultado)
