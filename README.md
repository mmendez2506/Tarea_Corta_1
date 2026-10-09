# TileUp — Tarea Corta 1
IC-6200 Inteligencia Artificial

**Integrantes:** María Felix Mendez Abarca, Cristhian Rivas y Jozafath Perez

## Descripción

En este proyecto desarrollamos dos agentes para jugar TileUp.

Uno de los agentes trabaja con un algoritmo de búsqueda y el otro utiliza un
algoritmo evolutivo. Para poder probarlos también desarrollamos el motor del juego,
un validador, un generador de instancias y diferentes pruebas.

Además hicimos varios experimentos para comparar los dos agentes y ver cómo se
comportan cuando cambia el tamaño del problema.

La explicación más detallada de los agentes y los resultados obtenidos se encuentra
en [`INFORME.md`](INFORME.md). El uso de herramientas de inteligencia artificial se
explica en [`DECLARACION_IA.md`](DECLARACION_IA.md).

## Requisitos

La forma principal de ejecutar el proyecto es con Docker.

- **Docker** con el servicio iniciado. Es lo único necesario: la imagen instala
  Python 3.12 y pytest durante la construcción, lo que requiere acceso a internet
  la primera vez.
- Para los comandos cortos: **PowerShell** en Windows (`run.ps1`) o **Make** en
  Linux o macOS (`Makefile`).
- Opcional, para ejecutar sin Docker: Python 3.10 o una versión más reciente. El
  código usa solo la biblioteca estándar; para las pruebas utilizamos pytest.

## Ejecución

Los comandos se deben ejecutar desde la carpeta principal del proyecto.

Con ellos se puede correr cualquiera de los agentes, validar una solución, ejecutar
las pruebas o correr los experimentos.

Cada agente recibe una instancia, una semilla y un límite de tiempo.

La semilla permite que una ejecución se pueda repetir con las mismas condiciones.
Además, los agentes controlan el tiempo disponible para evitar pasarse del límite
y devuelven la mejor solución encontrada hasta ese momento.

### Con un solo comando (Docker)

Cada comando construye la imagen y ejecuta dentro del contenedor.

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

Docker solo ve la carpeta del repositorio. Para ejecutar una instancia nueva,
cópiela primero dentro del repositorio (por ejemplo en `instances/`) y pase esa
ruta relativa en `-Instancia` o `INSTANCIA=`.

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

