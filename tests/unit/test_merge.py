# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Christian Rivas y Jozafath Perez
# Descripción: Pruebas de colocación, componentes conexas y conservación de valores.
# ==============================

import pytest

from tileup.engine.board import (
    MovimientoInvalido,
    colocar,
    ficha_mayor,
    indice,
    ocupadas,
    tablero_vacio,
)

N = 3

def poner(estado, ficha, fila, col):
    return colocar(estado, N, ficha, indice(N, fila, col))

def test_colocacion_sin_fusion():
    estado = poner(tablero_vacio(N), (1, 5), 1, 1)
    assert estado[indice(N, 1, 1)] == (1, 5)
    assert ocupadas(estado) == 1

def test_colores_distintos_no_se_fusionan():
    estado = poner(tablero_vacio(N), (1, 2), 0, 0)
    estado = poner(estado, (2, 3), 0, 1)
    assert ocupadas(estado) == 2

def test_diagonal_no_se_fusiona():
    estado = poner(tablero_vacio(N), (1, 2), 0, 0)
    estado = poner(estado, (1, 3), 1, 1)
    assert ocupadas(estado) == 2

def test_fusion_de_dos_fichas():
    estado = poner(tablero_vacio(N), (1, 2), 0, 0)
    estado = poner(estado, (1, 3), 0, 1)
    assert estado[indice(N, 0, 1)] == (1, 5)
    assert estado[indice(N, 0, 0)] is None
    assert ocupadas(estado) == 1

def test_fusion_de_componente_de_tres_o_mas():

    estado = poner(tablero_vacio(N), (1, 1), 0, 0)
    estado = poner(estado, (1, 2), 0, 2)
    estado = poner(estado, (1, 4), 0, 1)
    assert estado[indice(N, 0, 1)] == (1, 7)
    assert ocupadas(estado) == 1

def test_fusion_toma_la_componente_completa():

    estado = tablero_vacio(N)
    for fila, col in [(2, 0), (2, 2)]:
        estado = poner(estado, (1, 1), fila, col)
    estado = poner(estado, (2, 9), 1, 1)
    estado = poner(estado, (1, 1), 2, 1)
    assert estado[indice(N, 2, 1)] == (1, 3)
    assert estado[indice(N, 1, 1)] == (2, 9)
    assert ocupadas(estado) == 2

def test_fusion_conserva_la_suma():
    estado = poner(tablero_vacio(N), (1, 4), 1, 0)
    estado = poner(estado, (1, 6), 1, 2)
    estado = poner(estado, (1, 10), 1, 1)
    assert ficha_mayor(estado) == 20

def test_fusion_no_modifica_el_estado_original():
    antes = poner(tablero_vacio(N), (1, 2), 0, 0)
    poner(antes, (1, 3), 0, 1)
    assert antes[indice(N, 0, 0)] == (1, 2)

def test_colocar_en_celda_ocupada_falla():
    estado = poner(tablero_vacio(N), (1, 2), 0, 0)
    with pytest.raises(MovimientoInvalido):
        poner(estado, (2, 1), 0, 0)

def test_colocar_fuera_del_tablero_falla():
    with pytest.raises(MovimientoInvalido):
        colocar(tablero_vacio(N), N, (1, 1), N * N)
