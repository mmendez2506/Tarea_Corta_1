# Tarea Corta 1 — Inteligencia Artificial

**Integrantes:** María Felix Mendez Abarca, Christian Rivas y Jozafath Perez

**Descripción:** Descripción del motor, árbitro y metodología de escalabilidad de la parte A.

# Informe de TileUp

Estado: infraestructura de A implementada; comparación final pendiente de B y C.

## Motor y validador (A)

El motor guarda el tablero en una tupla que no se modifica. Cada colocación crea otro tablero. La siguiente ficha
se determina por la cantidad de colocaciones realizadas. Cada sucesor aplica la
regla de fusión mediante recorrido de las fichas conectadas por arriba, abajo, izquierda y derecha del mismo color.
La suma se conserva y el nuevo tablero permite explorar sucesores sin modificar
otros estados. La comprobación de coordenadas ocurre antes de convertir al índice.
La victoria tiene prioridad sobre la derrota al colocar la última ficha.

El árbitro utiliza un diccionario de posiciones y una pila para la componente.
No comparte imports con tileup ni código de decisión con los agentes. Comprueba
formato, orden de índices, límites de posiciones, ocupación, finalización y los tres
valores del resumen. Acepta prefijos legales incompletos para el caso de tiempo
agotado. La legalidad no implica victoria ni que el agente sea competitivo.

## Formulación del agente de búsqueda (B)

**Algoritmo.** Búsqueda en haz (*beam search*) por niveles, repetida con anchos
crecientes (1, 2, 4, 8, …) mientras quede presupuesto, y con poda por cota
admisible (ramificación y acotamiento). El nivel i contiene los estados con las
fichas 0..i−1 ya colocadas. Se descartó A* completo: el factor de ramificación es
la cantidad de celdas vacías y la profundidad es M, de modo que la frontera crece
como e! y no cabe en memoria ni en el límite de tiempo para N ≥ 3.

**Estado.** El par (tablero, i): la tupla plana de N² celdas del motor (`None` o
`(color, valor)`) y el índice de la siguiente ficha. El nodo guarda además la lista
de colocaciones para reconstruir la solución. El estado inicial es
(`tablero_vacio(N)`, 0).

