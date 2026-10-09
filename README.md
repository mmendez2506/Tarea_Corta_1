# TileUp — Tarea Corta 1 (IC-6200 Inteligencia Artificial)

**Integrantes:** María Felix Mendez Abarca, Christian Rivas y Jozafath Perez

**Descripción:** Dos agentes que resuelven TileUp: uno de búsqueda (haz iterativo
con poda por cota admisible) y otro evolutivo (algoritmo genético). Incluye el
motor del juego, un validador independiente, un generador de instancias, pruebas
automatizadas y las baterías de comparación y escalabilidad. La formulación de
los agentes y el análisis experimental están en [`INFORME.md`](INFORME.md); el uso
de herramientas de IA está en [`DECLARACION_IA.md`](DECLARACION_IA.md).

## Requisitos

- **Docker** con el servicio iniciado. Es lo único necesario: la imagen instala
  Python 3.12 y pytest durante la construcción, que requiere acceso a internet la
  primera vez.
- Para los comandos cortos: **PowerShell** en Windows (`run.ps1`) o **Make** en
  Linux/macOS (`Makefile`).
- Opcional, para ejecutar sin Docker: Python 3.10 o posterior. El código usa solo
  la biblioteca estándar; pytest se usa para las pruebas.

## Ejecución con un solo comando

Desde la raíz del repositorio. Cada comando construye la imagen y ejecuta dentro
del contenedor.

| Qué hace | Windows (PowerShell) | Linux/macOS |
|---|---|---|
| Resolver el ejemplo con el agente de búsqueda | `powershell -ExecutionPolicy Bypass -File .\run.ps1` | `make run` |
| Validar la solución producida | `powershell -ExecutionPolicy Bypass -File .\run.ps1 -Accion validate` | `make validate` |
| Correr todas las pruebas (unitarias e integración) | `powershell -ExecutionPolicy Bypass -File .\run.ps1 -Accion test` | `make test` |
| Correr la comparación experimental | `powershell -ExecutionPolicy Bypass -File .\run.ps1 -Accion experiments` | `make experiments` |
| Ensayar el concurso con el N, K y M anunciados | `powershell -ExecutionPolicy Bypass -File .\run.ps1 -Accion ensayo -N 20 -K 50 -M 1200` | `make ensayo N=20 K=50 M=1200` |

`run.ps1` y `make` reconstruyen la imagen en cada ejecución (con caché, tarda unos
segundos) y montan la carpeta del proyecto en el contenedor, así que las
instancias y soluciones no se copian a la imagen.

Para otra instancia, agente, semilla o límite de tiempo:

```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1 -Instancia instances/mia.txt -Agente evolutionary -Semilla 7 -Limite 10
powershell -ExecutionPolicy Bypass -File .\run.ps1 -Accion validate -Instancia instances/mia.txt -Agente evolutionary -Semilla 7
```

```sh
make run INSTANCIA=instances/mia.txt AGENTE=evolutionary SEMILLA=7 LIMITE=10
make validate INSTANCIA=instances/mia.txt AGENTE=evolutionary SEMILLA=7
```

La solución se escribe en `solutions/<instancia>_<agente>_s<semilla>.txt`, que es
la ruta que usa `validate` por defecto; con `-Solucion` o `SOLUCION=` se elige
otra. Los archivos quedan en el repositorio porque el contenedor lo monta.
Agentes disponibles: `search` (búsqueda), `evolutionary` (evolutivo) y `trivial`
(referencia: primera celda libre).

