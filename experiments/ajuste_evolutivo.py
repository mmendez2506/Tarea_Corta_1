# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Christian Rivas y Jozafath Perez
# Descripción: Barrido de parámetros del agente evolutivo sobre instancias de ajuste.
# ==============================

import argparse
import csv
from pathlib import Path
import sys
import time

from generator.generate import generar
from tileup.agents.evolutionary import AgenteEvolutivo
from tileup.engine.game import jugar
from tileup.io.instance import parsear_instancia

# Mismo conjunto de ajuste que el agente de búsqueda; semillas fuera de pruebas y baterías.
CONJUNTOS = {
    "ajuste": [(4, 12), (5, 16), (6, 24), (7, 32)],
    "medianos": [(10, 25), (10, 60), (12, 40), (12, 100), (16, 50), (16, 150), (20, 100), (24, 200)],
}
SEMILLAS = [101, 102, 103]

# Configuración elegida en el primer ajuste; las variantes "final_*" se comparan con ella.
FINAL = {"genes_mutados": 4.0, "densidad_inicial": 0.3}

# Punto de partida del barrido; cada variante cambia solo lo indicado.
BASE = {"genes_mutados": 2.0, "densidad_inicial": 0.1}

VARIANTES = {
    "base": {},
    "voraz": {"presupuesto": 1},
    "sin_cruce": {"prob_cruce": 0.0},
    "poblacion_20": {"poblacion": 20},
    "poblacion_80": {"poblacion": 80},
    "torneo_2": {"torneo": 2},
    "torneo_5": {"torneo": 5},
    "mutados_1": {"genes_mutados": 1.0},
    "mutados_4": {"genes_mutados": 4.0},
    "rango_0.15": {"prob_rango": 0.15},
    "rango_0.5": {"prob_rango": 0.5},
    "densidad_0": {"densidad_inicial": 0.0},
    "densidad_0.3": {"densidad_inicial": 0.3},
    "elite_1": {"elite": 1},
    "elite_5": {"elite": 5},
    "mutados_6": {"genes_mutados": 6.0},
    "mutados_4_densidad_0.3": {"genes_mutados": 4.0, "densidad_inicial": 0.3},
    "final": FINAL,
    "final_enfriamiento_0.5": {**FINAL, "enfriamiento": 0.5},
    "final_enfriamiento_0.8": {**FINAL, "enfriamiento": 0.8},
    "final_sin_repetidos": {**FINAL, "sin_repetidos": True},
    "final_poblacion_80": {**FINAL, "poblacion": 80},
    "final_torneo_5": {**FINAL, "torneo": 5},
}

def correr(variantes, presupuesto, semillas, configuraciones, ritmo=None):
    registros = []
    for nombre in variantes:
        parametros = {"presupuesto": presupuesto, **BASE, **VARIANTES[nombre]}
        for n, k in configuraciones:
            for semilla in semillas:
                instancia = parsear_instancia(generar(n, k, 3 * n * n, semilla))
                if ritmo is not None and "presupuesto" not in VARIANTES[nombre]:
                    # el presupuesto que el agente se daría con un límite de 10 s
                    parametros["presupuesto"] = max(1, int(ritmo * 10 / (instancia.m * n ** 0.5)))
                inicio = time.perf_counter()
                resultado = AgenteEvolutivo(**parametros).resolver(instancia, semilla, 600)
                tiempo = time.perf_counter() - inicio
                partida = jugar(instancia, resultado.colocaciones)
                registros.append({
                    "variante": nombre, "n": n, "k": k, "m": instancia.m, "semilla": semilla,
                    "resultado": partida.resultado, "colocadas": partida.colocadas,
                    "ocupadas": partida.ocupadas, "evaluaciones": resultado.esfuerzo,
                    "tiempo_s": round(tiempo, 3),
                })
        resumir(nombre, [r for r in registros if r["variante"] == nombre])
    return registros

def resumir(nombre, registros):
    victorias = sum(r["resultado"] == "victoria" for r in registros)
    colocadas = sum(r["colocadas"] for r in registros)
    ocupadas = sum(r["ocupadas"] for r in registros)
    tiempo = sum(r["tiempo_s"] for r in registros)
    print(f"{nombre:14} victorias={victorias:2}/{len(registros)} colocadas={colocadas:4} "
          f"ocupadas={ocupadas:4} tiempo_total={tiempo:6.1f}s", flush=True)

def main(argv=None):
    parser = argparse.ArgumentParser(description="Ajuste de parámetros del agente evolutivo")
    parser.add_argument("--variantes", nargs="+", default=list(VARIANTES), choices=list(VARIANTES))
    parser.add_argument("--presupuesto", type=int, default=1_500)
    parser.add_argument("--ritmo", type=float,
                        help="en lugar de --presupuesto, usa la fórmula del agente con este ritmo y 10 s")
    parser.add_argument("--semillas", nargs="+", type=int, default=SEMILLAS)
    parser.add_argument("--conjunto", choices=list(CONJUNTOS), default="ajuste")
    parser.add_argument("--salida", default="experiments/ajuste_evolutivo.csv")
    args = parser.parse_args(argv)
    registros = correr(args.variantes, args.presupuesto, args.semillas, CONJUNTOS[args.conjunto],
                       args.ritmo)
    ruta = Path(args.salida)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(registros[0]))
        escritor.writeheader()
        escritor.writerows(registros)
    return 0

if __name__ == "__main__":
    sys.exit(main())
