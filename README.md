# Tarea Corta 1 — Inteligencia Artificial

**Integrantes:** María Felix Mendez Abarca, Christian Rivas y Jozafath Perez

**Descripción:** Guía de instalación, ejecución, contratos y reproducción de la parte A.

# TileUp — Tarea Corta 1

Python 3.10 o posterior. El motor, validador, generador y experimentos utilizan
únicamente la biblioteca estándar. pytest se utiliza para pruebas.

## Ejecución reproducible

Requisito de la máquina: Docker con el servicio iniciado y acceso a la imagen de
Python y PyPI durante la primera construcción. No instalar paquetes Python a mano.
En PowerShell, desde la raíz del repositorio:

```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1
powershell -ExecutionPolicy Bypass -File .\run.ps1 -Accion test
powershell -ExecutionPolicy Bypass -File .\run.ps1 -Accion validate
```

El primer comando construye y ejecuta el ejemplo con el agente de referencia.
En Linux/macOS con Docker y Make: `make run`, `make test`,
`make validate SOLUCION=solutions/ejemplo_trivial_s1.txt`.
Las soluciones se conservan en el directorio montado del repositorio.

## Ejecución local

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m tileup.main --instancia instances/ejemplo.txt --agente trivial --semilla 1 --limite 10
.\.venv\Scripts\python.exe -m validator.validate --instancia instances/ejemplo.txt --solucion solutions/ejemplo_trivial_s1.txt
.\.venv\Scripts\python.exe -m generator.generate --n 4 --k 3 --m 48 --semilla 1 --salida instances/generada.txt
```

## Contratos y reglas

Instancia: `N K`, luego `M`, luego M líneas `color valor`. Se ignoran líneas
vacías y comentarios `#`. N y K son positivos; M puede ser cero; colores 1..K y
valores positivos. Solución: `indice fila columna` por movimiento, todos desde
cero, y última línea `# colocadas=X ocupadas=Y mayor=Z`.

El tablero comienza vacío. Cada colocación consume la siguiente ficha. Se fusiona
la componente ortogonal maximal del mismo color, conservando la suma en la celda
de colocación; no hay fusiones diagonales ni encadenadas. Colocar M fichas es
victoria, incluso si la última llena el tablero. Tablero lleno con fichas pendientes
es derrota. Un prefijo legal por agotamiento de tiempo es incompleto, y el árbitro
lo acepta con esa clasificación. Los conteos falsos y los movimientos ilegales
se rechazan. El validador implementa su propio parser y tablero sin importar tileup.

CLI: `--instancia`, `--agente`, `--semilla`, `--limite` y opcional `--salida`.
Informa colocadas, ocupadas, mayor, tiempo y esfuerzo. Códigos: 0 ejecución válida,
1 instancia inválida, 2 argumentos inválidos, 3 solución ilegal del agente.
El validador retorna 0 si es legal y 1 ante entrada o solución inválida.

## Agente de búsqueda (`search`)

Búsqueda en haz iterativa con poda por cota admisible, implementada en
`tileup/agents/search.py`. La formulación completa (estado, sucesores, costo,
meta, heurística y admisibilidad) está en `INFORME.md`.

Ejecutar y validar con Docker:

```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1 -Agente search
powershell -ExecutionPolicy Bypass -File .\run.ps1 -Accion validate -Solucion solutions/ejemplo_search_s1.txt
```

Con Make: `make run AGENTE=search` y
`make validate SOLUCION=solutions/ejemplo_search_s1.txt`. En local:

```powershell
.\.venv\Scripts\python.exe -m tileup.main --instancia instances/ejemplo.txt --agente search --semilla 1 --limite 10
```

Parámetros, fijados en `AgenteBusqueda` y no expuestos en la CLI:

| Parámetro | Valor | Significado |
|---|---|---|
| `ancho_max` | 1024 | ancho máximo del haz (se prueban 1, 2, 4, …) |
| presupuesto | max(M, ⌊60 000·límite/N⌋) | nodos expandidos; hace al agente determinista |
| `ventana` | 10 | fichas futuras consideradas en el potencial de fusión |
| `tope` | 2 | celdas libres contadas por color en el potencial |
| `margen` | 0,9 | fracción del límite tras la cual se detiene por tiempo |

El esfuerzo se informa en nodos expandidos. La semilla solo rompe empates, así
que la misma instancia, semilla y límite dan la misma solución. Pruebas propias:
`tests/unit/test_search.py` y `tests/integration/test_search.py`, que incluye
CLI + validador, determinismo y límite de tiempo.

Para reproducir el ajuste de parámetros:
`python -m experiments.ajuste_busqueda --salida experiments/ajuste_busqueda.csv`.

## Agente evolutivo (`evolutionary`)

Algoritmo genético con genes de rango por ficha y decodificación guiada,
implementado en `tileup/agents/evolutionary.py`. La formulación completa
(individuo, aptitud, selección, variación, reemplazo, paro y ajuste) está en
`INFORME.md`.

```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1 -Agente evolutionary
powershell -ExecutionPolicy Bypass -File .\run.ps1 -Accion validate -Solucion solutions/ejemplo_evolutionary_s1.txt
```

