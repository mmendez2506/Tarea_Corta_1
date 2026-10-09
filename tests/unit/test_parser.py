# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Cristhian Rivas y Jozafath Perez
# Descripción: Pruebas del formato y las restricciones de las instancias.
# ==============================

import pytest

from tileup.io.instance import InstanciaInvalida, leer_instancia, parsear_instancia

def test_lee_el_formato_con_comentarios():
    texto = "# comentario\n\n4 3 # tablero\n2 # fichas\n1 2\n\n3 5\n"
    instancia = parsear_instancia(texto)
    assert (instancia.n, instancia.k, instancia.m) == (4, 3, 2)
    assert instancia.fichas == ((1, 2), (3, 5))

def test_secuencia_vacia_es_valida():
    assert parsear_instancia("3 2\n0\n").m == 0

@pytest.mark.parametrize(
    "texto",
    [
        "",
        "4 3\n",
        "4\n1\n1 1\n",
        "4 x\n1\n1 1\n",
        "0 3\n1\n1 1\n",
        "4 3\n3\n1 1\n2 2\n",
        "4 3\n1\n1 1\n2 2\n",
        "4 3\n1\n4 1\n",
        "4 3\n1\n1 0\n",
        "4 3\n1\n1 1 1\n",
    ],
)
def test_archivos_mal_formados(texto):
    with pytest.raises(InstanciaInvalida):
        parsear_instancia(texto)

def test_archivo_inexistente(tmp_path):
    with pytest.raises(InstanciaInvalida):
        leer_instancia(str(tmp_path / "no_existe.txt"))