## Ejecución sin Docker

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m tileup.main --instancia instances/ejemplo.txt --agente search --semilla 1 --limite 10
.\.venv\Scripts\python.exe -m validator.validate --instancia instances/ejemplo.txt --solucion solutions/ejemplo_search_s1.txt
```

En Linux/macOS se usa `.venv/bin/python` en lugar de `.\.venv\Scripts\python.exe`.

## Línea de comandos

```
python -m tileup.main --instancia RUTA --agente {search,evolutionary,trivial} [--semilla S] [--limite SEGUNDOS] [--salida RUTA]
```

- `--semilla` vale 0 por defecto y `--limite` vale 10 segundos.
- Toda la aleatoriedad sale de la semilla: la misma instancia, agente, semilla y
  límite producen la misma solución.
- Cada agente controla su propio tiempo. Se detiene al 90 % del límite y entrega
  la mejor solución encontrada.

Al terminar informa por salida estándar:

```
agente=search
semilla=1
resultado=victoria          # victoria, derrota o incompleta
colocadas=6/6
ocupadas=3
mayor=6
tiempo_s=0.0003
esfuerzo=6 (nodos)          # nodos expandidos o evaluaciones de aptitud
solucion=solutions/ejemplo_search_s1.txt
```

Códigos de salida:

| Código | Significado |
|---|---|
| 0 | ejecución válida |
| 1 | instancia mal formada (mensaje legible por la salida de error, sin traza) |
| 2 | argumentos inválidos |
| 3 | el agente produjo una solución ilegal |

El validador independiente:

```
python -m validator.validate --instancia RUTA --solucion RUTA
```

Reproduce la partida con su propio parser y su propio tablero (no importa nada de
`tileup/`). Rechaza celdas ocupadas, posiciones fuera del tablero, índices fuera de
orden, movimientos después del final y resúmenes que no coinciden. Si la
solución es legal, informa `legal=si`, el resultado, las colocadas, las ocupadas
y la ficha mayor, y retorna 0; si no, retorna 1.

## Formatos

**Instancia.** Texto plano. Se ignoran las líneas en blanco y todo lo que sigue a
`#`. El contenido es:

- una línea con `N K`;
- una línea con `M`;
- M líneas `color valor`, en el orden en que deben colocarse.

N y K son positivos, M puede ser 0, los colores van de 1 a K y los valores son
positivos.

```
# TileUp -- instancia de ejemplo
4 3   # tablero 4x4, 3 colores
6     # 6 fichas en la secuencia
1 2
2 1
1 3
3 1
1 1
2 4
```

**Solución.** Una línea `indice fila columna` por colocación, todo contado desde
cero. La última línea resume el resultado. Se escribe aunque la partida termine
en derrota o se agote el tiempo.

```
0 0 0
1 0 2
2 0 1
3 1 0
4 0 0
5 0 1
# colocadas=6 ocupadas=3 mayor=6
```

## Reglas implementadas

- El tablero N×N comienza vacío.
- Cada paso coloca la siguiente ficha de la secuencia en cualquier celda vacía.
- Si la componente ortogonal (sin diagonales) de fichas del mismo color que
  contiene la ficha recién colocada tiene dos o más fichas, se retira completa y
  en la celda colocada queda una ficha con la suma de sus valores. La fusión no
  encadena.
- **Victoria:** se colocaron las M fichas, aunque la última llene el tablero.
- **Derrota:** quedan fichas y no hay celdas vacías.
- **Incompleta:** el agente entregó un prefijo legal porque se le agotó el tiempo.

## Agentes

**`search`** (`tileup/agents/search.py`). Búsqueda en haz por niveles, repetida con
anchos 1, 2, 4, … hasta 1024. Poda con la cota admisible de ocupadas finales
max(D, g − 3r) y se detiene si una victoria la alcanza, porque entonces es óptima.
Entre celdas que dejan las mismas ocupadas prefiere las que no tapan fichas de
colores que vuelven a salir. La implementación es incremental (índice de fichas
por color, candidatos generados en orden sin recorrer todo el tablero, huellas
de Zobrist para los repetidos) y evalúa a los hijos sin construirlos: solo
construye los que entran al haz.

| Parámetro | Valor | Significado |
|---|---|---|
| `ancho_max` | 1024 | ancho máximo del haz |
| presupuesto | max(M, ⌊60 000·límite/N⌋) | nodos expandidos; hace al agente determinista |
| `ventana` | 10 | fichas futuras consideradas en el potencial de fusión |
| `tope` | 2 | celdas libres contadas por color en el potencial |
| `evitar_bloqueos` | sí | desempata por fichas de colores que vuelven tapadas |
| `margen` | 0,9 | fracción del límite tras la cual se detiene por tiempo |

