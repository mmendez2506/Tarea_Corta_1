# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Christian Rivas y Jozafath Perez
# Descripción: Pruebas del punto de entrada y el manejo de errores de instancia.
# ==============================

from tileup.main import main

def test_cli_escribe_la_solucion(tmp_path, capsys):
    instancia = tmp_path / "inst.txt"
    instancia.write_text("2 1\n3\n1 1\n1 1\n1 1\n", encoding="utf-8")
    salida = tmp_path / "sol.txt"
    codigo = main(["--instancia", str(instancia), "--agente", "trivial", "--salida", str(salida)])
    assert codigo == 0
    assert salida.read_text(encoding="utf-8").splitlines()[-1].startswith("# colocadas=3")
    assert "resultado=victoria" in capsys.readouterr().out

def test_cli_instancia_mal_formada_devuelve_error(tmp_path, capsys):
    instancia = tmp_path / "mala.txt"
    instancia.write_text("esto no es una instancia\n", encoding="utf-8")
    codigo = main(["--instancia", str(instancia), "--agente", "trivial"])
    assert codigo != 0
    assert "error en la instancia" in capsys.readouterr().err
