# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Christian Rivas y Jozafath Perez
# Descripción: Pruebas de que las versiones incrementales de los agentes deciden lo mismo que la versión directa.
# ==============================

import random

import pytest

from generator.generate import generar
from tileup.agents.evolutionary import AgenteEvolutivo
from tileup.agents.search import AgenteBusqueda, _candidatos, _posiciones
from tileup.engine.board import colocar, tablero_vacio, vecinos
from tileup.io.instance import parsear_instancia

def decodificar_directo(instancia, genes):
    # Versión directa de la decodificación: en cada ficha recorre todo el tablero
    # y ordena todas las celdas vacías por (-s, b, l, c).
    n, fichas = instancia.n, instancia.fichas
    ultima = {}
    for j, (color, _) in enumerate(fichas):
        ultima[color] = j
    tablero = tablero_vacio(n)
    celdas = []
    for i, ficha in enumerate(fichas):
        color = ficha[0]
        candidatos = []
        for c, actual in enumerate(tablero):
            if actual is None:
                s = b = l = 0
                for v in vecinos(n, c):
                    vecino = tablero[v]
                    if vecino is None:
                        l += 1
                    elif vecino[0] == color:
                        s += 1
                    elif ultima[vecino[0]] > i:
                        b += 1
                candidatos.append((-s, b, l, c))
        if not candidatos:
            break
        candidatos.sort()
        celda = candidatos[min(genes[i], len(candidatos) - 1)][3]
        tablero = colocar(tablero, n, ficha, celda)
        celdas.append(celda)
    return tuple(celdas)

@pytest.mark.parametrize("n, k, m", [(1, 2, 3), (2, 3, 10), (4, 3, 40), (5, 8, 60), (8, 40, 192), (10, 100, 300)])
def test_decodificacion_incremental_igual_a_la_directa(n, k, m):
    rng = random.Random(n * 1000 + k)
    for semilla in range(3):
        instancia = parsear_instancia(generar(n, k, m, semilla))
        agente = AgenteEvolutivo(presupuesto=0)
        agente.resolver(instancia, 1, 60)
        for densidad in (0.0, 0.2, 0.8):
            genes = [rng.randrange(1, 6) if rng.random() < densidad else 0 for _ in range(m)]
            assert agente._evaluar(genes)[2] == decodificar_directo(instancia, genes)

def candidatos_directos(tablero, ocupadas, iguales, prioridad, bloqueo):
    # Todos los candidatos de un nodo, construidos y ordenados de una sola vez.
    total = len(prioridad)
    lista = []
    for c, ficha in enumerate(tablero):
        if ficha is not None:
            continue
        s = iguales.get(c, 0)
        if bloqueo is None:
            lista.append((ocupadas + 1 - s, 0, prioridad[c], c))
        else:
            vec, ultima, i, color = bloqueo
            b = sum(1 for v in vec[c] if tablero[v] is not None
                    and tablero[v][0] != color and ultima[tablero[v][0]] > i)
            lista.append((ocupadas + 1 - s, 0, b * total + prioridad[c], c))
    return sorted(lista)

