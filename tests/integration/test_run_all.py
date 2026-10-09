# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Cristhian Rivas y Jozafath Perez
# Descripción: Prueba de la batería experimental: carpetas, M fijo, CSV y validación.
# ==============================

import csv

from experiments.run_all import ejecutar

def test_bateria_con_carpetas_propias_y_m_fijo(tmp_path):
    instancias, soluciones = tmp_path / "inst", tmp_path / "sol"
    codigo = ejecutar(tmp_path / "res", ["trivial"], [1, 2, 3], [1, 2, 3], [1, 2, 3],
                      1, 3, instancias, soluciones, m_fijo=5)
    assert codigo == 0
    assert len(list(instancias.glob("*_m5_*.txt"))) == 27
    assert len(list(soluciones.glob("*_trivial.txt"))) == 27
    with (tmp_path / "res" / "resumen.csv").open(encoding="utf-8") as archivo:
        filas = list(csv.DictReader(archivo))
    assert len(filas) == 9
    assert all(fila["fallos"] == "0" and fila["m"] == "5" for fila in filas)
    assert (tmp_path / "res" / "tiempos.svg").exists()
