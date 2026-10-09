# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Cristhian Rivas y Jozafath Perez
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


def test_cli_informa_tiempo_total_de_la_ejecucion(tmp_path, capsys):
    # tiempo_total_s mide toda la ejecución (lectura, agente, verificación y
    # escritura), así que nunca puede ser menor que el tiempo del agente.
    instancia = tmp_path / "inst.txt"
    instancia.write_text("3 2\n4\n1 1\n2 1\n1 1\n2 1\n", encoding="utf-8")
    assert main(["--instancia", str(instancia), "--agente", "search",
                 "--salida", str(tmp_path / "sol.txt")]) == 0
    metricas = dict(linea.split("=", 1) for linea in capsys.readouterr().out.splitlines())
    assert float(metricas["tiempo_total_s"]) >= float(metricas["tiempo_s"])


def test_plazo_descuenta_el_tiempo_ya_usado():
    # Con el origen fijado en el pasado, el plazo vence antes que si se cuenta
    # desde ahora; sin origen, cuenta desde que se llama.
    import time
    from tileup.agents.base import fijar_origen, plazo
    ahora = time.perf_counter()
    fijar_origen(ahora - 5)
    try:
        con_origen = plazo(10, 0.9, 0)
    finally:
        fijar_origen(None)
    sin_origen = plazo(10, 0.9, 0)
    assert con_origen < sin_origen - 4