Con Make: `make run AGENTE=evolutionary`. En local:
`python -m tileup.main --instancia instances/ejemplo.txt --agente evolutionary --semilla 1 --limite 10`.

| Parámetro | Valor | Significado |
|---|---|---|
| `poblacion` | 40 | individuos por generación |
| `torneo` | 3 | tamaño del torneo de selección |
| `prob_cruce` | 0,9 | probabilidad de cruce de dos puntos |
| `genes_mutados` | 4 | mutaciones esperadas por hijo (tasa 4/M por gen) |
| `prob_rango` | 0,3 | parámetro de la distribución geométrica de rangos |
| `densidad_inicial` | 0,3 | fracción de genes no nulos en la población inicial |
| `elite` | 2 | mejores individuos que pasan intactos |
| presupuesto | max(1, ⌊100 000·límite/N³⌋) | evaluaciones de aptitud; hace al agente determinista |
| `margen` | 0,9 | fracción del límite tras la cual se detiene por tiempo |

El esfuerzo se informa en evaluaciones de aptitud. Toda la aleatoriedad sale de
`random.Random(semilla)`. Pruebas: `tests/unit/test_evolutionary.py` y
`tests/integration/test_evolutionary.py`. Para reproducir el ajuste de parámetros:
`python -m experiments.ajuste_evolutivo --salida experiments/ajuste_evolutivo.csv`.

`trivial` (primera celda libre) se conserva como referencia para pruebas y
experimentos; no sustituye a ninguno de los agentes obligatorios.

## Comparación experimental

```powershell
python -m experiments.run_all
python -m experiments.reporte --resumen experiments/comparacion/resumen.csv --tabla experiments/comparacion/tabla.md --graficas experiments/plots --prefijo comparacion_
```

También: `make experiments` o `run.ps1 -Accion experiments` (solo el primer
comando). Valores predeterminados: agentes `search`, `evolutionary` y `trivial`;
N = 4, 6, 8; K = 4, 12, 24; M = 3·N²; semillas 1, 2, 3; límite 10 s. Son nueve
configuraciones, tres semillas y tres agentes: 81 ejecuciones, que tardan unos
cinco minutos. Todos los agentes reciben las mismas instancias y semillas.

Salidas:
- instancias en `instances/comparacion/`;
- soluciones en `solutions/comparacion/`;
- resultados por ejecución y resumen con media y desviación muestral en
  `experiments/comparacion/`;
- gráficas en `experiments/plots/`.

Cada solución se valida con el árbitro independiente. Los errores y excesos de
tiempo quedan registrados y hacen retornar código 1; no se incorporan
silenciosamente al promedio.

Opciones de `run_all`:
- `--agentes`, `--n`, `--k`, `--semillas`, `--limite` y `--factor-m`;
- `--m-fijo`, que usa el mismo M en todas las configuraciones;
- `--salida`, `--instancias` y `--soluciones`, que eligen las carpetas de salida.

## Escalabilidad

Hay tres baterías, con ambos agentes, semillas 1–3 y límite de 10 s. Los
resultados y su lectura están en la sección *Escalabilidad* de `INFORME.md`.

```powershell
python -m experiments.run_all --agentes search evolutionary --n 8 16 32 48 --k 5 25 100 --salida experiments/escalabilidad --instancias instances/escalabilidad --soluciones solutions/escalabilidad
python -m experiments.run_all --agentes search evolutionary --n 50 56 64 --k 5 25 100 --salida experiments/escalabilidad_limite --instancias instances/escalabilidad_limite --soluciones solutions/escalabilidad_limite
python -m experiments.run_all --agentes search evolutionary --n 8 16 32 --k 5 25 100 --m-fijo 192 --salida experiments/escalabilidad_m_fijo --instancias instances/escalabilidad_m_fijo --soluciones solutions/escalabilidad_m_fijo
python -m experiments.reporte --resumen experiments/escalabilidad/resumen.csv --agentes search evolutionary --tabla experiments/escalabilidad/tabla.md --graficas experiments/plots --prefijo escalabilidad_
```

Las tres baterías tardan unos 20 minutos en total. Para las otras dos baterías,
`reporte` se usa igual, cambiando la carpeta y el prefijo (`limite_` o `m_fijo_`).

## Documentación y entrega

Consultar `INFORME.md` y `DECLARACION_IA.md`. El informe definitivo
requiere agentes, parámetros y resultados reales de B y C. Conservar las instancias
y soluciones experimentales para arbitraje. No subir `.venv` ni cachés. Cada
integrante debe aportar sus propios commits y poder explicar su código.

## Comprobaciones realizadas

Se verificaron las 63 pruebas localmente y dentro de Docker. También se construyó
la imagen y se ejecutaron run.ps1 -Accion run y -Accion validate: el ejemplo dio
victoria y el árbitro confirmó 6 colocadas, 4 ocupadas y mayor 5.

Con el agente de búsqueda integrado pasan 78 pruebas, localmente, con
`run.ps1 -Accion test` y con `make test`. Con Docker, `run.ps1 -Agente search` y
`make run AGENTE=search` resuelven el ejemplo con victoria y 3 ocupadas (el
óptimo), y el validador lo acepta.