**`evolutionary`** (`tileup/agents/evolutionary.py`). Algoritmo genético
generacional. El individuo tiene un gen de rango por ficha, y una decodificación
guiada convierte cualquier individuo en una partida legal. La regla de la
decodificación evita tapar fichas de cualquier color que vuelva a salir en la
secuencia, y se calcula de forma incremental (cubetas por clave). Se detiene en
cuanto alcanza la cota óptima.

| Parámetro | Valor | Significado |
|---|---|---|
| `poblacion` | 40 | individuos por generación |
| `torneo` | 3 | tamaño del torneo de selección |
| `prob_cruce` | 0,9 | probabilidad de cruce de dos puntos |
| `genes_mutados` | 4 | mutaciones esperadas por hijo (tasa 4/M por gen) |
| `prob_rango` | 0,3 | parámetro de la distribución geométrica de los rangos |
| `densidad_inicial` | 0,3 | fracción de genes no nulos en la población inicial |
| `elite` | 2 | mejores individuos que pasan intactos |
| presupuesto | max(1, ⌊180 000·límite/(M·√N)⌋) | evaluaciones de aptitud; hace al agente determinista |
| `margen` | 0,9 | fracción del límite tras la cual se detiene por tiempo |

Los parámetros están fijos en cada clase y no se exponen en la línea de comandos.
Los valores se eligieron con los scripts de ajuste; el procedimiento está en
`INFORME.md`.

**Qué agente usar.** Con un límite de 10 s, `search` es el mejor hasta N = 192:
completa la secuencia y llega a la cota inferior de ocupadas. Con N = 256 y
muchos colores ya no termina la pasada voraz y `evolutionary` coloca más fichas (ver
*Escalabilidad* en `INFORME.md`). En tableros chicos y muy difíciles (por ejemplo N = 6, K = 24) el
evolutivo deja menos ocupadas. Cuando se anuncien N, K y M, el ensayo
(`run.ps1 -Accion ensayo`) confirma la elección; la sección *Preparación del
concurso* del informe tiene una tabla con siete tamaños posibles.

## Pruebas

```
python -m pytest -q
```

Desde Docker: `run.ps1 -Accion test` o `make test`. Comprenden:

- **Unitarias** (`tests/unit/`):
  - motor: fusión de dos fichas, de una componente de tres o más, colocación sin
    fusión, diagonales, derrota y victoria en la última ficha;
  - parser con archivos mal formados;
  - CLI, validador y generador;
  - propiedades del juego en que se apoyan los agentes;
  - piezas de cada agente;
  - equivalencia de las versiones incrementales: deciden lo mismo que recorrer
    todo el tablero (`test_incremental.py`).
- **Integración** (`tests/integration/`): cada agente resuelve instancias pequeñas
  por la CLI y su solución se comprueba con el validador. También se prueban el
  determinismo, el límite de tiempo, el presupuesto, la batería experimental y
  el ensayo del concurso.

## Experimentos

Instancias, soluciones y resultados de todos los experimentos están versionados,
para que el informe se pueda verificar con el validador.

**Comparación** (sección *Comparación experimental* del informe):
N = 4, 6, 8; K = 4, 12, 24; M = 3N²; semillas 1–3; límite 10 s; tres agentes.
Son 81 ejecuciones y tardan unos 5 minutos.

```
python -m experiments.run_all
python -m experiments.reporte --resumen experiments/comparacion/resumen.csv --tabla experiments/comparacion/tabla.md --graficas experiments/plots --prefijo comparacion_
```

Salidas: instancias en `instances/comparacion/`, soluciones en
`solutions/comparacion/`, `resultados.csv`, `resumen.csv` (media y desviación
muestral) y `tabla.md` en `experiments/comparacion/`, y gráficas en
`experiments/plots/`.

