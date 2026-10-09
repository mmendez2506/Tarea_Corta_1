# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Cristhian Rivas y Jozafath Perez
# Descripción: Pruebas unitarias de la expansión, la evaluación y la poda del agente de búsqueda.
# ==============================

from tileup.agents.search import AgenteBusqueda, _clave
from tileup.engine.board import tablero_vacio, vecinos
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

def resolver(n, k, fichas, semilla=1):
    instancia = Instancia(n=n, k=k, fichas=tuple(fichas))
    resultado = AgenteBusqueda().resolver(instancia, semilla, 5)
    return resultado, jugar(instancia, resultado.colocaciones)

def test_ejemplo_del_enunciado_es_optimo():
    instancia = parsear_instancia(EJEMPLO)
    resultado = AgenteBusqueda().resolver(instancia, 1, 5)
    partida = jugar(instancia, resultado.colocaciones)
    assert partida.resultado == "victoria"
    assert partida.ocupadas == 3

def test_prefiere_fusionar():
    _, partida = resolver(2, 2, [(1, 1), (2, 1), (1, 1)])
    assert partida.resultado == "victoria"
    assert partida.ocupadas == 2

def test_un_solo_color_termina_en_una_ficha():
    _, partida = resolver(3, 1, [(1, v) for v in range(1, 10)])
    assert partida.ocupadas == 1
    assert partida.mayor == sum(range(1, 10))

def test_derrota_devuelve_prefijo_legal():
    resultado, partida = resolver(1, 2, [(1, 1), (2, 1)])
    assert resultado.colocaciones == [(0, 0)]
    assert partida.resultado == "derrota"

def test_secuencia_vacia():
    resultado, partida = resolver(2, 1, [])
    assert resultado.colocaciones == []
    assert partida.resultado == "victoria"

def test_parada_al_alcanzar_la_cota():
    resultado, partida = resolver(3, 2, [(1, 1), (2, 1)] * 6)
    assert partida.ocupadas == 2
    assert resultado.esfuerzo == 12

def test_potencial_cuenta_celdas_libres_del_color_siguiente():
    agente = AgenteBusqueda(ventana=1)
    agente._vecinos = [tuple(vecinos(3, c)) for c in range(9)]
    tablero = list(tablero_vacio(3))
    tablero[4] = (1, 5)
    tablero = tuple(tablero)
    agente._fichas = ((1, 1), (1, 1))
    assert agente._potencial(tablero, 1) == 2
    agente._fichas = ((1, 1), (2, 1))
    assert agente._potencial(tablero, 1) == 0
    assert agente._potencial(tablero, 2) == 0

def test_orden_de_soluciones_sigue_al_concurso():
    assert _clave((5, 9, ())) > _clave((4, 1, ()))
    assert _clave((5, 2, ())) > _clave((5, 3, ()))
