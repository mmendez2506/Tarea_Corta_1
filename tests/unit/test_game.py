# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Cristhian Rivas y Jozafath Perez
# Descripción: Pruebas de victoria, derrota, partida incompleta y coordenadas inválidas.
# ==============================

import pytest

from tileup.engine.game import DERROTA, INCOMPLETA, VICTORIA, jugar
from tileup.io.instance import Instancia, parsear_instancia
from tileup.engine.board import MovimientoInvalido

@pytest.mark.parametrize('pos', [(0, 2), (1, -1), (-1, 2), (2, 0)])
def test_coordenadas_invalidas(pos):
    with pytest.raises(MovimientoInvalido):
        jugar(Instancia(2, 1, ((1, 1),)), [pos])

EJEMPLO = """
4 3
6
1 2
2 1
1 3
3 1
1 1
2 4
"""

def test_ejemplo_del_enunciado():
    instancia = parsear_instancia(EJEMPLO)
    colocaciones = [(0, 0), (1, 1), (0, 1), (2, 2), (0, 2), (1, 2)]
    partida = jugar(instancia, colocaciones)
    assert partida.resultado == VICTORIA
    assert partida.colocadas == 6
    assert partida.ocupadas == 3
    assert partida.mayor == 6

def test_deteccion_de_derrota():

    instancia = Instancia(n=2, k=2, fichas=((1, 1), (2, 1), (2, 1), (1, 1), (1, 1)))
    partida = jugar(instancia, [(0, 0), (0, 1), (1, 0), (1, 1)])
    assert partida.resultado == DERROTA
    assert partida.colocadas == 4
    assert partida.ocupadas == 4

def test_tablero_lleno_en_la_ultima_ficha_es_victoria():
    instancia = Instancia(n=1, k=1, fichas=((1, 1),))
    assert jugar(instancia, [(0, 0)]).resultado == VICTORIA

def test_partida_incompleta():
    instancia = Instancia(n=2, k=1, fichas=((1, 1), (1, 1)))
    assert jugar(instancia, [(0, 0)]).resultado == INCOMPLETA

def test_colocacion_despues_de_derrota_falla():
    instancia = Instancia(n=1, k=2, fichas=((1, 1), (2, 1)))
    with pytest.raises(ValueError):
        jugar(instancia, [(0, 0), (0, 0)])