**Operador de sucesión.** Para cada celda vacía c, `colocar(tablero, N, fichas[i], c)`
produce (tablero', i+1). La ramificación es exactamente e, la cantidad de celdas
vacías. El agente nunca modifica un tablero: siempre usa `colocar`.

**Propiedad usada.** En todo tablero alcanzable no hay dos fichas ortogonalmente
adyacentes del mismo color: una ficha que no se fusiona no toca su color, y la
fusión absorbe la componente maximal. Por eso la componente de la ficha colocada
es la celda más sus vecinos del mismo color, y al colocar en c se cumple
Δocupadas = 1 − s(c), donde s(c) ∈ {0..4} cuenta esos vecinos. El efecto de cada
movimiento se calcula sin construir el sucesor.

**Costo.** El costo de una acción es Δocupadas = 1 − s(c), que está en el rango
−3..1. El costo de un camino es la cantidad de celdas ocupadas, g = `ocupadas(tablero)`.
Todas las metas están a la misma profundidad M, así que minimizar g en la meta
coincide con el segundo criterio del concurso.

**Prueba de meta.** i = M: se colocaron todas las fichas (victoria, aunque la última
llene el tablero). Un estado con i < M y sin celdas vacías es un callejón sin salida
(derrota) y no se expande.

**Orden de preferencia entre soluciones.** Es el mismo del concurso: primero más
fichas colocadas, luego menos celdas ocupadas. El agente conserva siempre la mejor
solución vista, completa o parcial.

**Cota admisible (para poda).** Sean r = M − i las fichas restantes y D la cantidad
de colores distintos presentes en el tablero o en las fichas restantes. En una
meta queda al menos una ficha de cada uno de esos colores, porque la fusión nunca
elimina un color. Además, cada colocación reduce las ocupadas en a lo sumo 3. Por
tanto las ocupadas finales son al menos L = max(D, g − 3r), y h = L − g nunca
sobreestima el costo restante: es admisible. Se comprobó empíricamente en 5514
estados de partidas aleatorias, sin ningún caso donde L superara el valor final.
Uso: si ya se tiene una victoria con ocupadas = B, se poda todo estado con L ≥ B.
Esta poda no descarta ninguna solución mejor.

**Evaluación del haz (no admisible, declarada).** Para elegir qué W estados pasan
al siguiente nivel se ordena por una evaluación heurística: primero menos celdas
ocupadas y luego mayor potencial de fusión. El potencial se mide como las celdas
vacías adyacentes a fichas del color de las próximas fichas de la secuencia, con
peso decreciente según la distancia en la secuencia; la ventana y el tope se
fijaron con el procedimiento de ajuste descrito más abajo. Esta evaluación no es
una cota y el haz descarta estados, así que **se renuncia a la optimalidad y a la
completitud**: puede devolver una solución con más celdas ocupadas que la óptima,
o una derrota en una instancia que sí admite victoria. A cambio, cada nivel cuesta
O(W·e) en puntuar candidatos más O(W·N²) en construir y evaluar hasta 4·W hijos,
y el tiempo es predecible.

**Estados repetidos.** En cada nivel se descartan los tableros repetidos y se
conserva el primero según el orden del haz. Colocadas y ocupadas dependen solo de
los colores, así que la llave es la tupla de colores del tablero. Dos estados con
los mismos colores tienen el mismo futuro en el concurso, porque el valor solo
afecta `mayor`. También se probó identificar las 8 simetrías del cuadrado, pero
se descartó en el ajuste porque no mejoró los resultados y triplicó el costo.

**Presupuesto, tiempo y determinismo.** El presupuesto principal es una cantidad
de nodos expandidos, que es determinista. El tiempo es solo una red de seguridad:
el agente se detiene al 90 % de `limite_s`. Si el plazo corta una iteración, se
devuelve la mejor solución encontrada (la más larga y, a igual largo, con menos
ocupadas), que siempre es un prefijo legal. Mientras el presupuesto de nodos se
agote antes que el tiempo, la misma instancia y la misma semilla producen la
misma solución en cualquier máquina. Si es el reloj el que corta, el resultado
puede variar entre máquinas, y este caso se reporta. Los empates en la evaluación
se rompen con un orden aleatorio de celdas tomado de `random.Random(semilla)`.

**Esfuerzo.** Nodos expandidos: estados del haz a los que se les generaron
sucesores.

**Parada anticipada.** La cota en la raíz es la cantidad de colores distintos de
la secuencia. Si una victoria la alcanza, es óptima y la búsqueda termina sin
ensanchar más el haz.

**Parámetros.** Ancho máximo 1024, ventana de 10 fichas para el potencial con
pesos 1, 1/2, 1/4, …, tope de 2 celdas por color, sin término de dobles, orden
lexicográfico (ocupadas, −potencial) y sin identificar simetrías. El presupuesto
es de ⌊60 000·`limite_s`/N⌋ nodos, con corte de tiempo al 90 %. En cada nivel se
construyen como máximo 4·W hijos antes del corte del haz.

**Procedimiento de ajuste.** El script `experiments/ajuste_busqueda.py` corre
cada variante sobre un conjunto de ajuste del régimen de muchos colores:
(N, K) ∈ {(4,12), (5,16), (6,24), (7,32)}, M = 3N², semillas 101–103, distintas de
las de pruebas y de la batería. Usa un presupuesto fijo de 30 000 nodos para que
la comparación no dependa del reloj. El criterio es el del concurso: victorias,
luego colocadas, luego ocupadas.

| Variante (conjunto de ajuste) | Victorias | Colocadas | Ocupadas en victorias |
|---|---|---|---|
| base (ventana 3) | 12/12 | 1134 | 272 |
| sin potencial | 11/12 | 1119 | 258 |
| ventana 1 | 11/12 | 1121 | 244 |
| ventana 5 | 12/12 | 1134 | 264 |
| ventana 10 | 12/12 | 1134 | **255** |
| tope 1 / tope 4 | 12/12 / 11/12 | 1134 / 1133 | 281 / 239 |
| dobles 0,5 / 1 | 12/12 | 1134 | 272 / 271 |
| combinado α = 0,5 / 1 | 12/12 | 1134 | 272 / 273 |
| simetrías | 12/12 | 1134 | 272 (2,5× más lento) |

Quitar el potencial o acortar la ventana cuesta victorias, así que la
anticipación de colores sí aporta. Se eligió la ventana 10 y se validó con
semillas nuevas (201–206): 24/24 victorias frente a 22/24 de la base. Con
secuencias más largas (M = 5N²) obtuvo 6/12 frente a 4/12. Las simetrías no
mejoran nada y triplican el costo, por lo que se descartaron.

**Presupuesto.** Con la ventana 10 y M = 5N², pasar de 30 000 a 100 000 nodos sube
las victorias de 6/12 a 10/12, y de 200 000 a 400 000 no aporta casi nada. El
ritmo medido baja aproximadamente como 1/N: unos 36 000 nodos/s con N = 4, 20 000
con N = 8 y 8 000 con N = 15. Un presupuesto fijo de 200 000 nodos tardaba 9,4 s
con N = 7, al borde del corte de tiempo. Por eso el presupuesto se escala como
60 000·`limite_s`/N: en esta máquina consume cerca de la mitad del límite, lo que
deja el doble de margen para que en una máquina más lenta termine el presupuesto
(determinista) y no el reloj.

**Resultados tras el ajuste (límite 10 s, 3 semillas).** En la batería por
defecto (N = 2..4, K = 2, 3, 5) `search` gana todas las configuraciones con
N ≥ 3 y deja ocupadas = K, que es la cota admisible, es decir, el óptimo. Con
N = 2 y K = 3 o 5 ninguna instancia admite victoria: una búsqueda exhaustiva
sobre los tableros de colores lo confirma, y `search` coloca exactamente el
máximo posible en las seis instancias. En una batería difícil (N = 5..7,
K = 16, 24, 32) gana 18 de 27 ejecuciones, mientras que `trivial` no gana
ninguna. Ninguna ejecución excedió el límite, y el promedio más alto fue 3,9 s.

### Comportamiento del agente de búsqueda al escalar

Datos en `experiments/busqueda/`: instancias, soluciones, `resultados.csv`,
`resumen.csv` y `tiempos.svg` por batería. Todas las corridas usan `run_all`,
límite de 10 s, M = 3N² y semillas 1–3. Todas las soluciones pasaron por el
validador.

- **Propuesta de comparación** (`comparacion/`, N ∈ {4, 6, 8}, K ∈ {4, 12, 24}):
  `search` gana 24 de 27 ejecuciones y `trivial` gana 2. Las tres derrotas de
  `search` son en N = 4, K = 24, donde la secuencia tiene 21–22 colores distintos
  para 16 celdas. Por la cota admisible, ahí ninguna victoria es posible.
- **Escalabilidad media** (`escalabilidad/`, N ∈ {6, 10, 15}, K ∈ {5, 20, 60}):
  gana todo salvo N = 6, K = 60, donde también es imposible (47–54 colores para
  36 celdas). En las 27 ejecuciones el presupuesto se agotó antes que el reloj,
  así que todas son deterministas. El tiempo máximo fue 5,4 s.
- **Escalabilidad grande** (`escalabilidad_grande/`, N ∈ {20, 30, 50},
  K ∈ {10, 100, 400}):

| N | K | Victorias | Colocadas (media ± d.e.) | Tiempo medio | Régimen |
|---|---|---|---|---|---|
| 20 | 10 / 100 | 3/3 / 3/3 | 1200 ± 0 | 0,25 / 6,8 s | presupuesto, determinista |
| 20 | 400 | 0/3 | 621 ± 14 de 1200 | 6,0 s | presupuesto; 376–385 colores en 400 celdas, imposibilidad no probada |
| 30 | 10 / 100 | 3/3 / 3/3 | 2700 ± 0 | 1,2 / 2,1 s | presupuesto, determinista |
| 30 | 400 | 3/3 | 2700 ± 0 | 9,0 s | corta el reloj |
| 50 | 10 / 100 / 400 | 0/3 cada una | 6810 / 6749 / 6197 de 7500 | 9,0 s | ni el ancho 1 termina: solución incompleta |

**Lectura.** El costo lo domina N, pero no por la ramificación sino por el largo
de la secuencia. Con M = 3N², una sola pasada de ancho 1 hace M expansiones, y
cada una recorre las N² celdas y copia el tablero, lo que da O(N⁴). La calidad la
domina la proporción de colores por celda, K/N²:

- Si K/N² es pequeño, el ancho 1 ya alcanza la cota (óptimo) y la búsqueda se
  detiene casi de inmediato.
- Si la secuencia tiene más colores distintos que celdas, la victoria es
  imposible y la cota lo detecta.
- Entre esos dos extremos el haz ancho es el que marca la diferencia.

Con límite de 10 s, el agente es determinista hasta N ≈ 20. Con N = 30–40 y
muchos colores corta el reloj, pero todavía gana. Hacia N ≈ 50 deja de terminar
dentro del límite y entrega un prefijo legal de alrededor del 90 % de la
secuencia.

### Garantías y limitaciones del agente de búsqueda

- **Legalidad:** siempre. Solo se usa `colocar` del motor, y la solución devuelta
  es la secuencia de colocaciones de un nodo alcanzado, es decir, un prefijo legal.
- **Óptimo certificado:** cuando una victoria deja ocupadas igual a la cantidad de
  colores distintos de la secuencia, es óptima. Esto ocurrió en todas las
  instancias con K ≤ 5 y en la mayoría con K ≤ N²/4.
- **Imposibilidad certificada:** si la secuencia tiene más colores distintos que
  celdas, ninguna victoria es posible. Todas las derrotas observadas con N ≤ 15
  cumplen esta condición.
- **Sin garantía de completitud ni de optimalidad** en el resto de los casos, por
  la evaluación no admisible y el ancho limitado.
- **Determinismo condicionado al presupuesto:** con la misma instancia, semilla y
  límite el resultado es idéntico mientras el presupuesto de nodos se agote antes
  que el 90 % del límite (N ≤ 20 con 10 s en la máquina de prueba).
- **Costo por tamaño:** cada expansión recorre y copia el tablero completo, así
  que una pasada cuesta O(M·N²). Una evaluación incremental (vecinos y potencial
  actualizados por cambio) extendería el rango de N en el que termina a tiempo.

## Formulación del agente evolutivo

**Familia.** Algoritmo genético generacional con elitismo, implementado en
`tileup/agents/evolutionary.py` (clave `evolutionary` en la CLI). Se usa
codificación por **rangos con decodificación guiada**: el genoma no fija celdas
absolutas, sino cuánto se aparta cada colocación de la jugada que una regla local
considera mejor.

**Individuo.** Una lista de M enteros no negativos g₀ … g_{M−1}, uno por ficha
de la secuencia.

**Decodificación.** Se parte del tablero vacío y se recorren las fichas en orden.
Para la ficha i, cada celda vacía c recibe la clave
(−s(c), b(c), l(c), c), donde:

- s(c) es la cantidad de vecinos del mismo color, es decir, cuántas fichas absorbe
  la fusión;
- b(c) es la cantidad de vecinos de otro color que aparece entre las 10 fichas
  siguientes (colocar ahí tapa un sitio de fusión futuro);
- l(c) es la cantidad de vecinos vacíos;
- el índice c rompe empates.

El orden es ascendente: primero más fusión, luego menos sitios tapados y luego
menos vecinos vacíos, para no fragmentar zonas libres. Se elige la celda que ocupa la posición mín(gᵢ, e−1) en ese orden, con e las
celdas vacías, y se aplica `colocar` del motor. Si no quedan celdas vacías la
partida termina en derrota y el resto de genes no se usa. Así **todo individuo
decodifica a una partida legal**, y el gen 0 equivale a la jugada voraz. La regla
local se eligió comparando cuatro variantes sobre 15 instancias difíciles: penalizar
b(c) subió las fichas colocadas por la regla voraz de 900 a 1539.

**Aptitud.** f = colocadas·(N² + 1) − ocupadas. Como las ocupadas nunca superan
N², una ficha colocada más siempre pesa más que cualquier diferencia de ocupadas,
de modo que maximizar f equivale al orden del concurso (más colocadas, luego menos
ocupadas). Cada decodificación cuenta como una evaluación; el esfuerzo informado
es la cantidad de evaluaciones.

**Población inicial.** P = 40 individuos. El primero es todo ceros (la jugada voraz);
en los demás cada gen vale 0 salvo con probabilidad 0,3, en cuyo caso toma un rango
aleatorio.

**Rango aleatorio.** Distribución geométrica: r = 0 y se incrementa mientras un
número aleatorio sea menor que 0,3. Favorece desviaciones pequeñas de la jugada
voraz (P(r = 0) = 0,7, P(r = 1) = 0,21, …).

**Selección.** Torneo de tamaño 3: se toman 3 individuos al azar y gana el de mayor
aptitud.

**Variación.** Cruce de dos puntos con probabilidad 0,9 (el hijo toma de un padre los
genes fuera del segmento y del otro los de dentro). Mutación por gen con probabilidad
4/M, es decir, unas 4 colocaciones cambiadas por hijo, que reemplaza el gen por un
rango aleatorio.

**Reemplazo.** Generacional con elitismo: los 2 mejores pasan intactos y el resto
de la nueva población son hijos.

**Criterio de paro.** El primero de:

- agotar el presupuesto de ⌊100 000·`limite_s`/N³⌋ evaluaciones, que es determinista;
- llegar al 90 % del límite de tiempo, como red de seguridad;
- encontrar una victoria con ocupadas igual a la cantidad de colores distintos de
  la secuencia, que es la cota óptima.

Se devuelve el mejor individuo visto.

**Semilla.** Toda la aleatoriedad (población inicial, torneos, cruces, mutaciones)
sale de un único `random.Random(semilla)`. La decodificación es determinista. Con la
misma instancia, semilla y límite el resultado es idéntico mientras el presupuesto
se agote antes que el reloj.

**Presupuesto.** Cada evaluación simula la partida entera: M = 3N² colocaciones, y
cada una recorre las N² celdas. El ritmo medido fue de unas 300 000/N³ evaluaciones
por segundo (de N = 4 a 20) aislado, y de unas 240 000/N³ dentro de la batería
completa. Con 100 000/N³ evaluaciones por segundo de límite, el agente usa entre un
tercio y la mitad del tiempo; el resto es margen para máquinas más lentas, donde de
otro modo cortaría el reloj y se perdería el determinismo.

**Procedimiento de ajuste.** El script `experiments/ajuste_evolutivo.py` corre cada
variante con un presupuesto fijo de 1500 evaluaciones (independiente del reloj)
sobre el mismo conjunto de ajuste que el agente de búsqueda: (N, K) ∈ {(4,12),
(5,16), (6,24), (7,32)}, M = 3N², semillas 101–103. Se partió de una base de 2 genes
mutados y densidad inicial 0,1, y cada variante cambia un solo parámetro. El
criterio es el del concurso.

| Variante (conjunto de ajuste) | Victorias | Colocadas | Ocupadas |
|---|---|---|---|
| voraz (solo el individuo inicial) | 5/12 | 908 | 348 |
| base | 11/12 | 1103 | 292 |
| sin cruce | 11/12 | 1108 | 296 |
| población 20 / 80 | 10/12 / 10/12 | 1083 / 1096 | 293 / 295 |
| torneo 2 / 5 | 10/12 / 10/12 | 1106 / 1090 | 293 / 300 |
| 1 / 4 / 6 genes mutados | 10/12 / 11/12 / 11/12 | 1104 / 1114 / 1121 | 298 / 293 / 291 |
| rango 0,15 / 0,5 | 10/12 / 10/12 | 1093 / 1102 | 300 / 293 |
| densidad inicial 0 / 0,3 | 10/12 / 11/12 | 1088 / 1097 | 294 / 287 |
| élite 1 / 5 | 11/12 / 11/12 | 1095 / 1095 | 292 / 288 |
| 4 genes mutados + densidad 0,3 | 11/12 | 1110 | **284** |

Las diferencias entre variantes son pequeñas frente a la que hay con la regla
voraz sola. Por eso las mejores se validaron con semillas nuevas (201–206,
24 instancias):

| Variante (validación) | Victorias | Colocadas | Ocupadas |
|---|---|---|---|
| voraz | 5/24 | 1712 | 743 |
| base | 19/24 | 2239 | 598 |
| sin cruce | 20/24 | 2244 | 611 |
| 4 genes mutados | 20/24 | 2256 | 604 |
| 6 genes mutados | 19/24 | 2231 | 615 |
| densidad 0,3 | 19/24 | 2237 | 596 |
| **4 genes mutados + densidad 0,3** | **23/24** | **2261** | **598** |

Se eligió la última. La evolución es la que produce la mejora: con el mismo
presupuesto, el AG gana 23 de 24 instancias de validación y la regla voraz que
usa para decodificar solo 5. El cruce aporta poco (sin cruce: 20/24 frente a
19/24 de la base), lo que indica que la mutación es el operador principal. Se
mantiene el cruce porque no empeora el resultado y combina segmentos buenos de
distintas partidas.

**Limitaciones.** El significado de un gen depende de las colocaciones anteriores
(epistasis): el mismo rango apunta a otra celda si cambia el prefijo, y eso limita
lo que puede transmitir el cruce. Cada evaluación cuesta O(M·N²), así que en
tableros grandes el presupuesto alcanza para pocas generaciones.

## Comparación experimental

### Metodología

- **Instancias.** `generator/generate.py`: colores uniformes en 1..K, valores en
  1..9, generador aleatorio local con semilla. Nueve configuraciones:
  N ∈ {4, 6, 8} × K ∈ {4, 12, 24}, con M = 3N² y semillas 1, 2 y 3, para 27
  instancias. K cubre tres regímenes: pocos colores, una cuarta parte de las
  celdas del tablero menor y más colores que celdas en N = 4. La batería por
  defecto original (N ≤ 4, K ≤ 5) se descartó porque ambos agentes alcanzan el
  óptimo con la regla voraz y no se distinguen.
- **Ejecución.** `python -m experiments.run_all`, el comando por defecto, que
  también corre con `make experiments` y `run.ps1 -Accion experiments`. Cada
  agente recibe el mismo archivo, la misma semilla y un límite de 10 s. Se incluye
  `trivial` (primera celda libre) como referencia.
- **Validación.** Cada solución pasa por el validador independiente, y sus métricas
  deben coincidir con las de la salida estándar. Hubo 81 ejecuciones, 0 fallos y
  ninguna excedió el límite.
- **Métricas.** Colocadas, ocupadas, tiempo de `resolver` (sin arranque del
  intérprete) y esfuerzo propio (nodos expandidos o evaluaciones de aptitud), con
  media y desviación estándar muestral entre las 3 semillas.
- **Archivos.** Instancias en `instances/comparacion/`, soluciones en
  `solutions/comparacion/`, datos en `experiments/comparacion/` (`resultados.csv`
  y `resumen.csv`) y gráficas en `experiments/plots/`. La tabla se genera con
  `python -m experiments.reporte --resumen experiments/comparacion/resumen.csv`.

La semilla cambia a la vez la instancia y la aleatoriedad del agente, así que la
dispersión mezcla ambas fuentes. El agente de búsqueda solo usa la semilla para
desempates, por lo que su dispersión es casi toda debida a la instancia.

### Resultados

| N | K | M | Agente | Victorias | Colocadas | Ocupadas | Tiempo (s) | Esfuerzo |
|---|---|---|---|---|---|---|---|---|
| 4 | 4 | 48 | `search` | 3/3 | 48.0 ± 0.0 | 4.0 ± 0.0 | 0.001 ± 0.000 | 48 ± 0 nodos |
| 4 | 4 | 48 | `evolutionary` | 3/3 | 48.0 ± 0.0 | 4.0 ± 0.0 | 0.009 ± 0.001 | 40 ± 0 evaluaciones |
| 4 | 4 | 48 | `trivial` | 0/3 | 33.7 ± 9.3 | 16.0 ± 0.0 | 0.000 ± 0.000 | 34 ± 9 colocaciones |
| 4 | 12 | 48 | `search` | 3/3 | 48.0 ± 0.0 | 12.0 ± 0.0 | 0.738 ± 0.606 | 31180 ± 25739 nodos |
| 4 | 12 | 48 | `evolutionary` | 3/3 | 48.0 ± 0.0 | 12.7 ± 1.2 | 0.879 ± 0.994 | 7021 ± 7868 evaluaciones |
| 4 | 12 | 48 | `trivial` | 0/3 | 17.3 ± 0.6 | 16.0 ± 0.0 | 0.000 ± 0.000 | 17 ± 1 colocaciones |
| 4 | 24 | 48 | `search` | 0/3 | 20.7 ± 2.1 | 16.0 ± 0.0 | 0.823 ± 0.124 | 39324 ± 4261 nodos |
| 4 | 24 | 48 | `evolutionary` | 0/3 | 20.7 ± 2.1 | 16.0 ± 0.0 | 1.169 ± 0.159 | 15625 ± 0 evaluaciones |
| 4 | 24 | 48 | `trivial` | 0/3 | 16.7 ± 0.6 | 16.0 ± 0.0 | 0.000 ± 0.000 | 17 ± 1 colocaciones |
| 6 | 4 | 108 | `search` | 3/3 | 108.0 ± 0.0 | 4.0 ± 0.0 | 0.004 ± 0.000 | 108 ± 0 nodos |
| 6 | 4 | 108 | `evolutionary` | 3/3 | 108.0 ± 0.0 | 4.0 ± 0.0 | 0.035 ± 0.001 | 40 ± 0 evaluaciones |
| 6 | 4 | 108 | `trivial` | 1/3 | 98.3 ± 8.7 | 35.3 ± 1.2 | 0.000 ± 0.000 | 98 ± 9 colocaciones |
| 6 | 12 | 108 | `search` | 3/3 | 108.0 ± 0.0 | 12.0 ± 0.0 | 0.004 ± 0.000 | 108 ± 0 nodos |
| 6 | 12 | 108 | `evolutionary` | 3/3 | 108.0 ± 0.0 | 12.0 ± 0.0 | 0.044 ± 0.017 | 53 ± 22 evaluaciones |
| 6 | 12 | 108 | `trivial` | 0/3 | 43.0 ± 3.6 | 36.0 ± 0.0 | 0.000 ± 0.000 | 43 ± 4 colocaciones |
| 6 | 24 | 108 | `search` | 3/3 | 108.0 ± 0.0 | 25.7 ± 1.5 | 2.724 ± 1.923 | 71171 ± 49933 nodos |
| 6 | 24 | 108 | `evolutionary` | 3/3 | 108.0 ± 0.0 | 26.7 ± 1.5 | 2.548 ± 0.105 | 4629 ± 0 evaluaciones |
| 6 | 24 | 108 | `trivial` | 0/3 | 39.0 ± 2.6 | 36.0 ± 0.0 | 0.000 ± 0.000 | 39 ± 3 colocaciones |
| 8 | 4 | 192 | `search` | 3/3 | 192.0 ± 0.0 | 4.0 ± 0.0 | 0.009 ± 0.000 | 192 ± 0 nodos |
| 8 | 4 | 192 | `evolutionary` | 3/3 | 192.0 ± 0.0 | 4.0 ± 0.0 | 0.101 ± 0.001 | 40 ± 0 evaluaciones |
| 8 | 4 | 192 | `trivial` | 1/3 | 166.7 ± 24.5 | 60.7 ± 5.8 | 0.001 ± 0.000 | 167 ± 25 colocaciones |
| 8 | 12 | 192 | `search` | 3/3 | 192.0 ± 0.0 | 12.0 ± 0.0 | 0.010 ± 0.000 | 192 ± 0 nodos |
| 8 | 12 | 192 | `evolutionary` | 3/3 | 192.0 ± 0.0 | 12.0 ± 0.0 | 0.129 ± 0.055 | 53 ± 22 evaluaciones |
| 8 | 12 | 192 | `trivial` | 0/3 | 76.3 ± 4.0 | 64.0 ± 0.0 | 0.000 ± 0.000 | 76 ± 4 colocaciones |
| 8 | 24 | 192 | `search` | 3/3 | 192.0 ± 0.0 | 24.0 ± 0.0 | 0.017 ± 0.012 | 320 ± 221 nodos |
| 8 | 24 | 192 | `evolutionary` | 3/3 | 192.0 ± 0.0 | 28.0 ± 4.4 | 4.054 ± 0.191 | 1953 ± 0 evaluaciones |
| 8 | 24 | 192 | `trivial` | 0/3 | 68.3 ± 3.1 | 64.0 ± 0.0 | 0.000 ± 0.000 | 68 ± 3 colocaciones |

![Tiempo de cómputo según N](experiments/plots/comparacion_tiempo.svg)

![Celdas ocupadas según N](experiments/plots/comparacion_ocupadas.svg)

### Lectura

- **Victorias.** Ambos agentes ganan las 24 instancias ganables. `trivial` gana 2.
  Las 3 instancias restantes (N = 4, K = 24) son imposibles: tienen 21–22 colores
  distintos para 16 celdas y en una victoria quedaría al menos una ficha por color.
  Ahí los dos agentes llegan a la misma derrota, 20,7 ± 2,1 colocadas.
- **Ocupadas.** Con K = 4, y con K = 12 en N ≥ 6, los dos agentes terminan con
  ocupadas = K. Es la cota inferior, es decir, el óptimo. Las diferencias aparecen
  en el régimen difícil, y siempre a favor de la búsqueda:
  - N = 4, K = 12: 12,0 frente a 12,7 ± 1,2;
  - N = 6, K = 24: 25,7 ± 1,5 frente a 26,7 ± 1,5;
  - N = 8, K = 24: 24,0 frente a 28,0 ± 4,4.

  La búsqueda nunca queda peor que el evolutivo en ninguna configuración.
- **Tiempo y esfuerzo.** La búsqueda termina en milisegundos cuando la regla voraz
  ya alcanza la cota, porque la poda la certifica como óptima. El evolutivo solo
  se detiene antes de tiempo en ese mismo caso; si no, agota su presupuesto
  completo (15 625, 4 629 y 1 953 evaluaciones para N = 4, 6, 8). Por eso su tiempo
  crece con N en K = 24 (1,2 → 2,5 → 4,1 s) mientras el de la búsqueda baja a
  0,02 s en N = 8. La excepción es N = 6, K = 24: es la configuración más ajustada
  (24 colores en 36 celdas), la búsqueda ensancha el haz hasta agotar su
  presupuesto en dos de tres semillas y queda en 2,7 ± 1,9 s, a la par del
  evolutivo. Las unidades de esfuerzo no son comparables entre agentes: un nodo
  expandido es una colocación, y una evaluación es una partida completa de M
  colocaciones.
- **Dispersión.** La del evolutivo en ocupadas crece con la dificultad (± 4,4 en
  N = 8, K = 24): con el presupuesto de evaluaciones de los tableros grandes caben
  pocas generaciones y el resultado depende más de la semilla.
- **Conclusión.** En estas instancias la búsqueda en haz domina: iguala o mejora
  al evolutivo en colocadas y ocupadas, y es más rápida salvo en el caso más
  ajustado. La explicación es estructural. La búsqueda evalúa cada colocación con
  información local exacta (Δocupadas) y poda con una cota admisible. El evolutivo
  aprende solo a través de partidas completas, y el significado de sus genes
  depende del prefijo. Para el concurso se elige el agente de búsqueda.

## Pruebas de ejecución

Se aprobaron 63 pruebas tanto localmente como en Docker. En Docker también se
ejecutó el ejemplo con el trivial y se validó su solución: victoria, 6 colocadas,
4 ocupadas y mayor 5. El contenedor instala sus dependencias durante la construcción.
