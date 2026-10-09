# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Cristhian Rivas y Jozafath Perez
# Descripción: Agente de búsqueda en haz iterativa con poda por cota admisible.
# ==============================

import heapq
import random
import time

from tileup.agents.base import Agente, Resultado, plazo
from tileup.engine.board import colocar, colocar_en, posicion, tabla_vecinos, tablero_vacio

class AgenteBusqueda(Agente):
    nombre = "search"
    unidad_esfuerzo = "nodos"

    def __init__(self, ancho_max: int = 1024, presupuesto: int | None = None,
                 ritmo: float = 60_000, ventana: int = 10, tope: int = 2, peso_dobles: float = 0.0,
                 alfa: float = 0.0, simetrias: bool = False, evitar_bloqueos: bool = True,
                 margen: float = 0.9):
        self.ancho_max = ancho_max
        self.presupuesto = presupuesto
        self.ritmo = ritmo
        self.ventana = ventana
        self.tope = tope
        self.peso_dobles = peso_dobles
        self.alfa = alfa
        self.simetrias = simetrias
        self.evitar_bloqueos = evitar_bloqueos
        self.margen = margen
        self._pesos = None

    def resolver(self, instancia, semilla, limite_s):
        self._fin = plazo(limite_s, self.margen, instancia.m)
        self._n = n = instancia.n
        self._fichas = fichas = instancia.fichas
        self._vecinos = tabla_vecinos(n)
        self._expandidos = 0
        # Presupuesto determinista: depende solo del límite y de N, no del reloj.
        self._presupuesto = self.presupuesto
        if self._presupuesto is None:
            # al menos una pasada voraz completa (M nodos) si el tiempo alcanza
            self._presupuesto = max(instancia.m, int(self.ritmo * limite_s / n))
        self._transformaciones = _simetrias(n) if self.simetrias else ()

        prioridad = list(range(n * n))
        random.Random(semilla).shuffle(prioridad)
        self._prioridad = prioridad
        # las celdas en orden de prioridad, para recorrer las vacías sin ordenar
        self._por_prioridad = sorted(range(n * n), key=prioridad.__getitem__)
        # números de Zobrist, creados a medida que aparecen pares (celda, color)
        self._zobrist = {}
        self._azar_zobrist = random.Random(n)

        # colores de las fichas restantes desde cada índice
        resto = [frozenset()] * (instancia.m + 1)
        for i in range(instancia.m - 1, -1, -1):
            resto[i] = resto[i + 1] | {fichas[i][0]}
        self._resto = resto
        cota_raiz = len(resto[0])
        # última aparición de cada color: un color "vuelve" después de la ficha i
        # si su última aparición es posterior a i
        self._ultima = {}
        for j, (color, _) in enumerate(fichas):
            self._ultima[color] = j
        # pesos del potencial por color, calculados una vez por índice de ficha
        self._pesos = [None] * (instancia.m + 1)

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

    def _z(self, celda, color):
        # número aleatorio de 64 bits para la ficha de ese color en esa celda
        llave = (celda, color)
        numero = self._zobrist.get(llave)
        if numero is None:
            numero = self._zobrist[llave] = self._azar_zobrist.getrandbits(64)
        return numero

    def _haz(self, ancho, victoria):
        # Un nodo es (tablero, ocupadas, camino, posiciones, huella):
        # - tablero: lista propia del nodo; solo cambia con colocar_en (reglas del motor);
        # - camino: lista enlazada (celda, camino del padre) con las colocaciones;
        # - posiciones: color -> celdas con fichas de ese color;
        # - huella: XOR de los números de Zobrist de sus fichas (colores y celdas).
        n, fichas, vecinos, prioridad = self._n, self._fichas, self._vecinos, self._prioridad
        por_prioridad = self._por_prioridad
        m = len(fichas)
        haz = [(list(tablero_vacio(n)), 0, None, {}, 0)]
        mejor = (0, 0, None)

        for i in range(m):
            ficha = fichas[i]
            color = ficha[0]
            flujos = []
            for orden, (tablero, ocupadas, _, posiciones, _) in enumerate(haz):
                if self._agotado():
                    return _solucion(mejor, n), True
                self._expandidos += 1
                # Nunca hay dos vecinas del mismo color: las celdas que fusionan son
                # las vacías junto a fichas de este color.
                iguales = {}
                for t in posiciones.get(color, ()):
                    for v in vecinos[t]:
                        if tablero[v] is None:
                            iguales[v] = iguales.get(v, 0) + 1
                if ocupadas < n * n:
                    bloqueo = (vecinos, self._ultima, i, color) if self.evitar_bloqueos else None
                    flujos.append(_candidatos(tablero, ocupadas, orden, iguales,
                                              prioridad, por_prioridad, bloqueo))
            if not flujos:
                break

            resto = self._resto[i + 1]
            restantes = m - i - 1
            hijos = []
            vistos = {}
            colores_hijo = {}
            z = self._z
            # Con un solo padre no puede haber dos hijos con los mismos colores: cada
            # uno deja la ficha en una celda distinta. Con ancho 1 no se buscan repetidos.
            buscar_repetidos = ancho > 1
            # El haz se ordena primero por ocupadas (salvo con alfa) y los candidatos
            # llegan en ese orden: en cuanto ya hay `ancho` hijos y el candidato deja
            # más ocupadas que el último de ellos, ni él ni los siguientes pueden entrar.
            cortar = not self.alfa
            # heapq.merge recorre los candidatos de todos los nodos en el mismo orden
            # que sorted(candidatos), pero solo genera los que se llegan a usar.
            candidatos = flujos[0] if len(flujos) == 1 else heapq.merge(*flujos)
            for numero, (ocupadas, orden, _, celda) in enumerate(candidatos):
                if len(hijos) >= ancho * 4:
                    break
                if cortar and len(hijos) >= ancho and ocupadas > hijos[ancho - 1][0]:
                    break
                if numero % 64 == 63 and time.perf_counter() >= self._fin:
                    return _solucion(mejor, n), True
                # Un hijo se evalúa sin construirlo: basta saber dónde cae la ficha y
                # qué fichas absorbe. Solo se construyen los que entran al haz.
                padre = haz[orden]
                tablero, posiciones, huella = padre[0], padre[3], padre[4]
                absorbidas = [v for v in vecinos[celda]
                              if tablero[v] is not None and tablero[v][0] == color]
                huella_hijo = 0
                if buscar_repetidos:
                    huella_hijo = huella ^ z(celda, color)
                    for v in absorbidas:
                        huella_hijo ^= z(v, color)
                    if self._repetido_hijo(padre, celda, ficha, huella_hijo, vistos):
                        continue
                if victoria is not None:
                    # los colores del hijo son los del padre más el de la ficha: igual
                    # para todos los hijos de un padre, así que se calcula una vez
                    distintos = colores_hijo.get(orden)
                    if distintos is None:
                        distintos = colores_hijo[orden] = len(resto.union(posiciones, (color,)))
                    if max(distintos, ocupadas - 3 * restantes) >= victoria:
                        continue
                hijos.append((ocupadas, orden, celda, absorbidas, huella_hijo))
            if not hijos:
                break

            # El potencial solo desempata hijos con las mismas ocupadas: si un hijo es
            # el único con sus ocupadas, su lugar en el orden no depende de él.
            repetidas = {}
            for ocupadas, *_ in hijos:
                repetidas[ocupadas] = repetidas.get(ocupadas, 0) + 1
            contactos = {}
            pesos = self._pesos_desde(i + 1)
            siguiente = []
            for numero, (ocupadas, orden, celda, absorbidas, huella_hijo) in enumerate(hijos):
                if self.alfa or repetidas[ocupadas] > 1:
                    potencial = self._potencial_hijo(haz[orden], contactos.setdefault(orden, {}),
                                                     celda, absorbidas, color, pesos)
                else:
                    potencial = 0.0
                if self.alfa:
                    clave = (ocupadas - self.alfa * potencial, 0)
                else:
                    clave = (ocupadas, -potencial)
                siguiente.append((*clave, numero, ocupadas, orden, celda, absorbidas, huella_hijo))
            siguiente.sort(key=lambda nodo: nodo[:3])
            elegidos = siguiente[:ancho]

            # Se construyen solo los elegidos. El último elegido de cada padre se queda
            # con el tablero y las posiciones del padre (que ya no se usan) y los
            # modifica en el lugar; los demás trabajan sobre una copia.
            pendientes = {}
            for nodo in elegidos:
                pendientes[nodo[4]] = pendientes.get(nodo[4], 0) + 1
            nuevo = []
            for _, _, _, ocupadas, orden, celda, absorbidas, huella_hijo in elegidos:
                tablero, _, camino, posiciones, _ = haz[orden]
                propias = posiciones.get(color, frozenset())
                pendientes[orden] -= 1
                if pendientes[orden]:
                    tablero, posiciones = list(tablero), dict(posiciones)
                colocar_en(tablero, n, ficha, celda)
                posiciones[color] = propias.difference(absorbidas) | {celda}
                nuevo.append((tablero, ocupadas, (celda, camino), posiciones, huella_hijo))
            haz = nuevo
            mejor = min(((i + 1, ocupadas, camino) for _, ocupadas, camino, _, _ in haz),
                        key=lambda solucion: solucion[1])

        return _solucion(mejor, n), False

    def _repetido_hijo(self, padre, celda, ficha, huella, vistos):
        # Como _repetido, pero sin construir el hijo salvo que haga falta comparar:
        # con simetrías siempre, y si no, solo cuando dos huellas coinciden.
        n = self._n
        if self._transformaciones:
            return self._repetido(colocar(padre[0], n, ficha, celda), huella, vistos)
        previos = vistos.setdefault(huella, [])
        construido = None
        if previos:
            construido = colocar(padre[0], n, ficha, celda)
            for previo in previos:
                if previo[2] is None:
                    previo[2] = colocar(previo[0][0], n, ficha, previo[1])
                if _mismos_colores(construido, previo[2]):
                    return True
        previos.append([padre, celda, construido])
        return False

    def _repetido(self, hijo, huella, vistos):
        # Dos tableros con los mismos colores en las mismas celdas tienen el mismo
        # futuro. La huella de Zobrist los agrupa y se confirma comparando colores.
        if self._transformaciones:
            llave = tuple([0 if f is None else f[0] for f in hijo])
            unica = min(tuple(llave[c] for c in t) for t in self._transformaciones)
            if unica in vistos:
                return True
            vistos[unica] = None
            return False
        previos = vistos.setdefault(huella, [])
        if any(_mismos_colores(hijo, otro) for otro in previos):
            return True
        previos.append(hijo)
        return False

    def _potencial(self, tablero, desde, posiciones=None):
        # Celdas vacías junto a fichas de los colores de las próximas fichas, con
        # peso 1, 1/2, 1/4, … según la distancia. Los pesos de un mismo color se
        # suman una vez por color; como son potencias de 2, el total es exacto.
        pesos = self._pesos_desde(desde)
        if not pesos:
            return 0.0
        if posiciones is None:
            posiciones = _posiciones(tablero)
        vecinos, tope, dobles = self._vecinos, self.tope, self.peso_dobles
        total = 0.0
        for color, peso in pesos:
            cuenta = {}
            for t in posiciones.get(color, ()):
                for v in vecinos[t]:
                    if tablero[v] is None:
                        cuenta[v] = cuenta.get(v, 0) + 1
                if not dobles and len(cuenta) >= tope:
                    break
            termino = min(len(cuenta), tope)
            if dobles:
                termino += dobles * sum(1 for c in cuenta.values() if c >= 2)
            total += peso * termino
        return total

    def _contactos(self, tablero, posiciones, color):
        # celdas vacías vecinas de fichas de ese color -> cuántas fichas de ese color tocan
        cuenta = {}
        for t in posiciones.get(color, ()):
            for v in self._vecinos[t]:
                if tablero[v] is None:
                    cuenta[v] = cuenta.get(v, 0) + 1
        return cuenta

    def _potencial_hijo(self, padre, cache, celda, absorbidas, color, pesos):
        # El mismo valor que _potencial sobre el hijo, calculado desde el padre sin
        # construir el hijo. `pesos` son los de las fichas que siguen. Para cada color
        # próximo d:
        # - si d no es el color colocado, sus fichas no cambian: respecto de los
        #   contactos del padre (calculados una vez y guardados en `cache`) se pierde
        #   la celda que se ocupa y se ganan las absorbidas que tocan fichas de d;
        # - si d es el color colocado, sus fichas son las del padre sin las
        #   absorbidas, más la celda, y se cuentan directamente.
        if not pesos:
            return 0.0
        tablero, posiciones = padre[0], padre[3]
        vecinos, tope, dobles = self._vecinos, self.tope, self.peso_dobles
        total = 0.0
        for d, peso in pesos:
            if d == color:
                # absorbidas tiene a lo sumo 4 celdas: buscar en la lista es barato
                cuenta = {}
                for t in posiciones.get(d, ()):
                    if t not in absorbidas:
                        for v in vecinos[t]:
                            if v != celda and (tablero[v] is None or v in absorbidas):
                                cuenta[v] = cuenta.get(v, 0) + 1
                for v in vecinos[celda]:
                    if tablero[v] is None or v in absorbidas:
                        cuenta[v] = cuenta.get(v, 0) + 1
                largo = len(cuenta)
                dobles_d = sum(1 for c in cuenta.values() if c >= 2) if dobles else 0
            else:
                cuenta = cache.get(d)
                if cuenta is None:
                    cuenta = cache[d] = self._contactos(tablero, posiciones, d)
                largo = len(cuenta) - (celda in cuenta)
                dobles_d = 0
                if dobles:
                    dobles_d = (sum(1 for c in cuenta.values() if c >= 2)
                                - (cuenta.get(celda, 0) >= 2))
                for a in absorbidas:
                    toca = 0
                    for v in vecinos[a]:
                        f = tablero[v]
                        if f is not None and f[0] == d:
                            toca += 1
                    largo += toca > 0
                    dobles_d += toca >= 2
            termino = largo if largo < tope else tope
            if dobles:
                termino += dobles * dobles_d
            total += peso * termino
        return total

    def _pesos_desde(self, desde):
        if self._pesos is not None and self._pesos[desde] is not None:
            return self._pesos[desde]
        acumulado = {}
        peso = 1.0
        for color, _ in self._fichas[desde:desde + self.ventana]:
            acumulado[color] = acumulado.get(color, 0.0) + peso
            peso /= 2
        pesos = tuple(acumulado.items())
        if self._pesos is not None:
            self._pesos[desde] = pesos
        return pesos

