# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Christian Rivas y Jozafath Perez
# Descripción: Pruebas del flujo completo y comparación entre motor y árbitro.
# ==============================

import random
from generator.generate import generar
from tileup.main import main
from tileup.io.instance import parsear_instancia
from tileup.engine.game import jugar, terminada
from tileup.engine.board import tablero_vacio, celdas_vacias, colocar, posicion
from validator.validate import validar, validar_textos

def test_cli_validador(tmp_path, capsys):
    entrada, salida = tmp_path / 'inst.txt', tmp_path / 'sol.txt'
    entrada.write_text(generar(3, 3, 25, 42), encoding='utf-8')
    assert main(['--instancia', str(entrada), '--agente', 'trivial', '--semilla', '1', '--salida', str(salida)]) == 0
    r = validar(entrada, salida)
    stdout = capsys.readouterr().out
    for clave in ('colocadas', 'ocupadas', 'mayor'):
        assert f'{clave}={getattr(r, clave)}' in stdout

def test_motor_y_arbitro_coinciden_en_partidas():

    for seed in range(30):
        texto = generar(3, 3, 30, seed)
        inst = parsear_instancia(texto)
        estado, moves = tablero_vacio(3), []
        rng = random.Random(seed)
        for ficha in inst.fichas:
            if terminada(inst, estado, len(moves)):
                break
            celda = rng.choice(celdas_vacias(estado))
            estado = colocar(estado, 3, ficha, celda)
            moves.append(posicion(3, celda))
        p = jugar(inst, moves)
        sol = '\n'.join(f'{i} {r} {c}' for i, (r,c) in enumerate(moves))
        sol += f'\n# colocadas={p.colocadas} ocupadas={p.ocupadas} mayor={p.mayor}\n'
        v = validar_textos(texto, sol)
        assert (v.colocadas, v.ocupadas, v.mayor, v.resultado) == (p.colocadas, p.ocupadas, p.mayor, p.resultado)