### Sin Docker

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m tileup.main --instancia instances/ejemplo.txt --agente search --semilla 1 --limite 10
.\.venv\Scripts\python.exe -m validator.validate --instancia instances/ejemplo.txt --solucion solutions/ejemplo_search_s1.txt
```

En Linux/macOS se usa `.venv/bin/python` en lugar de `.\.venv\Scripts\python.exe`.

### Línea de comandos

```
python -m tileup.main --instancia RUTA --agente {search,evolutionary,trivial} [--semilla S] [--limite SEGUNDOS] [--salida RUTA]
```

- `--semilla` vale 0 por defecto y `--limite` vale 10 segundos.
- Toda la aleatoriedad sale de la semilla. Cada agente trabaja con un presupuesto
  fijo de nodos o evaluaciones, así que la misma instancia, agente, semilla y
  límite producen la misma solución siempre que el agente termine por
  presupuesto o por llegar al óptimo. Si el reloj lo corta antes (tableros muy
  grandes, límites muy bajos o una máquina lenta), entrega una solución legal,
  pero puede cambiar de una ejecución a otra porque depende de la velocidad de
  la máquina.
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
tiempo_s=0.0003            # tiempo del agente
tiempo_total_s=0.0021      # toda la ejecución: lectura, agente, verificación y escritura
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

## Validador

El proyecto tiene un validador separado del motor principal.

Su función es volver a ejecutar los movimientos de una solución y comprobar que
realmente sean válidos según las reglas de TileUp.

Por ejemplo, revisa que no se coloque una ficha en una posición ocupada, que las
coordenadas estén dentro del tablero y que las fichas se coloquen en el orden
correcto.

Al final también comprueba que los datos de la solución coincidan con el resultado
obtenido.

```
python -m validator.validate --instancia RUTA --solucion RUTA
```

Reproduce la partida con su propio parser y su propio tablero (no importa nada de
`tileup/`). Rechaza celdas ocupadas, posiciones fuera del tablero, índices fuera de
orden, movimientos después del final y resúmenes que no coinciden. Si la
solución es legal, informa `legal=si`, el resultado, las colocadas, las ocupadas
y la ficha mayor, y retorna 0; si no, retorna 1.

## Reglas de TileUp

El juego comienza con un tablero vacío de tamaño N x N.

En cada turno se debe colocar la siguiente ficha de la secuencia en una posición
vacía.

Cuando la ficha colocada queda conectada de forma horizontal o vertical con otras
fichas del mismo color se revisa el grupo que se formó. Si hay dos o más fichas,
estas se fusionan y en la posición donde se hizo la última jugada queda una sola
ficha con la suma de sus valores.

Las diagonales no cuentan para formar grupos y una fusión no provoca otra fusión
automáticamente.

Se gana cuando se logra colocar toda la secuencia de fichas, aunque la última
ficha llene el tablero.

Si todavía quedan fichas por colocar y el tablero ya no tiene espacios disponibles,
la partida termina en derrota.

Si el agente se queda sin tiempo antes de terminar, entrega las jugadas que logró
hacer y el resultado se reporta como incompleto.

## Agente de búsqueda

El primer agente (`search`, en `tileup/agents/search.py`) utiliza una búsqueda en
haz.

La idea es mantener solamente una cantidad limitada de las mejores opciones en
cada paso en lugar de guardar todos los estados posibles.

El ancho empieza pequeño y va aumentando poco a poco hasta llegar al máximo
establecido.

También usamos una cota para descartar estados que ya no tienen posibilidad de
mejorar la mejor solución encontrada.

Se agregaron algunas mejoras para reducir la cantidad de trabajo que hace el agente,
principalmente evitando recorrer o construir estados cuando no es necesario.

### Formulación

- **Estado:** el par (tablero, i), donde el tablero es la tupla de N² celdas del
  motor (`None` o `(color, valor)`) e i es el índice de la siguiente ficha. El
  estado inicial es (tablero vacío, 0).
- **Operador de sucesión:** para cada celda vacía c, colocar la ficha i en c con
  el motor produce (tablero', i+1). El factor de ramificación es la cantidad de
  celdas vacías.
- **Costo:** cada acción cuesta el cambio en celdas ocupadas, 1 − s(c), donde s(c)
  es la cantidad de vecinos del mismo color que se fusionan (rango −3..1). El
  costo de un camino es la cantidad de celdas ocupadas.
- **Prueba de meta:** i = M, es decir, se colocaron todas las fichas. Un estado con
  fichas pendientes y sin celdas vacías es una derrota y no se expande.
- **Cota admisible (poda):** L = max(D, g − 3r), con D los colores distintos en el
  tablero o en las fichas restantes, g las ocupadas y r las fichas restantes. Es
  admisible porque la fusión nunca elimina un color y cada colocación libera a lo
  sumo 3 celdas. Se poda todo estado con L mayor o igual que la mejor victoria.
- **Heurística del haz (no admisible, declarada):** ordena por menos ocupadas y
  luego por mayor potencial de fusión con las próximas fichas. Como el haz descarta
  estados, se pierden la optimalidad y la completitud. Si una victoria alcanza la
  cota de colores distintos, es óptima.

### Parámetros

| Parámetro | Valor | Significado |
|---|---|---|
| `ancho_max` | 1024 | ancho máximo del haz |
| presupuesto | max(M, ⌊60 000·límite/N⌋) | nodos expandidos; hace al agente determinista |
| `ventana` | 10 | fichas futuras consideradas en el potencial de fusión |
| `tope` | 2 | celdas libres contadas por color en el potencial |
| `evitar_bloqueos` | sí | desempata por fichas de colores que vuelven tapadas |
| `margen` | 0,9 | fracción del límite tras la cual se detiene por tiempo |

Los valores se eligieron con `experiments/ajuste_busqueda.py`; el procedimiento
está en `INFORME.md`.

## Agente evolutivo

El segundo agente (`evolutionary`, en `tileup/agents/evolutionary.py`) utiliza un
algoritmo genético.

Cada individuo representa una posible forma de tomar las decisiones durante la
partida. A partir de esa representación se genera una secuencia de movimientos
válidos.

La calidad de cada individuo depende primero de cuántas fichas logra colocar y
después de cuántas posiciones quedan ocupadas.

Para crear nuevas soluciones utilizamos selección por torneo, cruce, mutación y
elitismo.

El proceso continúa hasta que se termina el presupuesto disponible, se alcanza
el límite de tiempo o se encuentra una solución que ya no se puede mejorar según
la cota utilizada.

### Formulación

- **Individuo:** M enteros no negativos, un gen de rango por ficha. Para cada
  ficha, la decodificación ordena las celdas vacías por una regla local (más
  fusión, menos sitios de fusión futuros tapados, menos vecinos vacíos) y elige
  la que está en la posición del gen. Todo individuo es una partida legal.
- **Aptitud:** f = colocadas·(N² + 1) − ocupadas, equivalente al orden del
  concurso.
- **Selección:** torneo de tamaño 3.
- **Variación:** cruce de dos puntos con probabilidad 0,9 y mutación por gen con
  probabilidad 4/M, que cambia el gen por un rango aleatorio.
- **Reemplazo:** generacional con elitismo; los 2 mejores pasan intactos y el resto
  de la nueva población son hijos.
- **Criterio de paro:** lo primero que ocurra entre agotar el presupuesto de
  evaluaciones (determinista), llegar al 90 % del límite de tiempo o encontrar una
  victoria con ocupadas igual a la cota de colores distintos. Se devuelve el mejor
  individuo visto.
- **Parámetros:** los de la tabla anterior, fijados con
  `experiments/ajuste_evolutivo.py` (barrido de una variante por vez con
  presupuesto fijo y validación con semillas nuevas, ver `INFORME.md`).

### Parámetros

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

### Qué agente usar

Con un límite de 10 s, `search` es el mejor hasta N = 192:
completa la secuencia y llega a la cota inferior de ocupadas. Con N = 256 y
muchos colores ya no termina la pasada voraz y `evolutionary` coloca más fichas (ver
*Escalabilidad* en `INFORME.md`). En tableros chicos y muy difíciles (por ejemplo N = 6, K = 24) el
evolutivo deja menos ocupadas. Cuando se anuncien N, K y M, el ensayo
(`run.ps1 -Accion ensayo`) confirma la elección; la sección *Preparación del
concurso* del informe tiene una tabla con siete tamaños posibles.

## Pruebas

Se hicieron pruebas unitarias y pruebas de integración.

Las pruebas unitarias revisan por separado las partes principales del proyecto.
Entre ellas están las fusiones de fichas, movimientos sin fusión, victoria, derrota,
lectura de instancias, validador, generador y diferentes funciones utilizadas por
los agentes.

Las pruebas de integración revisan el funcionamiento completo. Se ejecuta un agente,
se genera una solución y después esa solución se pasa por el validador.

También se hicieron pruebas para revisar que los resultados sean reproducibles al
utilizar las mismas semillas y que los agentes respeten el límite de tiempo.

Para correr todas las pruebas:

```
python -m pytest -q
```

Desde Docker: `powershell -ExecutionPolicy Bypass -File .\run.ps1 -Accion test` o
`make test`.

## Experimentos

Para comparar los agentes se utilizaron diferentes combinaciones de N, K y M y
varias semillas para cada configuración.

En cada ejecución guardamos los resultados para después comparar el desempeño de
los agentes.

También hicimos pruebas de escalabilidad aumentando el tamaño de los problemas.
Esto nos permitió observar cómo cambia el comportamiento de los agentes cuando
aumenta el tablero, la cantidad de colores o la cantidad de fichas.

Los resultados, tablas y gráficas utilizadas para el análisis se encuentran dentro
de la carpeta `experiments`. Las instancias y soluciones están en `instances/` y
`solutions/`, para que el informe se pueda verificar con el validador.

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

## Generador de instancias

También se desarrolló un generador para crear nuevas instancias de TileUp.

Se puede indicar el tamaño del tablero, la cantidad de colores, la cantidad de
fichas y una semilla.

Usar una semilla permite volver a generar exactamente la misma instancia.

```
python -m generator.generate --n 6 --k 12 --m 108 --semilla 1 --salida instances/nueva.txt
```

Colores uniformes en 1..K y valores en 1..9 (cambiable con `--valor-max`). La
misma semilla produce el mismo archivo.

## Estructura del proyecto

El proyecto se separó en diferentes carpetas para mantener cada parte organizada.

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