**Escalabilidad** (sección *Escalabilidad* del informe): cinco baterías que tardan
unos 25 minutos en total. Las instancias y soluciones de las baterías extrema y
máxima pesan unos 85 MB y no se versionan: sus comandos las regeneran exactamente
y sus resultados quedan en `experiments/`.

```
python -m experiments.run_all --agentes search evolutionary --n 8 16 32 48 --k 5 25 100 --salida experiments/escalabilidad --instancias instances/escalabilidad --soluciones solutions/escalabilidad
python -m experiments.run_all --agentes search evolutionary --n 50 56 64 --k 5 25 100 --salida experiments/escalabilidad_limite --instancias instances/escalabilidad_limite --soluciones solutions/escalabilidad_limite
python -m experiments.run_all --agentes search evolutionary --n 8 16 32 --k 5 25 100 --m-fijo 192 --salida experiments/escalabilidad_m_fijo --instancias instances/escalabilidad_m_fijo --soluciones solutions/escalabilidad_m_fijo
python -m experiments.run_all --agentes search evolutionary --n 80 96 128 --k 5 25 100 --salida experiments/escalabilidad_extrema --instancias instances/escalabilidad_extrema --soluciones solutions/escalabilidad_extrema
python -m experiments.run_all --agentes search evolutionary --n 160 192 256 --k 5 25 100 --salida experiments/escalabilidad_maxima --instancias instances/escalabilidad_maxima --soluciones solutions/escalabilidad_maxima
```

Las tablas y gráficas de cada batería se generan con `experiments.reporte`,
cambiando `--resumen` y `--prefijo` y agregando `--agentes search evolutionary`.

**Ajuste de parámetros:** los comandos exactos de cada tabla están en el informe.
Los resultados quedan en `experiments/ajuste/`.

```
python -m experiments.ajuste_busqueda --salida experiments/ajuste/busqueda.csv
python -m experiments.ajuste_evolutivo --salida experiments/ajuste/evolutivo.csv
```

**Ensayo del concurso:** cuando se anuncien N, K y M, genera varias instancias con
esos valores, corre ambos agentes como en el concurso (midiendo el reloj del
proceso completo), valida cada solución y recomienda un agente según el orden del
concurso: más colocadas, menos ocupadas y menos tiempo.

```
python -m experiments.ensayo --n 20 --k 50 --m 1200 --limite 10 --semillas 1 2 3 4 5
```

Desde Docker: `run.ps1 -Accion ensayo -N 20 -K 50 -M 1200` o
`make ensayo N=20 K=50 M=1200`. Los resultados quedan en `experiments/ensayo/`.

`run_all` valida cada solución con el árbitro independiente. Los errores y los
excesos de tiempo quedan registrados, hacen retornar código 1 y no entran en los
promedios. Opciones de `run_all`:

- `--agentes`, `--n`, `--k`, `--semillas`, `--limite` y `--factor-m` (M = factor·N²);
- `--m-fijo`, que usa el mismo M en todas las configuraciones;
- `--salida`, `--instancias` y `--soluciones`, que eligen las carpetas de salida.

**Generador de instancias:**

```
python -m generator.generate --n 6 --k 12 --m 108 --semilla 1 --salida instances/nueva.txt
```

Colores uniformes en 1..K y valores en 1..9 (cambiable con `--valor-max`). La
misma semilla produce el mismo archivo.

## Estructura

| Ruta | Contenido |
|---|---|
| `tileup/engine/` | motor: tablero, colocación, fusión, victoria y derrota |
| `tileup/io/` | lectura de instancias y escritura de soluciones |
| `tileup/agents/` | interfaz común (`base.py`), `search.py`, `evolutionary.py` y `trivial.py` |
| `tileup/main.py` | línea de comandos |
| `validator/` | validador independiente |
| `generator/` | generador de instancias |
| `experiments/` | `run_all`, ajustes, `reporte`, resultados y gráficas |
| `instances/`, `solutions/` | instancias y soluciones de todos los experimentos |
| `tests/` | pruebas unitarias y de integración |
| `Dockerfile`, `Makefile`, `run.ps1` | construcción y ejecución con un solo comando |
