# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Cristhian Rivas y Jozafath Perez
# Descripción: Batería de escalabilidad: ejecución, validación, métricas, dispersión y gráfica.
# ==============================

import argparse
from collections import defaultdict
import csv
from html import escape
import math
from pathlib import Path
import statistics
import subprocess
import sys

from generator.generate import generar
from tileup.main import AGENTES
from validator.validate import validar

METRICAS = ('colocadas', 'ocupadas', 'mayor', 'tiempo_s', 'esfuerzo')
ESTADOS_VALIDOS = ('victoria', 'derrota', 'incompleta')


def correr_agente(entrada, salida, agente, n, k, m, semilla, limite):
    registro = {
        'agente': agente, 'n': n, 'k': k, 'm': m, 'semilla': semilla,
        'estado': 'error', 'colocadas': '', 'ocupadas': '', 'mayor': '',
        'tiempo_s': '', 'tiempo_total_s': '', 'esfuerzo': '', 'detalle': '',
    }
    comando = [
        sys.executable, '-m', 'tileup.main',
        '--instancia', str(entrada), '--salida', str(salida),
        '--agente', agente, '--semilla', str(semilla), '--limite', str(limite),
    ]
    try:
        proceso = subprocess.run(
            comando, capture_output=True, text=True, timeout=limite + 5
        )
        if proceso.returncode != 0:
            raise ValueError(proceso.stderr.strip() or f'código {proceso.returncode}')

        metricas = {}
        for linea in proceso.stdout.splitlines():
            if '=' in linea:
                nombre, valor = linea.split('=', 1)
                metricas[nombre] = valor

        partida = validar(entrada, salida)
        for nombre in ('colocadas', 'ocupadas', 'mayor'):
            valor = int(metricas[nombre].split('/')[0])
            if valor != getattr(partida, nombre):
                raise ValueError('métricas incompatibles con el validador')
            registro[nombre] = valor

        registro['tiempo_s'] = float(metricas['tiempo_s'])
        # El límite se controla con el tiempo de toda la ejecución, que incluye la
        # verificación y la escritura de la solución, no solo el del agente.
        registro['tiempo_total_s'] = float(metricas.get('tiempo_total_s', metricas['tiempo_s']))
        registro['esfuerzo'] = int(metricas['esfuerzo'].split()[0])
        if registro['tiempo_total_s'] > limite:
            registro['estado'] = 'fuera_de_tiempo'
        else:
            registro['estado'] = partida.resultado
    except (subprocess.TimeoutExpired, ValueError, KeyError) as error:
        registro['detalle'] = str(error)
    return registro


def guardar_csv(ruta, registros):
    with ruta.open('w', newline='', encoding='utf-8') as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(registros[0]))
        escritor.writeheader()
        escritor.writerows(registros)


def resumir_resultados(registros):
    grupos = defaultdict(list)
    for registro in registros:
        clave = (registro['agente'], registro['n'], registro['k'], registro['m'])
        grupos[clave].append(registro)

    resumenes = []
    for (agente, n, k, m), grupo in sorted(grupos.items()):
        validas = [registro for registro in grupo if registro['estado'] in ESTADOS_VALIDOS]
        resumen = {
            'agente': agente, 'n': n, 'k': k, 'm': m,
            'ejecuciones': len(grupo), 'validas': len(validas),
            'victorias': sum(registro['estado'] == 'victoria' for registro in validas),
            'fallos': len(grupo) - len(validas),
        }
        for nombre in METRICAS:
            valores = [registro[nombre] for registro in validas]
            if not valores:
                media, desviacion = '', ''
            else:
                media = statistics.mean(valores)
                desviacion = statistics.stdev(valores) if len(valores) > 1 else 0
            resumen[nombre + '_media'] = media
            resumen[nombre + '_desviacion'] = desviacion
        resumenes.append(resumen)
    return resumenes


