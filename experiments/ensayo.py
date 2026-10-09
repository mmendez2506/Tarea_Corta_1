# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Christian Rivas y Jozafath Perez
# Descripción: Ensayo del concurso: corre ambos agentes con el N, K y M anunciados y recomienda uno.
# ==============================

import argparse
import csv
from pathlib import Path
import subprocess
import sys
import time

from generator.generate import generar
from validator.validate import ValidacionInvalida, validar

AGENTES = ("search", "evolutionary")

def correr(instancia, solucion, agente, semilla, limite):
    # Corre el programa completo, como en el concurso, y mide el reloj del proceso.
    comando = [sys.executable, "-m", "tileup.main", "--instancia", str(instancia),
               "--agente", agente, "--semilla", str(semilla), "--limite", str(limite),
               "--salida", str(solucion)]
    inicio = time.perf_counter()
    proceso = subprocess.run(comando, capture_output=True, text=True, timeout=limite * 3 + 10)
    reloj = time.perf_counter() - inicio
    registro = {"agente": agente, "semilla": semilla, "reloj_s": round(reloj, 3)}
    if proceso.returncode != 0:
        return {**registro, "estado": "error", "colocadas": 0, "ocupadas": 0}
    try:
        partida = validar(instancia, solucion)
    except ValidacionInvalida:
        return {**registro, "estado": "rechazada", "colocadas": 0, "ocupadas": 0}
    estado = "fuera_de_tiempo" if reloj > limite else partida.resultado
    return {**registro, "estado": estado, "colocadas": partida.colocadas, "ocupadas": partida.ocupadas}

def orden_concurso(registro):
    # más colocadas, luego menos ocupadas, luego menos tiempo; fuera de tiempo o rechazada pierde
    valida = registro["estado"] in ("victoria", "derrota", "incompleta")
    return (not valida, -registro["colocadas"], registro["ocupadas"], registro["reloj_s"])

def main(argv=None):
    parser = argparse.ArgumentParser(description="Ensayo del concurso con N, K y M anunciados")
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--k", type=int, required=True)
    parser.add_argument("--m", type=int, required=True)
    parser.add_argument("--limite", type=float, default=10)
    parser.add_argument("--semillas", nargs="+", type=int, default=[1, 2, 3, 4, 5])
    parser.add_argument("--salida", default="experiments/ensayo")
    args = parser.parse_args(argv)

    carpeta = Path(args.salida)
    carpeta.mkdir(parents=True, exist_ok=True)
    registros, ganadas = [], {agente: 0 for agente in AGENTES}
    print(f"Ensayo N={args.n} K={args.k} M={args.m} límite={args.limite}s")
    for semilla in args.semillas:
        instancia = carpeta / f"n{args.n}_k{args.k}_m{args.m}_s{semilla}.txt"
        instancia.write_text(generar(args.n, args.k, args.m, semilla), encoding="utf-8")
        ronda = [correr(instancia, carpeta / f"{instancia.stem}_{agente}.txt", agente, semilla, args.limite)
                 for agente in AGENTES]
        ganador = min(ronda, key=orden_concurso)["agente"]
        ganadas[ganador] += 1
        registros += ronda
        for r in ronda:
            print(f"  semilla {semilla:3} {r['agente']:13} {r['estado']:15} colocadas={r['colocadas']:6} "
                  f"ocupadas={r['ocupadas']:5} reloj={r['reloj_s']:6.2f}s{'  <- gana' if r['agente'] == ganador else ''}")

    with (carpeta / "resultados.csv").open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(registros[0]))
        escritor.writeheader()
        escritor.writerows(registros)
    # a igual cantidad de rondas ganadas, desempata el total con el mismo orden del concurso
    def total(agente):
        propios = [r for r in registros if r["agente"] == agente]
        return (ganadas[agente], sum(r["colocadas"] for r in propios),
                -sum(r["ocupadas"] for r in propios), -sum(r["reloj_s"] for r in propios))
    recomendado = max(AGENTES, key=total)
    print(f"Rondas ganadas: {ganadas}. Agente recomendado para el concurso: {recomendado}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
