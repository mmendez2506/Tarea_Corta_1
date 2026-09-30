# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Christian Rivas y Jozafath Perez
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
