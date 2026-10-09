# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Cristhian Rivas y Jozafath Perez
# Descripción: Pruebas de aceptación y rechazo del árbitro independiente.
# ==============================

import pytest
from validator.validate import ValidacionInvalida, validar_textos

INST = '2 2\n3\n1 2\n2 1\n1 3\n'

def test_fusion_y_resumen():
    r = validar_textos(INST, '0 0 0\n1 1 1\n2 0 1\n# colocadas=3 ocupadas=2 mayor=5\n')
    assert (r.colocadas, r.ocupadas, r.mayor, r.resultado) == (3, 2, 5, 'victoria')

@pytest.mark.parametrize('sol', [
    '', '0 0 0',
    '1 0 0\n# colocadas=1 ocupadas=1 mayor=2',
    '0 0 2\n# colocadas=1 ocupadas=1 mayor=2',
    '0 1 -1\n# colocadas=1 ocupadas=1 mayor=2',
    '0 0 0\n1 0 0\n# colocadas=2 ocupadas=2 mayor=2',
    '0 x 0\n# colocadas=1 ocupadas=1 mayor=2',
    '0 0 0 9\n# colocadas=1 ocupadas=1 mayor=2',
    '0 0 0\n# colocadas=1 ocupadas=1 mayor=999',
    '# colocadas=0 ocupadas=0 mayor=0\n0 0 0',
])
def test_rechaza_ilegal(sol):
    with pytest.raises(ValidacionInvalida):
        validar_textos(INST, sol)

def test_derrota_y_movimiento_posterior():
    inst = '1 2\n2\n1 1\n2 1'
    assert validar_textos(inst, '0 0 0\n# colocadas=1 ocupadas=1 mayor=1').resultado == 'derrota'
    with pytest.raises(ValidacionInvalida):
        validar_textos(inst, '0 0 0\n1 0 0\n# colocadas=2 ocupadas=1 mayor=2')

def test_victoria_y_movimiento_posterior():
    with pytest.raises(ValidacionInvalida):
        validar_textos('2 1\n1\n1 1', '0 0 0\n1 0 1\n# colocadas=2 ocupadas=1 mayor=2')

def test_prefijo_y_vacia():
    assert validar_textos(INST, '# colocadas=0 ocupadas=0 mayor=0').resultado == 'incompleta'
    assert validar_textos('1 1\n0', '# colocadas=0 ocupadas=0 mayor=0').resultado == 'victoria'

def test_componente_y_diagonal():
    inst = '3 1\n3\n1 1\n1 2\n1 4'
    assert validar_textos(inst, '0 0 0\n1 0 2\n2 0 1\n# colocadas=3 ocupadas=1 mayor=7').mayor == 7
    assert validar_textos('2 1\n2\n1 1\n1 2', '0 0 0\n1 1 1\n# colocadas=2 ocupadas=2 mayor=2').ocupadas == 2

@pytest.mark.parametrize('inst', ['', '0 1\n0', '2 0\n0', '2 1\n-1', '2 1\n1\n2 1', '2 1\n1\n1 0', '2 1\n2\n1 1'])
def test_instancia_invalida(inst):
    with pytest.raises(ValidacionInvalida):
        validar_textos(inst, '# colocadas=0 ocupadas=0 mayor=0')


# Ejemplo exacto del enunciado (sección 3): instancia con comentarios al final de
# la línea y la solución publicada, que debe aceptarse con las métricas del PDF.
INSTANCIA_ENUNCIADO = """# TileUp -- instancia de ejemplo
4 3           # tablero 4x4, 3 colores
6             # 6 fichas en la secuencia

1 2
2 1
1 3
3 1
1 1
2 4
"""

SOLUCION_ENUNCIADO = """0 0 0
1 1 1
2 0 1
3 2 2
4 0 2
5 1 2
# colocadas=6 ocupadas=3 mayor=6
"""

def test_acepta_la_solucion_del_enunciado():
    r = validar_textos(INSTANCIA_ENUNCIADO, SOLUCION_ENUNCIADO)
    assert (r.colocadas, r.ocupadas, r.mayor, r.resultado) == (6, 3, 6, 'victoria')

@pytest.mark.parametrize('cambio', [
    ('5 1 2', '5 0 2'),                                   # celda ya ocupada
    ('# colocadas=6 ocupadas=3 mayor=6', '# colocadas=6 ocupadas=4 mayor=6'),  # resumen falso
    ('3 2 2', '4 2 2'),                                   # índice fuera de orden
    ('5 1 2', '5 1 4'),                                   # columna fuera del tablero
])
def test_rechaza_variantes_ilegales_del_enunciado(cambio):
    viejo, nuevo = cambio
    with pytest.raises(ValidacionInvalida):
        validar_textos(INSTANCIA_ENUNCIADO, SOLUCION_ENUNCIADO.replace(viejo, nuevo))
