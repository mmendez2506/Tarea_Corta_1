# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Cristhian Rivas y Jozafath Perez
# Descripción: Agente evolutivo: algoritmo genético con genes de rango por ficha.
# ==============================

import bisect
import random
import time

from tileup.agents.base import Agente, Resultado, plazo
from tileup.engine.board import colocar_en, posicion, tabla_vecinos, tablero_vacio

class AgenteEvolutivo(Agente):
    nombre = "evolutionary"
    unidad_esfuerzo = "evaluaciones"

    def __init__(self, poblacion: int = 40, torneo: int = 3, prob_cruce: float = 0.9,
                 genes_mutados: float = 4.0, prob_rango: float = 0.3,
                 densidad_inicial: float = 0.3, elite: int = 2, enfriamiento: float = 0.0,
                 sin_repetidos: bool = False, presupuesto: int | None = None,
                 ritmo: float = 180_000, margen: float = 0.9):
        self.poblacion = poblacion
        self.torneo = torneo
        self.prob_cruce = prob_cruce
        self.genes_mutados = genes_mutados
        self.prob_rango = prob_rango
        self.densidad_inicial = densidad_inicial
        self.elite = elite
        self.enfriamiento = enfriamiento
        self.sin_repetidos = sin_repetidos
        self.presupuesto = presupuesto
        self.ritmo = ritmo
        self.margen = margen

    def resolver(self, instancia, semilla, limite_s):
        self._fin = plazo(limite_s, self.margen, instancia.m)
        self._n = n = instancia.n
        self._fichas = instancia.fichas
        self._vecinos = tabla_vecinos(n)
        # última aparición de cada color: después de la ficha i, un color
        # vuelve a salir si su última aparición es posterior a i
        self._ultima = {}
        for j, (color, _) in enumerate(instancia.fichas):
            self._ultima[color] = j
        self._evaluaciones = 0
        self._presupuesto = self.presupuesto
        if self._presupuesto is None:
            # Cada evaluación simula M colocaciones, y con la evaluación incremental
            # cada colocación cuesta aproximadamente proporcional a √N (medido).
            costo = max(1, instancia.m) * n ** 0.5
            self._presupuesto = max(1, int(self.ritmo * limite_s / costo))
        m = instancia.m
        rng = random.Random(semilla)
        cota = len({color for color, _ in instancia.fichas})

        mejor = None
        poblacion = []
        vistos = set()
        for numero in range(self.poblacion):
            if self._agotado():
                break
            densidad = 0.0 if numero == 0 else self.densidad_inicial
            genes = [self._rango(rng) if rng.random() < densidad else 0 for _ in range(m)]
            if self.sin_repetidos:
                vistos.add(tuple(genes))
            individuo = self._evaluar(genes)
            poblacion.append(individuo)
            mejor = _mejor(mejor, individuo)
            if _optimo(mejor, m, cota):
                break

        while poblacion and not self._agotado() and not _optimo(mejor, m, cota):
            poblacion.sort(key=lambda individuo: -individuo[0])
            nueva = poblacion[:self.elite]
            # Enfriamiento: la mutación empieza en (1 + e) veces la base y baja hasta
            # (1 - e) veces según la fracción del presupuesto usada (explorar primero,
            # afinar después). Depende de las evaluaciones, no del reloj.
            avance = min(1.0, self._evaluaciones / self._presupuesto)
            factor = 1 + self.enfriamiento * (1 - 2 * avance)
            tasa = self.genes_mutados * factor / m
            while len(nueva) < self.poblacion and not self._agotado():
                padre = self._seleccionar(poblacion, rng)
                if rng.random() < self.prob_cruce:
                    genes = _cruzar(padre[1], self._seleccionar(poblacion, rng)[1], rng)
                else:
                    genes = list(padre[1])
                for i in range(m):
                    if rng.random() < tasa:
                        genes[i] = self._rango(rng)
                if self.sin_repetidos:
                    # un genoma ya evaluado repetiría la misma partida: se muta un gen más
                    intentos = 0
                    while tuple(genes) in vistos and intentos < 10:
                        genes[rng.randrange(m)] = self._rango(rng) + 1
                        intentos += 1
                    vistos.add(tuple(genes))
                hijo = self._evaluar(genes)
                nueva.append(hijo)
                mejor = _mejor(mejor, hijo)
                # nadie puede superar la cota: se para en cuanto se alcanza
                if _optimo(mejor, m, cota):
                    break
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
        # Decodifica los genes en una partida. Para la ficha i, cada celda vacía c
        # tiene la clave (-s, b, l, c): s vecinos del color de la ficha, b vecinos
        # de otro color que vuelve a salir y l vecinos vacíos. El gen elige la
        # posición de la celda en ese orden.
        #
        # Evaluación incremental: en lugar de recorrer el tablero en cada ficha,
        # se lleva para cada celda vacía l (libres) y el total de vecinos de un
        # color que todavía sale (pend), y se agrupan en cubetas por (pend, l).
        # Solo se recalculan las celdas cercanas a lo que cambió.
        self._evaluaciones += 1
        n, vecinos, ultima = self._n, self._vecinos, self._ultima
        # La partida se simula sobre una lista propia con colocar_en (las reglas del
        # motor), sin copiar el tablero en cada ficha. Nunca se toca un estado ajeno.
        tablero = list(tablero_vacio(n))
        celdas = []
        libres = [len(v) for v in vecinos]
        pend = [0] * (n * n)
        cubetas = [[] for _ in range(25)]           # cubeta pend * 5 + l
        cubeta_de = libres[:]                        # -1 si la celda está ocupada
        for celda in range(n * n):
            cubetas[cubeta_de[celda]].append(celda)
        posiciones = {}                              # color -> celdas con ese color
        vacias = n * n
        for i, ficha in enumerate(self._fichas):
            # una evaluación simula la partida completa: se corta si vence el plazo
            if i % 16 == 0 and time.perf_counter() >= self._fin:
                break
            if not vacias:
                break
            color = ficha[0]
            # Como nunca hay dos vecinas del mismo color, las celdas que fusionan
            # son las vacías junto a fichas de este color: van primero (s > 0).
            iguales = {}
            for t in posiciones.get(color, ()):
                for v in vecinos[t]:
                    if tablero[v] is None:
                        iguales[v] = iguales.get(v, 0) + 1
            rango = min(genes[i], vacias - 1)
            if rango < len(iguales):
                # pend cuenta también los vecinos de este color: b = pend - s
                claves = [(-s, pend[c] - s, libres[c], c) for c, s in iguales.items()]
                celda = (min(claves) if rango == 0 else sorted(claves)[rango])[3]
            else:
                celda = _en_cubetas(cubetas, iguales, rango - len(iguales))

            grupo = colocar_en(tablero, n, ficha, celda)
            # como no hay vecinas del mismo color, el grupo es la celda y las absorbidas
            absorbidas = grupo - {celda}
            celdas.append(celda)
            propias = posiciones.setdefault(color, set())
            propias.difference_update(absorbidas)
            propias.add(celda)
            vacias += len(absorbidas) - 1

            tocadas = {celda, *absorbidas}
            for c in (celda, *absorbidas):
                tocadas.update(vecinos[c])
            if ultima[color] == i:
                # el color ya no vuelve a salir: deja de contar en pend
                for t in propias:
                    tocadas.update(vecinos[t])
            for c in tocadas:
                if tablero[c] is None:
                    l = p = 0
                    for v in vecinos[c]:
                        vecino = tablero[v]
                        if vecino is None:
                            l += 1
                        elif ultima[vecino[0]] > i:
                            p += 1
                    libres[c], pend[c] = l, p
                    nueva = p * 5 + l
                else:
                    nueva = -1
                anterior = cubeta_de[c]
                if nueva != anterior:
                    if anterior >= 0:
                        lista = cubetas[anterior]
                        del lista[bisect.bisect_left(lista, c)]
                    if nueva >= 0:
                        bisect.insort(cubetas[nueva], c)
                    cubeta_de[c] = nueva
        ocupadas = n * n - vacias
        aptitud = len(celdas) * (n * n + 1) - ocupadas
        return (aptitud, genes, tuple(celdas), ocupadas)

def _en_cubetas(cubetas, excluidas, k):
    # k-ésima celda (desde 0) en el orden (pend, l, c), saltando las excluidas
    for lista in cubetas:
        for celda in lista:
            if celda in excluidas:
                continue
            if k == 0:
                return celda
            k -= 1
    raise ValueError("no hay suficientes celdas vacías")

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
