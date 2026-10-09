# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Cristhian Rivas y Jozafath Perez
# Descripción: Pruebas del agente de búsqueda: determinismo, límite de tiempo y presupuesto.
# ==============================

import time

import pytest

from generator.generate import generar
from tileup.agents.search import AgenteBusqueda
from tileup.engine.game import jugar
from tileup.io.instance import parsear_instancia
from tileup.main import main
from validator.validate import validar

def instancia(n, k, m, semilla):
    return parsear_instancia(generar(n, k, m, semilla))

@pytest.mark.parametrize("n, k, m, semilla", [(3, 3, 25, 42), (4, 5, 48, 1), (3, 9, 27, 2)])
def test_cli_search_y_validador(tmp_path, capsys, n, k, m, semilla):
    entrada, salida = tmp_path / "inst.txt", tmp_path / "sol.txt"
    entrada.write_text(generar(n, k, m, semilla), encoding="utf-8")
    codigo = main(["--instancia", str(entrada), "--agente", "search",
                   "--semilla", "1", "--limite", "5", "--salida", str(salida)])
    assert codigo == 0
    partida = validar(entrada, salida)
    stdout = capsys.readouterr().out
    assert f"colocadas={partida.colocadas}/{m}" in stdout
    assert f"ocupadas={partida.ocupadas}" in stdout
    assert f"mayor={partida.mayor}" in stdout
    assert f"resultado={partida.resultado}" in stdout
    assert "(nodos)" in stdout

def test_misma_semilla_misma_solucion():
    inst = instancia(3, 9, 27, 1)
    a = AgenteBusqueda().resolver(inst, 7, 10)
    b = AgenteBusqueda().resolver(inst, 7, 10)
    assert a.colocaciones == b.colocaciones
    assert a.esfuerzo == b.esfuerzo

def test_respeta_limite_de_tiempo():
    inst = instancia(8, 40, 192, 1)
    limite = 1.0
    inicio = time.perf_counter()
    resultado = AgenteBusqueda(presupuesto=10**9).resolver(inst, 1, limite)
    assert time.perf_counter() - inicio < limite
    jugar(inst, resultado.colocaciones)

def test_limite_minusculo_devuelve_prefijo_legal():
    inst = instancia(6, 25, 108, 2)
    resultado = AgenteBusqueda().resolver(inst, 1, 1e-6)
    partida = jugar(inst, resultado.colocaciones)
    assert partida.colocadas == len(resultado.colocaciones) <= inst.m

def test_presupuesto_de_nodos_acota_el_esfuerzo():
    inst = instancia(4, 14, 48, 1)
    resultado = AgenteBusqueda(presupuesto=10).resolver(inst, 1, 10)
    assert resultado.esfuerzo <= 10
    jugar(inst, resultado.colocaciones)