def guardar_grafica(ruta, resumenes):
    alto = 100 + 35 * len(resumenes)
    tiempos = [
        resumen['tiempo_s_media'] + resumen['tiempo_s_desviacion']
        for resumen in resumenes if resumen['validas']
    ]
    maximo = max(tiempos, default=1) or 1
    partes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{alto}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="20" y="28" font-family="sans-serif" font-size="18">'
        'Tiempo: media y desviación entre semillas (segundos)</text>',
    ]
    for indice, resumen in enumerate(resumenes):
        altura = 65 + indice * 35
        etiqueta = (
            f"{resumen['agente']} N={resumen['n']} K={resumen['k']} M={resumen['m']} "
            f"válidas={resumen['validas']}/{resumen['ejecuciones']}"
        )
        partes.append(
            f'<text x="15" y="{altura + 12}" font-family="sans-serif" '
            f'font-size="12">{escape(etiqueta)}</text>'
        )
        if not resumen['validas']:
            continue
        media = resumen['tiempo_s_media']
        desviacion = resumen['tiempo_s_desviacion']
        ancho_barra = media / maximo * 550
        izquierda = 360 + max(0, media - desviacion) / maximo * 550
        derecha = 360 + (media + desviacion) / maximo * 550
        partes.extend([
            f'<rect x="360" y="{altura}" width="{ancho_barra}" height="16" fill="#3873aa"/>',
            f'<path d="M {izquierda} {altura + 8} H {derecha} '
            f'M {izquierda} {altura + 3} V {altura + 13} '
            f'M {derecha} {altura + 3} V {altura + 13}" stroke="black"/>',
            f'<text x="920" y="{altura + 12}" font-size="12">{media:.4f}</text>',
        ])
    partes.append('</svg>')
    ruta.write_text('\n'.join(partes), encoding='utf-8')


def ejecutar(raiz, agentes, ns, ks, semillas, limite, factor,
             dir_instancias=None, dir_soluciones=None, m_fijo=None):
    if len(set(ns)) < 3 or len(set(ks)) < 3 or len(set(semillas)) < 3:
        raise ValueError('se requieren tres valores distintos de N, K y semilla')
    if min(ns + ks) < 1 or not math.isfinite(limite) or limite <= 0 or factor < 1:
        raise ValueError('dimensiones, límite y factor deben ser positivos')
    desconocidos = set(agentes) - set(AGENTES)
    if desconocidos:
        raise ValueError(f'agentes aún no registrados: {sorted(desconocidos)}')
    if not agentes:
        raise ValueError('se requiere al menos un agente')

    if m_fijo is not None and m_fijo < 0:
        raise ValueError('M fijo no puede ser negativo')

    raiz = Path(raiz)
    dir_instancias = Path(dir_instancias) if dir_instancias else raiz / 'instancias'
    dir_soluciones = Path(dir_soluciones) if dir_soluciones else raiz / 'soluciones'
    for carpeta in (raiz, dir_instancias, dir_soluciones):
        carpeta.mkdir(parents=True, exist_ok=True)
    registros = []
    for n in ns:
        for k in ks:
            m = m_fijo if m_fijo is not None else factor * n * n
            for semilla in semillas:
                nombre = f'n{n}_k{k}_m{m}_s{semilla}'
                entrada = dir_instancias / f'{nombre}.txt'
                entrada.write_text(generar(n, k, m, semilla), encoding='utf-8')
                for agente in agentes:
                    salida = dir_soluciones / f'{nombre}_{agente}.txt'
                    registro = correr_agente(entrada, salida, agente, n, k, m, semilla, limite)
                    registros.append(registro)

    guardar_csv(raiz / 'resultados.csv', registros)
    resumenes = resumir_resultados(registros)
    guardar_csv(raiz / 'resumen.csv', resumenes)
    guardar_grafica(raiz / 'tiempos.svg', resumenes)
    fallos = sum(registro['estado'] not in ESTADOS_VALIDOS for registro in registros)
    print(f'ejecuciones={len(registros)} fallos={fallos} resultados={raiz}')
    return 1 if fallos else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description='Ejecuta la batería experimental de TileUp')
    parser.add_argument('--agentes', nargs='+', default=['search', 'evolutionary', 'trivial'])
    parser.add_argument('--n', nargs='+', type=int, default=[4, 6, 8])
    parser.add_argument('--k', nargs='+', type=int, default=[4, 12, 24])
    parser.add_argument('--semillas', nargs='+', type=int, default=[1, 2, 3])
    parser.add_argument('--limite', type=float, default=10)
    parser.add_argument('--factor-m', type=int, default=3)
    parser.add_argument('--m-fijo', type=int, help='usa este M en todas las configuraciones en lugar de factor*N²')
    parser.add_argument('--salida', default='experiments/comparacion', help='carpeta de CSV y gráfica')
    parser.add_argument('--instancias', default='instances/comparacion', help='carpeta de instancias')
    parser.add_argument('--soluciones', default='solutions/comparacion', help='carpeta de soluciones')
    args = parser.parse_args(argv)
    try:
        return ejecutar(args.salida, args.agentes, args.n, args.k, args.semillas, args.limite,
                       args.factor_m, args.instancias, args.soluciones, args.m_fijo)
    except (ValueError, OSError) as error:
        print(f'error: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
