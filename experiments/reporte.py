# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Christian Rivas y Jozafath Perez
# Descripción: Tablas Markdown y gráficas SVG de tendencia a partir de resumen.csv.
# ==============================

import argparse
import csv
import math
from html import escape
from pathlib import Path
import sys

from tileup.main import cargar_agente

COLORES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
MARCADORES = ["circulo", "cuadrado", "triangulo", "rombo"]
TINTA, TINTA_SECUNDARIA, REJILLA, FONDO = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"

def leer(ruta):
    with open(ruta, encoding="utf-8") as archivo:
        filas = list(csv.DictReader(archivo))
    for fila in filas:
        for clave in ("n", "k", "m", "ejecuciones", "validas", "victorias", "fallos"):
            fila[clave] = int(fila[clave])
        for clave, valor in list(fila.items()):
            if clave.endswith(("_media", "_desviacion")):
                fila[clave] = float(valor) if valor != "" else None
    return filas

def _md(media, desviacion, decimales):
    if media is None:
        return "—"
    return f"{media:.{decimales}f} ± {desviacion:.{decimales}f}"

def tabla(filas, agentes):
    lineas = [
        "| N | K | M | Agente | Victorias | Colocadas | Ocupadas | Tiempo (s) | Esfuerzo |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    orden = {agente: i for i, agente in enumerate(agentes)}
    for fila in sorted(filas, key=lambda f: (f["n"], f["k"], f["m"], orden.get(f["agente"], 99))):
        if fila["agente"] not in orden:
            continue
        unidad = cargar_agente(fila["agente"]).unidad_esfuerzo
        lineas.append(
            f"| {fila['n']} | {fila['k']} | {fila['m']} | `{fila['agente']}` "
            f"| {fila['victorias']}/{fila['ejecuciones']} "
            f"| {_md(fila['colocadas_media'], fila['colocadas_desviacion'], 1)} "
            f"| {_md(fila['ocupadas_media'], fila['ocupadas_desviacion'], 1)} "
            f"| {_md(fila['tiempo_s_media'], fila['tiempo_s_desviacion'], 3)} "
            f"| {_md(fila['esfuerzo_media'], fila['esfuerzo_desviacion'], 0)} {unidad} |"
        )
    return "\n".join(lineas) + "\n"

def _marcador(forma, x, y, color):
    r = 4.5
    borde = f'fill="{color}" stroke="{FONDO}" stroke-width="2"'
    if forma == "cuadrado":
        return f'<rect x="{x - r:.1f}" y="{y - r:.1f}" width="{2 * r}" height="{2 * r}" rx="1" {borde}/>'
    if forma == "triangulo":
        puntos = f"{x:.1f},{y - r - 1:.1f} {x + r + 1:.1f},{y + r:.1f} {x - r - 1:.1f},{y + r:.1f}"
        return f'<polygon points="{puntos}" {borde}/>'
    if forma == "rombo":
        puntos = f"{x:.1f},{y - r - 1:.1f} {x + r + 1:.1f},{y:.1f} {x:.1f},{y + r + 1:.1f} {x - r - 1:.1f},{y:.1f}"
        return f'<polygon points="{puntos}" {borde}/>'
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" {borde}/>'

def _escala(maximo):
    if maximo <= 0:
        return 1.0, [0, 0.25, 0.5, 0.75, 1.0]
    for exponente in range(-4, 8):
        for base in (1, 2, 2.5, 5):
            paso = base * 10 ** exponente
            divisiones = math.ceil(maximo / paso - 1e-9)
            if divisiones <= 5:
                return divisiones * paso, [paso * i for i in range(divisiones + 1)]
    return maximo, [0, maximo]

def grafica(filas, agentes, eje, serie, metrica, titulo, etiqueta_y, ruta, relativa=False):
    def valor(fila):
        media, desviacion = fila[metrica + "_media"], fila[metrica + "_desviacion"]
        if media is None:
            return None
        if relativa:
            return media / fila["m"], desviacion / fila["m"]
        return media, desviacion

    xs = sorted({fila[eje] for fila in filas})
    series = sorted({fila[serie] for fila in filas})
    puntos = [valor(f) for f in filas if f["agente"] in agentes and valor(f)]
    maximo = max((m + d for m, d in puntos), default=1)
    tope, marcas = _escala(1.0 if relativa else maximo)

    ancho_panel, alto, izquierda, arriba, abajo, separacion = 330, 300, 64, 86, 56, 56
    ancho = izquierda + len(agentes) * ancho_panel + (len(agentes) - 1) * separacion + 24
    alto_total = arriba + alto + abajo + 30
    partes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto_total}" '
        f'viewBox="0 0 {ancho} {alto_total}" font-family="sans-serif" role="img" '
        f'aria-label="{escape(titulo)}">',
        f'<rect width="100%" height="100%" fill="{FONDO}"/>',
        f'<text x="{izquierda}" y="24" font-size="15" font-weight="600" fill="{TINTA}">{escape(titulo)}</text>',
    ]
    leyenda_x = izquierda
    for i, s in enumerate(series):
        color, forma = COLORES[i % len(COLORES)], MARCADORES[i % len(MARCADORES)]
        partes.append(f'<line x1="{leyenda_x}" y1="44" x2="{leyenda_x + 22}" y2="44" stroke="{color}" stroke-width="2"/>')
        partes.append(_marcador(forma, leyenda_x + 11, 44, color))
        partes.append(f'<text x="{leyenda_x + 28}" y="48" font-size="12" fill="{TINTA_SECUNDARIA}">{serie.upper()} = {s}</text>')
        leyenda_x += 90

    for p, agente in enumerate(agentes):
        x0 = izquierda + p * (ancho_panel + separacion)
        base = arriba + alto
        partes.append(f'<text x="{x0 + ancho_panel / 2}" y="{arriba - 16}" font-size="13" '
                      f'text-anchor="middle" fill="{TINTA}">{escape(agente)}</text>')
        for marca in marcas:
            y = base - marca / tope * alto
            partes.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x0 + ancho_panel}" y2="{y:.1f}" stroke="{REJILLA}" stroke-width="1"/>')
            if p == 0:
                texto = f"{marca:.0%}" if relativa else f"{marca:g}"
                partes.append(f'<text x="{x0 - 8}" y="{y + 4:.1f}" font-size="11" text-anchor="end" fill="{TINTA_SECUNDARIA}">{texto}</text>')

        def px(x):
            if len(xs) == 1:
                return x0 + ancho_panel / 2
            return x0 + 20 + xs.index(x) / (len(xs) - 1) * (ancho_panel - 40)

        for x in xs:
            partes.append(f'<text x="{px(x):.1f}" y="{base + 18}" font-size="11" text-anchor="middle" fill="{TINTA_SECUNDARIA}">{x}</text>')
        partes.append(f'<text x="{x0 + ancho_panel / 2}" y="{base + 38}" font-size="12" text-anchor="middle" fill="{TINTA_SECUNDARIA}">{eje.upper()}</text>')

        etiquetas = []
        for i, s in enumerate(series):
            color, forma = COLORES[i % len(COLORES)], MARCADORES[i % len(MARCADORES)]
            datos = []
            for fila in sorted(filas, key=lambda f: f[eje]):
                if fila["agente"] == agente and fila[serie] == s and valor(fila):
                    media, desviacion = valor(fila)
                    datos.append((px(fila[eje]), base - media / tope * alto,
                                  base - min(media + desviacion, tope) / tope * alto,
                                  base - max(media - desviacion, 0) / tope * alto))
            if len(datos) > 1:
                camino = " ".join(f"{x:.1f},{y:.1f}" for x, y, _, _ in datos)
                partes.append(f'<polyline points="{camino}" fill="none" stroke="{color}" stroke-width="2"/>')
            for x, y, y_alto, y_bajo in datos:
                if y_bajo - y_alto > 1:
                    partes.append(f'<line x1="{x:.1f}" y1="{y_alto:.1f}" x2="{x:.1f}" y2="{y_bajo:.1f}" stroke="{color}" stroke-width="1.5"/>')
                partes.append(_marcador(forma, x, y, color))
            if datos:
                etiquetas.append([datos[-1][1], datos[-1][0], f"{serie.upper()}={s}"])
        etiquetas.sort()
        for j in range(1, len(etiquetas)):
            etiquetas[j][0] = max(etiquetas[j][0], etiquetas[j - 1][0] + 13)
        for y, x, texto in etiquetas:
            partes.append(f'<text x="{x + 9:.1f}" y="{y + 4:.1f}" font-size="11" fill="{TINTA_SECUNDARIA}">{texto}</text>')
        partes.append(f'<line x1="{x0}" y1="{base}" x2="{x0 + ancho_panel}" y2="{base}" stroke="{TINTA_SECUNDARIA}" stroke-width="1"/>')

    partes.append(f'<text x="16" y="{arriba + alto / 2}" font-size="12" fill="{TINTA_SECUNDARIA}" '
                  f'text-anchor="middle" transform="rotate(-90 16 {arriba + alto / 2})">{escape(etiqueta_y)}</text>')
    partes.append(f'<text x="{izquierda}" y="{alto_total - 8}" font-size="11" fill="{TINTA_SECUNDARIA}">'
                  'Media entre semillas; las barras verticales indican ± una desviación estándar.</text>')
    partes.append("</svg>")
    Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    Path(ruta).write_text("\n".join(partes), encoding="utf-8")

