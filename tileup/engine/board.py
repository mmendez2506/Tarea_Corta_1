# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Christian Rivas y Jozafath Perez
# Descripción: Motor del tablero: posiciones, vecinos, colocación y fusión de fichas.
# ==============================

from collections import deque

Ficha = tuple[int, int]
Estado = tuple

class MovimientoInvalido(ValueError):
    pass

def tablero_vacio(n: int) -> Estado:
    return (None,) * (n * n)

def indice(n: int, fila: int, col: int) -> int:
    if not (0 <= fila < n and 0 <= col < n):
        raise MovimientoInvalido(f"la posición ({fila}, {col}) está fuera del tablero")
    return fila * n + col

def posicion(n: int, celda: int) -> tuple[int, int]:

    return divmod(celda, n)

def celdas_vacias(estado: Estado) -> list[int]:
    return [i for i, c in enumerate(estado) if c is None]

def ocupadas(estado: Estado) -> int:
    return sum(1 for c in estado if c is not None)

def ficha_mayor(estado: Estado) -> int:

    return max((c[1] for c in estado if c is not None), default=0)

def vecinos(n: int, celda: int):

    fila, col = divmod(celda, n)
    if fila > 0:
        yield celda - n
    if fila < n - 1:
        yield celda + n
    if col > 0:
        yield celda - 1
    if col < n - 1:
        yield celda + 1

_tablas_vecinos = {}

def tabla_vecinos(n: int) -> list[tuple[int, ...]]:
    # Los vecinos de cada celda de un tablero de lado n, calculados una sola vez.
    tabla = _tablas_vecinos.get(n)
    if tabla is None:
        tabla = _tablas_vecinos[n] = [tuple(vecinos(n, celda)) for celda in range(n * n)]
    return tabla

def componente(estado, n: int, celda: int, color: int) -> set[int]:

    tabla = tabla_vecinos(n)
    visitadas = {celda}
    cola = deque([celda])
    while cola:
        actual = cola.popleft()
        for v in tabla[actual]:
            ficha = estado[v]
            if v not in visitadas and ficha is not None and ficha[0] == color:
                visitadas.add(v)
                cola.append(v)
    return visitadas

def colocar(estado: Estado, n: int, ficha: Ficha, celda: int) -> Estado:
    # Versión inmutable: no modifica el estado recibido y devuelve uno nuevo.
    tablero = list(estado)
    colocar_en(tablero, n, ficha, celda)
    return tuple(tablero)

def colocar_en(tablero: list, n: int, ficha: Ficha, celda: int) -> set[int]:
    # La regla de colocación y fusión, aplicada sobre una lista que se modifica.
    # Devuelve el grupo de la ficha colocada (si tiene 2 o más fichas, se fusionó).
    if not 0 <= celda < len(tablero):
        raise MovimientoInvalido(f"la celda {celda} está fuera del tablero")
    if tablero[celda] is not None:
        fila, col = posicion(n, celda)
        raise MovimientoInvalido(f"la celda ({fila}, {col}) ya está ocupada")

    color, _ = ficha
    tablero[celda] = ficha

    grupo = componente(tablero, n, celda, color)
    if len(grupo) >= 2:
        total = 0
        for i in grupo:
            total += tablero[i][1]
            tablero[i] = None
        tablero[celda] = (color, total)

    return grupo
