# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Cristhian Rivas y Jozafath Perez
# Descripción: Barrido de parámetros del agente de búsqueda sobre instancias de ajuste.
# ==============================

import argparse
import csv
from pathlib import Path
import sys
import time

from generator.generate import generar
from tileup.agents.search import AgenteBusqueda
from tileup.engine.game import jugar
from tileup.io.instance import parsear_instancia

# Régimen de muchos colores; semillas distintas de las de pruebas y batería.
CONJUNTOS = {
    "ajuste": [(4, 12), (5, 16), (6, 24), (7, 32)],
    # tableros medianos con muchos colores, donde se ajustó el desempate por bloqueos
    "medianos": [(10, 25), (10, 60), (12, 40), (12, 100), (16, 50), (16, 150), (20, 100), (24, 200)],
}
SEMILLAS = [101, 102, 103]

# Punto de partida del barrido (valores previos al ajuste); cada variante cambia solo lo indicado.
# El desempate por bloqueos se agregó después, por eso la base lo deja apagado.
BASE = {"ventana": 3, "evitar_bloqueos": False}

VARIANTES = {
    "base": {},
    "sin_potencial": {"ventana": 0},
    "ventana_1": {"ventana": 1},
    "ventana_5": {"ventana": 5},
    "tope_1": {"tope": 1},
    "tope_4": {"tope": 4},
    "dobles_0.5": {"peso_dobles": 0.5},
    "dobles_1": {"peso_dobles": 1.0},
    "alfa_0.5": {"alfa": 0.5},
    "alfa_1": {"alfa": 1.0},
    "simetrias": {"simetrias": True},
    "ventana_7": {"ventana": 7},
    "ventana_10": {"ventana": 10},
    "ventana_5_tope_3": {"ventana": 5, "tope": 3},
    "ventana_5_dobles_0.5": {"ventana": 5, "peso_dobles": 0.5},
    "ventana_7_tope_3": {"ventana": 7, "tope": 3},
    "ventana_10_bloqueos": {"ventana": 10, "evitar_bloqueos": True},
}

def correr(variantes, presupuesto, factor_m, semillas, configuraciones):
    registros = []
    for nombre in variantes:
        parametros = VARIANTES[nombre]
        for n, k in configuraciones:
            for semilla in semillas:
                instancia = parsear_instancia(generar(n, k, factor_m * n * n, semilla))
                agente = AgenteBusqueda(presupuesto=presupuesto, **{**BASE, **parametros})
                inicio = time.perf_counter()
                resultado = agente.resolver(instancia, semilla, 600)
                tiempo = time.perf_counter() - inicio
                partida = jugar(instancia, resultado.colocaciones)
                registros.append({
                    "variante": nombre, "n": n, "k": k, "m": instancia.m, "semilla": semilla,
                    "resultado": partida.resultado, "colocadas": partida.colocadas,
                    "ocupadas": partida.ocupadas, "nodos": resultado.esfuerzo,
                    "tiempo_s": round(tiempo, 3),
                })
        resumir(nombre, [r for r in registros if r["variante"] == nombre])
    return registros

def resumir(nombre, registros):
    victorias = sum(r["resultado"] == "victoria" for r in registros)
    colocadas = sum(r["colocadas"] for r in registros)
    ocupadas = sum(r["ocupadas"] for r in registros if r["resultado"] == "victoria")
    tiempo = sum(r["tiempo_s"] for r in registros)
    print(f"{nombre:14} victorias={victorias:2}/{len(registros)} colocadas={colocadas:4} "
          f"ocupadas_en_victorias={ocupadas:4} tiempo_total={tiempo:6.1f}s", flush=True)

def main(argv=None):
    parser = argparse.ArgumentParser(description="Ajuste de parámetros del agente de búsqueda")
    parser.add_argument("--variantes", nargs="+", default=list(VARIANTES), choices=list(VARIANTES))
    parser.add_argument("--presupuesto", type=int, default=30_000)
    parser.add_argument("--factor-m", type=int, default=3)
    parser.add_argument("--semillas", nargs="+", type=int, default=SEMILLAS)
    parser.add_argument("--conjunto", choices=list(CONJUNTOS), default="ajuste")
    parser.add_argument("--salida", default="experiments/ajuste_busqueda.csv")
    args = parser.parse_args(argv)
    registros = correr(args.variantes, args.presupuesto, args.factor_m, args.semillas,
                       CONJUNTOS[args.conjunto])
    ruta = Path(args.salida)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(registros[0]))
        escritor.writeheader()
        escritor.writerows(registros)
    return 0

if __name__ == "__main__":
    sys.exit(main())