def main(argv=None):
    parser = argparse.ArgumentParser(description="Genera tablas y gráficas de una batería de run_all")
    parser.add_argument("--resumen", required=True, help="resumen.csv de run_all")
    parser.add_argument("--agentes", nargs="+", default=["search", "evolutionary", "trivial"])
    parser.add_argument("--tabla", help="archivo Markdown de salida para la tabla")
    parser.add_argument("--graficas", help="carpeta de salida de las gráficas SVG")
    parser.add_argument("--prefijo", default="", help="prefijo del nombre de cada gráfica")
    parser.add_argument("--eje", default="n", choices=["n", "k", "m"])
    parser.add_argument("--serie", default="k", choices=["n", "k", "m"])
    args = parser.parse_args(argv)
    filas = leer(args.resumen)
    if args.tabla:
        Path(args.tabla).write_text(tabla(filas, args.agentes), encoding="utf-8")
    if args.graficas:
        agentes = [a for a in args.agentes if a != "trivial"]
        destino = Path(args.graficas)
        p = args.prefijo
        grafica(filas, agentes, args.eje, args.serie, "tiempo_s",
                f"Tiempo de cómputo según {args.eje.upper()}", "segundos", destino / f"{p}tiempo.svg")
        grafica(filas, agentes, args.eje, args.serie, "colocadas",
                f"Fracción de la secuencia colocada según {args.eje.upper()}", "colocadas / M",
                destino / f"{p}colocadas.svg", relativa=True)
        grafica(filas, agentes, args.eje, args.serie, "ocupadas",
                f"Celdas ocupadas al terminar según {args.eje.upper()}", "celdas ocupadas",
                destino / f"{p}ocupadas.svg")
    return 0

if __name__ == "__main__":
    sys.exit(main())
