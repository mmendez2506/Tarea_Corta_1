# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Cristhian Rivas y Jozafath Perez
# Descripción: Partida: reproduce movimientos y determina victoria, derrota o partida incompleta.
# ==============================

from collections import namedtuple

from tileup.engine.board import (
    Estado,
    colocar_en,
    ficha_mayor,
    indice,
    ocupadas,
    tablero_vacio,
)
from tileup.io.instance import Instancia

VICTORIA = "victoria"
DERROTA = "derrota"
INCOMPLETA = "incompleta"

# estado final, fichas colocadas, celdas ocupadas, valor de la ficha mayor y resultado
ResultadoPartida = namedtuple("ResultadoPartida", "estado colocadas ocupadas mayor resultado")

def terminada(instancia: Instancia, estado: Estado, colocadas: int) -> str | None:

    if colocadas == instancia.m:
        return VICTORIA
    if None not in estado:
        return DERROTA
    return None

def jugar(instancia: Instancia, colocaciones) -> ResultadoPartida:
    # Reproduce la partida sobre una sola lista, sin copiar el tablero en cada
    # jugada, y lleva la cuenta de celdas vacías para detectar la derrota.
    n = instancia.n
    tablero = list(tablero_vacio(n))
    vacias = n * n
    colocadas = 0
    for fila, col in colocaciones:
        if colocadas == instancia.m or vacias == 0:
            raise ValueError("hay más colocaciones de las que admite la partida")
        grupo = colocar_en(tablero, n, instancia.fichas[colocadas], indice(n, fila, col))
        vacias += len(grupo) - 2 if len(grupo) >= 2 else -1
        colocadas += 1

    estado = tuple(tablero)
    resultado = terminada(instancia, estado, colocadas) or INCOMPLETA
    return ResultadoPartida(
        estado=estado,
        colocadas=colocadas,
        ocupadas=ocupadas(estado),
        mayor=ficha_mayor(estado),
        resultado=resultado,
    )
