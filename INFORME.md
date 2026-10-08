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

## Formulación del agente de búsqueda (B, borrador)

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
fijaron con el procedimiento de ajuste descrito más abajo. Esta evaluación no es una cota y el haz descarta estados, así que **se
renuncia a la optimalidad y a la completitud**: puede devolver una solución con
más celdas ocupadas que la óptima, o una derrota en una instancia que sí admite
victoria. A cambio, cada nivel cuesta O(W·e) y el tiempo es predecible.

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

## Formulación del evolutivo (C, pendiente)

Documentar individuo, decodificación legal, aptitud alineada al orden del concurso,
selección, variación, reemplazo, paro, semilla y parámetros. Explicar el procedimiento
experimental utilizado para fijar los parámetros, no solo sus valores.

## Metodología de comparación y escalabilidad (A)

Generación reproducible uniforme: colores 1..K y valores 1..9, RNG local con
semilla. Se combinan N={2,3,4} y K={2,3,5}, con M=3*N²; tres semillas por
configuración. Los dos agentes reciben exactamente cada mismo archivo generado
y la misma semilla. El límite previsto es 10 segundos por agente.

El script conserva los movimientos y los valida de forma independiente. Reporta
colocadas, ocupadas, mayor, tiempo de resolución y esfuerzo; guarda media y
desviación muestral entre semillas, cantidad de victorias y fallos por configuración.
El tiempo es el del algoritmo, excluyendo arranque del intérprete y validación.
La gráfica SVG muestra media y desviación de tiempo. Fallos y excesos de tiempo
se excluyen de los promedios y se reportan explícitamente. Para tiempos diminutos,
la salida de cuatro decimales del CLI limita la precisión de la medición.

M crece junto con N, por lo que el efecto del tamaño del tablero y el de la longitud
de secuencia no se pueden separar en esta batería: la interpretación debe declararlo. Para aislar
el efecto de N, complementar con un diseño de M fijo antes de afirmar que el cambio se debe solo a N.
La dispersión combina cambios de instancia y de aleatoriedad del agente; si se
necesita separar ambos, variar sus semillas por separado en un estudio adicional.

## Verificación de infraestructura

Se ejecutaron 27 partidas del agente trivial con este diseño y límite de 1 segundo.
Todas produjeron soluciones legales. Los archivos en
`experiments/prueba_infraestructura/` son evidencia de funcionamiento del generador,
orquestación, validación y exportación, no resultados de búsqueda ni evolutivo.

## Resultados e interpretación final (pendiente)

Una vez integrados B y C, ejecutar la batería, incorporar `resumen.csv` y
`tiempos.svg`, y comparar colocadas antes que ocupadas y tiempo. Describir qué
configuraciones agotan el límite, cuál parámetro está asociado al mayor costo,
cómo se comporta el evolutivo en ese régimen y las limitaciones del diseño.
No hay todavía evidencia para concluir cuál agente domina.

## Pruebas de ejecución

Se aprobaron 63 pruebas tanto localmente como en Docker. En Docker también se
ejecutó el ejemplo con el trivial y se validó su solución: victoria, 6 colocadas,
4 ocupadas y mayor 5. El contenedor instala sus dependencias durante la construcción.
