# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Cristhian Rivas y Jozafath Perez
# Descripción: Generador de instancias parametrizado por N, K, M y semilla.
# ==============================

import argparse
from pathlib import Path
import random
import sys

def generar(n, k, m, semilla, valor_max=9):
    if n < 1 or k < 1 or m < 0 or valor_max < 1:
        raise ValueError("N, K y valor_max deben ser positivos; M no negativo")
    rng = random.Random(semilla)
    lineas = [f"# semilla={semilla}", f"{n} {k}", str(m)]
    lineas += [f"{rng.randint(1, k)} {rng.randint(1, valor_max)}" for _ in range(m)]
    return "\n".join(lineas) + "\n"

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    for nombre in ("n", "k", "m", "semilla"):
        p.add_argument("--" + nombre, type=int, required=True)
    p.add_argument("--valor-max", type=int, default=9)
    p.add_argument("--salida", required=True)
    a = p.parse_args(argv)
    try:
        texto = generar(a.n, a.k, a.m, a.semilla, a.valor_max)
        ruta = Path(a.salida)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(texto, encoding="utf-8")
    except (ValueError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
