# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Cristhian Rivas y Jozafath Perez
# Descripción: Pruebas unitarias de la decodificación, la aptitud y los operadores del agente evolutivo.
# ==============================

import random

from tileup.agents.evolutionary import AgenteEvolutivo, _cruzar, _mejor
from tileup.engine.game import jugar
from tileup.io.instance import Instancia, parsear_instancia

EJEMPLO = """4 3
6
1 2
2 1
1 3
3 1
1 1
2 4
"""

def preparar(n, k, fichas):
    instancia = Instancia(n=n, k=k, fichas=tuple(fichas))
    agente = AgenteEvolutivo(presupuesto=0)
    agente.resolver(instancia, 1, 5)
    return instancia, agente

def test_ejemplo_del_enunciado_es_optimo():
    instancia = parsear_instancia(EJEMPLO)
    resultado = AgenteEvolutivo().resolver(instancia, 1, 5)
    partida = jugar(instancia, resultado.colocaciones)
    assert partida.resultado == "victoria"
    assert partida.ocupadas == 3

def test_gen_cero_fusiona_con_su_color():
    instancia, agente = preparar(2, 2, [(1, 1), (2, 1), (1, 1)])
    aptitud, _, celdas, ocupadas = agente._evaluar([0, 0, 0])
    assert len(celdas) == 3 and ocupadas == 2
    assert aptitud == 3 * 5 - 2

def test_rango_mayor_que_las_celdas_vacias_es_legal():
    instancia, agente = preparar(2, 3, [(1, 1), (2, 1), (3, 1)])
    _, _, celdas, _ = agente._evaluar([99, 99, 99])
    assert len(set(celdas)) == 3

def test_decodificacion_detiene_en_derrota():
    instancia, agente = preparar(1, 2, [(1, 1), (2, 1)])
    aptitud, _, celdas, ocupadas = agente._evaluar([0, 0])
    assert celdas == (0,) and ocupadas == 1
    assert aptitud == 1 * 2 - 1

def test_aptitud_prefiere_colocar_mas_fichas():
    _, lleno = preparar(2, 4, [(1, 1), (2, 1), (3, 1), (4, 1)])
    _, despejado = preparar(2, 1, [(1, 1)] * 3)
    cuatro_fichas_tablero_lleno = lleno._evaluar([0] * 4)
    tres_fichas_una_ocupada = despejado._evaluar([0] * 3)
    assert cuatro_fichas_tablero_lleno[3] == 4 and tres_fichas_una_ocupada[3] == 1
    assert cuatro_fichas_tablero_lleno[0] > tres_fichas_una_ocupada[0]

def test_cruce_de_dos_puntos():
    rng = random.Random(3)
    a, b = [0] * 10, [1] * 10
    hijo = _cruzar(a, b, rng)
    assert len(hijo) == 10 and set(hijo) <= {0, 1}
    assert a == [0] * 10 and b == [1] * 10

def test_mejor_conserva_el_de_mayor_aptitud():
    x, y = (5, [], (), 0), (7, [], (), 0)
    assert _mejor(None, x) is x
    assert _mejor(x, y) is y
    assert _mejor(y, x) is y

def test_secuencia_vacia():
    resultado = AgenteEvolutivo().resolver(Instancia(n=2, k=1, fichas=()), 1, 5)
    assert resultado.colocaciones == []
