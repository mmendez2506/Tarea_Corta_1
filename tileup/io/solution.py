# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Cristhian Rivas y Jozafath Perez
# Descripción: Escritura de movimientos y métricas en el archivo de solución.
# ==============================

import os

def formatear_solucion(colocaciones, colocadas: int, ocupadas: int, mayor: int) -> str:
    lineas = [f"{i} {fila} {col}" for i, (fila, col) in enumerate(colocaciones)]
    lineas.append(f"# colocadas={colocadas} ocupadas={ocupadas} mayor={mayor}")
    return "\n".join(lineas) + "\n"

def escribir_solucion(ruta: str, colocaciones, colocadas: int, ocupadas: int, mayor: int) -> None:
    carpeta = os.path.dirname(ruta)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write(formatear_solucion(colocaciones, colocadas, ocupadas, mayor))
