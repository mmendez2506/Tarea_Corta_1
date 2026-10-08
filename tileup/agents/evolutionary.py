# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Christian Rivas y Jozafath Perez
# Descripción: Agente evolutivo: algoritmo genético con genes de rango por ficha.
# ==============================

import heapq
import random
import time

from tileup.agents.base import Agente, Resultado
from tileup.engine.board import colocar, posicion, tablero_vacio, vecinos as vecinos_de

class AgenteEvolutivo(Agente):
    nombre = "evolutionary"
    unidad_esfuerzo = "evaluaciones"

    def __init__(self, poblacion: int = 40, torneo: int = 3, prob_cruce: float = 0.9,
                 genes_mutados: float = 4.0, prob_rango: float = 0.3,
                 densidad_inicial: float = 0.3, elite: int = 2, ventana: int = 10,
                 presupuesto: int | None = None, ritmo: float = 100_000, margen: float = 0.9):
        self.poblacion = poblacion
        self.torneo = torneo
        self.prob_cruce = prob_cruce
        self.genes_mutados = genes_mutados
        self.prob_rango = prob_rango
        self.densidad_inicial = densidad_inicial
        self.elite = elite
        self.ventana = ventana
        self.presupuesto = presupuesto
        self.ritmo = ritmo
        self.margen = margen

    def resolver(self, instancia, semilla, limite_s):
        self._fin = time.perf_counter() + limite_s * self.margen
        self._n = n = instancia.n
        self._fichas = instancia.fichas
        self._vecinos = [tuple(vecinos_de(n, celda)) for celda in range(n * n)]
        self._proximos = [
            frozenset(color for color, _ in instancia.fichas[i + 1:i + 1 + self.ventana])
            for i in range(instancia.m)
        ]
        self._evaluaciones = 0
        self._presupuesto = self.presupuesto
        if self._presupuesto is None:
            # cada evaluación simula la partida completa: el costo crece como N³
            self._presupuesto = max(1, int(self.ritmo * limite_s / n ** 3))
        m = instancia.m
        rng = random.Random(semilla)
        cota = len({color for color, _ in instancia.fichas})

        mejor = None
        poblacion = []
        for numero in range(self.poblacion):
            if self._agotado():
                break
            densidad = 0.0 if numero == 0 else self.densidad_inicial
            genes = [self._rango(rng) if rng.random() < densidad else 0 for _ in range(m)]
            individuo = self._evaluar(genes)
            poblacion.append(individuo)
            mejor = _mejor(mejor, individuo)

        tasa = self.genes_mutados / m if m else 0.0
        while poblacion and not self._agotado() and not _optimo(mejor, m, cota):
            poblacion.sort(key=lambda individuo: -individuo[0])
            nueva = poblacion[:self.elite]
            while len(nueva) < self.poblacion and not self._agotado():
                padre = self._seleccionar(poblacion, rng)
                if rng.random() < self.prob_cruce:
                    genes = _cruzar(padre[1], self._seleccionar(poblacion, rng)[1], rng)
                else:
                    genes = list(padre[1])
                for i in range(m):
                    if rng.random() < tasa:
                        genes[i] = self._rango(rng)
                hijo = self._evaluar(genes)
                nueva.append(hijo)
                mejor = _mejor(mejor, hijo)
            poblacion = nueva

        colocaciones = [] if mejor is None else [posicion(n, c) for c in mejor[2]]
        return Resultado(colocaciones=colocaciones, esfuerzo=self._evaluaciones)

    def _agotado(self):
        return (self._evaluaciones >= self._presupuesto
                or time.perf_counter() >= self._fin)

    def _rango(self, rng):
        rango = 0
        while rng.random() < self.prob_rango and rango < self._n * self._n:
            rango += 1
        return rango

    def _seleccionar(self, poblacion, rng):
        return max((rng.choice(poblacion) for _ in range(self.torneo)),
                   key=lambda individuo: individuo[0])

    def _evaluar(self, genes):
        self._evaluaciones += 1
        n, vecinos = self._n, self._vecinos
        tablero = tablero_vacio(n)
        celdas = []
        for i, ficha in enumerate(self._fichas):
            # una evaluación simula la partida completa: se corta si vence el plazo
            if i % 16 == 0 and time.perf_counter() >= self._fin:
                break
            color = ficha[0]
            proximos = self._proximos[i]
            candidatos = []
            for celda, actual in enumerate(tablero):
                if actual is None:
                    iguales = bloqueados = libres = 0
                    for v in vecinos[celda]:
                        vecino = tablero[v]
                        if vecino is None:
                            libres += 1
                        elif vecino[0] == color:
                            iguales += 1
                        elif vecino[0] in proximos:
                            bloqueados += 1
                    candidatos.append((-iguales, bloqueados, libres, celda))
            if not candidatos:
                break
            rango = min(genes[i], len(candidatos) - 1)
            if rango == 0:
                celda = min(candidatos)[-1]
            else:
                celda = heapq.nsmallest(rango + 1, candidatos)[-1][-1]
            tablero = colocar(tablero, n, ficha, celda)
            celdas.append(celda)
        ocupadas = sum(1 for actual in tablero if actual is not None)
        aptitud = len(celdas) * (n * n + 1) - ocupadas
        return (aptitud, genes, tuple(celdas), ocupadas)

def _cruzar(a, b, rng):
    if len(a) < 2:
        return list(a)
    i, j = sorted(rng.sample(range(len(a) + 1), 2))
    return list(a[:i]) + list(b[i:j]) + list(a[j:])

def _mejor(actual, candidato):
    if actual is None or candidato[0] > actual[0]:
        return candidato
    return actual

def _optimo(mejor, m, cota):
    return mejor is not None and len(mejor[2]) == m and mejor[3] <= cota
