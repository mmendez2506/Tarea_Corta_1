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

def test_camino_rapido_lee_igual_que_argparse():
    from tileup.main import construir_parser, leer_argumentos
    for argv in (["--instancia", "a.txt", "--agente", "search"],
                 ["--agente", "evolutionary", "--instancia", "b.txt", "--semilla", "-7",
                  "--limite", "2.5", "--salida", "s.txt"],
                 ["--instancia", "a.txt", "--agente", "trivial", "--semilla", "3", "--semilla", "4"]):
        rapido, completo = vars(leer_argumentos(argv)), vars(construir_parser().parse_args(argv))
        assert rapido == completo

def test_formas_no_habituales_pasan_por_argparse():
    import pytest
    from tileup.main import leer_argumentos
    assert leer_argumentos(["--instancia=a.txt", "--agente", "search"]).instancia == "a.txt"
    for argv in (["--instancia", "a.txt", "--agente", "otro"],
                 ["--instancia", "a.txt", "--agente", "search", "--semilla", "1.5"],
                 ["--agente", "search"]):
        with pytest.raises(SystemExit):
            leer_argumentos(argv)
