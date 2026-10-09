# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Cristhian Rivas y Jozafath Perez
# Descripción: Pruebas de reproducibilidad y parámetros del generador.
# ==============================

import pytest
from generator.generate import generar
from tileup.io.instance import parsear_instancia

def test_generacion_reproducible():
    a = generar(3, 4, 20, 17)
    assert a == generar(3, 4, 20, 17)
    assert a != generar(3, 4, 20, 18)
    i = parsear_instancia(a)
    assert (i.n, i.k, i.m) == (3, 4, 20)
    assert all(1 <= c <= 4 and 1 <= v <= 9 for c, v in i.fichas)

@pytest.mark.parametrize('args', [(0,1,1,0),(1,0,1,0),(1,1,-1,0),(1,1,1,0,0)])
def test_parametros_invalidos(args):
    with pytest.raises(ValueError):
        generar(*args)
