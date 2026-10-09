# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Cristhian Rivas y Jozafath Perez
# Descripción: Prueba del ensayo del concurso con una instancia pequeña.
# ==============================

import csv

from experiments.ensayo import main

def test_ensayo_corre_ambos_agentes_y_recomienda(tmp_path, capsys):
    assert main(["--n", "3", "--k", "2", "--m", "12", "--limite", "2",
                 "--semillas", "1", "--salida", str(tmp_path)]) == 0
    filas = list(csv.DictReader((tmp_path / "resultados.csv").open(encoding="utf-8")))
    assert {f["agente"] for f in filas} == {"search", "evolutionary"}
    assert all(f["estado"] == "victoria" for f in filas)
    assert "Agente recomendado para el concurso" in capsys.readouterr().out
