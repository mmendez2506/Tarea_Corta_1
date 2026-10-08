# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Christian Rivas y Jozafath Perez
# Descripción: Punto de entrada: recibe argumentos, ejecuta el agente y guarda la solución.
# ==============================

import argparse
import math
import os
import sys
import time

from tileup.agents.base import Agente
from tileup.agents.evolutionary import AgenteEvolutivo
from tileup.agents.search import AgenteBusqueda
from tileup.agents.trivial import PrimeraLibre
from tileup.engine.board import MovimientoInvalido
from tileup.engine.game import jugar
from tileup.io.instance import InstanciaInvalida, leer_instancia
from tileup.io.solution import escribir_solucion

AGENTES: dict[str, type[Agente]] = {
    "evolutionary": AgenteEvolutivo,
    "search": AgenteBusqueda,
    "trivial": PrimeraLibre,
}

def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tileup", description="Agentes para TileUp")
    parser.add_argument("--instancia", required=True, help="ruta del archivo de instancia")
    parser.add_argument("--agente", required=True, choices=sorted(AGENTES), help="agente a usar")
    parser.add_argument("--semilla", type=int, default=0, help="semilla (por defecto 0)")
    parser.add_argument("--limite", type=float, default=10.0, help="límite de tiempo en segundos")
    parser.add_argument("--salida", help="archivo de solución (por defecto en solutions/)")
    return parser

def ruta_por_defecto(instancia: str, agente: str, semilla: int) -> str:
    base = os.path.splitext(os.path.basename(instancia))[0]
    return os.path.join("solutions", f"{base}_{agente}_s{semilla}.txt")

def main(argv=None) -> int:
    args = construir_parser().parse_args(argv)
    if not math.isfinite(args.limite) or args.limite <= 0:
        print("error: el límite de tiempo debe ser positivo", file=sys.stderr)
        return 2

    try:
        instancia = leer_instancia(args.instancia)
    except InstanciaInvalida as error:
        print(f"error en la instancia: {error}", file=sys.stderr)
        return 1

    agente = AGENTES[args.agente]()
    inicio = time.perf_counter()
    resultado = agente.resolver(instancia, args.semilla, args.limite)
    transcurrido = time.perf_counter() - inicio

    try:
        partida = jugar(instancia, resultado.colocaciones)
    except (MovimientoInvalido, ValueError) as error:
        print(f"error: el agente produjo una solución ilegal: {error}", file=sys.stderr)
        return 3

    salida = args.salida or ruta_por_defecto(args.instancia, args.agente, args.semilla)
    escribir_solucion(
        salida, resultado.colocaciones, partida.colocadas, partida.ocupadas, partida.mayor
    )

    print(f"agente={args.agente}")
    print(f"semilla={args.semilla}")
    print(f"resultado={partida.resultado}")
    print(f"colocadas={partida.colocadas}/{instancia.m}")
    print(f"ocupadas={partida.ocupadas}")
    print(f"mayor={partida.mayor}")
    print(f"tiempo_s={transcurrido:.4f}")
    print(f"esfuerzo={resultado.esfuerzo} ({agente.unidad_esfuerzo})")
    print(f"solucion={salida}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
