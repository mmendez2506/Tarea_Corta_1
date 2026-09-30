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

## Formulación del agente de búsqueda (B, pendiente)

Documentar: algoritmo, estado completo incluyendo índice de ficha, sucesores,
costo, prueba de meta, tratamiento de repetidos y poda; si hay heurística,
admisibilidad o garantía a la que se renuncia. Especificar control temporal y
qué solución se devuelve al agotar el presupuesto.

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
