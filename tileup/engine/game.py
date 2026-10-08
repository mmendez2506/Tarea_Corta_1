# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Christian Rivas y Jozafath Perez
# Descripción: Partida: reproduce movimientos y determina victoria, derrota o partida incompleta.
# ==============================

from dataclasses import dataclass

from tileup.engine.board import (
    Estado,
    celdas_vacias,
    colocar,
    ficha_mayor,
    indice,
    ocupadas,
    tablero_vacio,
)
from tileup.io.instance import Instancia

VICTORIA = "victoria"
DERROTA = "derrota"
INCOMPLETA = "incompleta"

@dataclass
class ResultadoPartida:
    estado: Estado
    colocadas: int
    ocupadas: int
    mayor: int
    resultado: str

def terminada(instancia: Instancia, estado: Estado, colocadas: int) -> str | None:

    if colocadas == instancia.m:
        return VICTORIA
    if not celdas_vacias(estado):
        return DERROTA
    return None

def jugar(instancia: Instancia, colocaciones) -> ResultadoPartida:

    n = instancia.n
    estado = tablero_vacio(n)
    colocadas = 0
    for fila, col in colocaciones:
        if terminada(instancia, estado, colocadas) is not None:
            raise ValueError("hay más colocaciones de las que admite la partida")
        estado = colocar(estado, n, instancia.fichas[colocadas], indice(n, fila, col))
        colocadas += 1

    resultado = terminada(instancia, estado, colocadas) or INCOMPLETA
    return ResultadoPartida(
        estado=estado,
        colocadas=colocadas,
        ocupadas=ocupadas(estado),
        mayor=ficha_mayor(estado),
        resultado=resultado,
    )