@pytest.mark.parametrize("bloqueos", [False, True])
def test_candidatos_perezosos_en_el_mismo_orden_que_ordenar_todo(bloqueos):
    rng = random.Random(7)
    for _ in range(40):
        n = rng.randrange(2, 7)
        instancia = parsear_instancia(generar(n, rng.randrange(1, 9), 3 * n * n, rng.randrange(1000)))
        fichas = instancia.fichas
        i = rng.randrange(len(fichas))
        tablero = tablero_vacio(n)
        for ficha in fichas[:i]:
            vacias = [c for c, f in enumerate(tablero) if f is None]
            if not vacias:
                break
            tablero = colocar(tablero, n, ficha, rng.choice(vacias))
        if None not in tablero:
            continue
        color = fichas[i][0]
        vec = [tuple(vecinos(n, c)) for c in range(n * n)]
        iguales = {}
        for t in _posiciones(tablero).get(color, ()):
            for v in vec[t]:
                if tablero[v] is None:
                    iguales[v] = iguales.get(v, 0) + 1
        prioridad = list(range(n * n))
        rng.shuffle(prioridad)
        por_prioridad = sorted(range(n * n), key=prioridad.__getitem__)
        ultima = {}
        for j, (c, _) in enumerate(fichas):
            ultima[c] = j
        bloqueo = (vec, ultima, i, color) if bloqueos else None
        ocupadas = sum(f is not None for f in tablero)
        perezosos = list(_candidatos(tablero, ocupadas, 0, iguales, prioridad, por_prioridad, bloqueo))
        assert perezosos == candidatos_directos(tablero, ocupadas, iguales, prioridad, bloqueo)

def test_repetidos_comparan_colores_no_valores():
    agente = AgenteBusqueda()
    agente.resolver(parsear_instancia("2 2\n1\n1 1\n"), 1, 5)
    a = ((1, 3), None, None, (2, 1))
    b = ((1, 9), None, None, (2, 4))      # mismos colores, otros valores: mismo futuro
    c = ((2, 3), None, None, (1, 1))      # otros colores en las mismas celdas
    vistos = {}
    assert not agente._repetido(a, 123, vistos)
    assert agente._repetido(b, 123, vistos)
    assert not agente._repetido(c, 123, vistos)   # misma huella pero colores distintos

@pytest.mark.parametrize("opciones", [{"enfriamiento": 0.8}, {"sin_repetidos": True}])
def test_opciones_del_evolutivo_son_deterministas(opciones):
    instancia = parsear_instancia(generar(5, 16, 75, 4))
    a = AgenteEvolutivo(presupuesto=150, **opciones).resolver(instancia, 3, 60)
    b = AgenteEvolutivo(presupuesto=150, **opciones).resolver(instancia, 3, 60)
    assert a.colocaciones == b.colocaciones and a.esfuerzo == b.esfuerzo

@pytest.mark.parametrize("dobles", [0.0, 0.5])
def test_potencial_del_hijo_sin_construirlo_es_el_del_hijo_construido(dobles):
    rng = random.Random(11)
    for _ in range(150):
        n = rng.randrange(2, 7)
        instancia = parsear_instancia(generar(n, rng.randrange(1, 9), 3 * n * n, rng.randrange(1000)))
        fichas = instancia.fichas
        agente = AgenteBusqueda(peso_dobles=dobles, ventana=rng.choice([1, 3, 10]))
        agente.resolver(parsear_instancia("1 1\n0\n"), 1, 5)
        agente._n, agente._fichas = n, fichas
        agente._vecinos, agente._pesos = [tuple(vecinos(n, c)) for c in range(n * n)], None
        i = rng.randrange(len(fichas) - 1)
        tablero = tablero_vacio(n)
        for ficha in fichas[:i]:
            vacias = [c for c, f in enumerate(tablero) if f is None]
            if not vacias:
                break
            tablero = colocar(tablero, n, ficha, rng.choice(vacias))
        vacias = [c for c, f in enumerate(tablero) if f is None]
        if not vacias:
            continue
        posiciones = {color: frozenset(celdas) for color, celdas in _posiciones(tablero).items()}
        padre = (list(tablero), 0, None, posiciones, 0)
        ficha = fichas[i]
        cache = {}
        for celda in rng.sample(vacias, min(4, len(vacias))):
            absorbidas = [v for v in vecinos(n, celda)
                          if tablero[v] is not None and tablero[v][0] == ficha[0]]
            esperado = agente._potencial(colocar(tablero, n, ficha, celda), i + 1)
            obtenido = agente._potencial_hijo(padre, cache, celda, absorbidas, ficha[0],
                                              agente._pesos_desde(i + 1))
            assert obtenido == esperado