def _candidatos(tablero, ocupadas, orden, iguales, prioridad, por_prioridad, bloqueo):
    # Candidatos de un nodo, ya en orden (ocupadas tras colocar, orden, desempate, celda):
    # primero las celdas que fusionan y luego las demás vacías.
    if bloqueo is None:
        # desempate por el orden aleatorio de la semilla
        yield from sorted((ocupadas + 1 - s, orden, prioridad[c], c) for c, s in iguales.items())
        for c in por_prioridad:
            if tablero[c] is None and c not in iguales:
                yield (ocupadas + 1, orden, prioridad[c], c)
        return
    # Desempate por bloqueos: primero las celdas que tapan menos fichas de colores
    # que vuelven a salir (b), y a igual b, el orden de la semilla.
    vecinos, ultima, i, color = bloqueo
    total = len(prioridad)

    def tapadas(c):
        b = 0
        for v in vecinos[c]:
            f = tablero[v]
            if f is not None and f[0] != color and ultima[f[0]] > i:
                b += 1
        return b

    yield from sorted((ocupadas + 1 - s, orden, tapadas(c) * total + prioridad[c], c)
                      for c, s in iguales.items())
    # Las que no tapan nada salen en cuanto aparecen; las demás esperan su turno.
    demoradas = [[] for _ in range(5)]
    for c in por_prioridad:
        if tablero[c] is None and c not in iguales:
            b = tapadas(c)
            if b == 0:
                yield (ocupadas + 1, orden, prioridad[c], c)
            else:
                demoradas[b].append(c)
    for b in range(1, 5):
        for c in demoradas[b]:
            yield (ocupadas + 1, orden, b * total + prioridad[c], c)

def _posiciones(tablero):
    posiciones = {}
    for celda, ficha in enumerate(tablero):
        if ficha is not None:
            posiciones.setdefault(ficha[0], set()).add(celda)
    return posiciones

def _mismos_colores(a, b):
    return all((x is None) == (y is None) and (x is None or x[0] == y[0])
               for x, y in zip(a, b))

def _solucion(mejor, n):
    colocadas, ocupadas, camino = mejor
    celdas = []
    while camino is not None:
        celda, camino = camino
        celdas.append(posicion(n, celda))
    celdas.reverse()
    return (colocadas, ocupadas, tuple(celdas))

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
