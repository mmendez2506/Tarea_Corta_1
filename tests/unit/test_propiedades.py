# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Christian Rivas y Jozafath Perez
# Descripción: Propiedades del juego en que se apoyan los agentes: no adyacencia y cota admisible.
# ==============================

import random

from generator.generate import generar
from tileup.engine.board import celdas_vacias, colocar, ocupadas, tablero_vacio, vecinos
from tileup.io.instance import parsear_instancia

def partidas(cantidad):
    for semilla in range(cantidad):
        rng = random.Random(semilla)
        n, k = rng.randint(2, 6), rng.randint(1, 6)
        instancia = parsear_instancia(generar(n, k, rng.randint(1, 4 * n * n), semilla))
        estado, historia = tablero_vacio(n), []
        for i, ficha in enumerate(instancia.fichas):
            vacias = celdas_vacias(estado)
            if not vacias:
                break
            historia.append((estado, i))
            estado = colocar(estado, n, ficha, rng.choice(vacias))
        historia.append((estado, len(historia)))
        yield instancia, historia

def test_nunca_hay_dos_vecinas_del_mismo_color():
    for instancia, historia in partidas(300):
        n = instancia.n
        for estado, _ in historia:
            for celda, ficha in enumerate(estado):
                if ficha is None:
                    continue
                for v in vecinos(n, celda):
                    assert estado[v] is None or estado[v][0] != ficha[0]

def test_cota_de_ocupadas_finales_es_admisible():
    revisados = 0
    for instancia, historia in partidas(400):
        final, colocadas = historia[-1]
        if colocadas < instancia.m:
            continue
        for estado, i in historia:
            restantes = instancia.fichas[i:]
            distintos = len({f[0] for f in estado if f} | {color for color, _ in restantes})
            cota = max(distintos, ocupadas(estado) - 3 * len(restantes))
            assert cota <= ocupadas(final)
            revisados += 1
    assert revisados > 1000
