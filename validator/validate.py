# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Cristhian Rivas y Jozafath Perez
# Descripción: Validador independiente: comprueba la legalidad y el resumen de una solución.
# ==============================

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sys

class ValidacionInvalida(ValueError):
    pass

@dataclass(frozen=True)
class Resumen:
    colocadas: int
    ocupadas: int
    mayor: int
    resultado: str

def leer_texto(ruta):
    try:
        return Path(ruta).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise ValidacionInvalida(f"no se pudo leer {ruta}: {error}") from None

def instancia_desde_texto(texto):
    filas = [linea.split("#", 1)[0].split() for linea in texto.splitlines()]
    filas = [fila for fila in filas if fila]
    try:
        if len(filas) < 2 or len(filas[0]) != 2 or len(filas[1]) != 1:
            raise ValueError
        n, k = map(int, filas[0])
        m = int(filas[1][0])
        if n < 1 or k < 1 or m < 0 or len(filas) != m + 2:
            raise ValueError
        fichas = []
        for fila in filas[2:]:
            if len(fila) != 2:
                raise ValueError
            color, valor = map(int, fila)
            if not 1 <= color <= k or valor <= 0:
                raise ValueError
            fichas.append((color, valor))
        return n, fichas
    except ValueError:
        raise ValidacionInvalida("formato de instancia inválido") from None

def validar_textos(instancia, solucion):
    n, fichas = instancia_desde_texto(instancia)
    lineas = [linea.strip() for linea in solucion.splitlines() if linea.strip()]
    if not lineas:
        raise ValidacionInvalida("falta el resumen final")
    resumen = re.fullmatch(r"#\s*colocadas=(\d+)\s+ocupadas=(\d+)\s+mayor=(\d+)", lineas[-1])
    if resumen is None:
        raise ValidacionInvalida("resumen final inválido")
    tablero = {}
    for numero, linea in enumerate(lineas[:-1]):
        try:
            tokens = linea.split()
            if len(tokens) != 3:
                raise ValueError
            indice, fila, columna = map(int, tokens)
        except ValueError:
            raise ValidacionInvalida(f"movimiento {numero}: se requieren tres enteros") from None
        if indice != numero:
            raise ValidacionInvalida(f"movimiento {numero}: índice fuera de orden")
        if numero >= len(fichas) or len(tablero) == n * n:
            raise ValidacionInvalida(f"movimiento {numero}: partida ya terminada")
        posicion = fila, columna
        if not (0 <= fila < n and 0 <= columna < n):
            raise ValidacionInvalida(f"movimiento {numero}: posición fuera del tablero")
        if posicion in tablero:
            raise ValidacionInvalida(f"movimiento {numero}: celda ocupada")
        color, valor = fichas[numero]
        tablero[posicion] = (color, valor)
        grupo, pendientes = {posicion}, [posicion]
        while pendientes:
            fila_actual, columna_actual = pendientes.pop()
            for vecino in ((fila_actual - 1, columna_actual), (fila_actual + 1, columna_actual),
                           (fila_actual, columna_actual - 1), (fila_actual, columna_actual + 1)):
                if vecino not in grupo and vecino in tablero and tablero[vecino][0] == color:
                    grupo.add(vecino)
                    pendientes.append(vecino)
        total = sum(tablero[celda][1] for celda in grupo)
        for celda in grupo:
            del tablero[celda]
        tablero[posicion] = (color, total)
    colocadas = len(lineas) - 1
    ocupadas = len(tablero)
    mayor = max((ficha[1] for ficha in tablero.values()), default=0)
    if tuple(map(int, resumen.groups())) != (colocadas, ocupadas, mayor):
        raise ValidacionInvalida("el resumen no coincide con la partida")
    if colocadas == len(fichas):
        resultado = "victoria"
    elif ocupadas == n * n:
        resultado = "derrota"
    else:
        resultado = "incompleta"

    return Resumen(colocadas, ocupadas, mayor, resultado)

def validar(instancia, solucion):
    return validar_textos(leer_texto(instancia), leer_texto(solucion))

def main(argv=None):
    parser = argparse.ArgumentParser(description="Comprueba una solución de TileUp con un árbitro independiente")
    parser.add_argument("--instancia", required=True)
    parser.add_argument("--solucion", required=True)
    args = parser.parse_args(argv)
    try:
        partida = validar(args.instancia, args.solucion)
    except ValidacionInvalida as error:
        print(f"solucion ilegal: {error}", file=sys.stderr)
        return 1
    print(f"legal=si\nresultado={partida.resultado}\ncolocadas={partida.colocadas}\nocupadas={partida.ocupadas}\nmayor={partida.mayor}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
