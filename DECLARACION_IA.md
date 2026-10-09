# Tarea Corta 1 — Inteligencia Artificial

**Integrantes:** María Felix Mendez Abarca, Christian Rivas y Jozafath Perez

**Descripción:** Declaración de la asistencia de inteligencia artificial utilizada.

# Declaración de uso de IA

Según el historial de trabajo aportado por el integrante, se utilizó Claude para
generar el bloque inicial: motor, parser de instancias, CLI y pruebas. También
se utilizó para la revisión posterior de la parte A y su documentación.

En la parte A se utilizó Codex como asistencia para revisar el enunciado y el
repositorio, detectar un error de coordenadas, modificar el motor y el agente de
referencia, implementar el validador independiente, generador, batería experimental,
pruebas, contenedor y documentación. La asistencia incluyó generación de código.

No se invoca un modelo de lenguaje durante la ejecución para decidir movimientos.
Motor, árbitro y generador usan la biblioteca estándar; pytest se usa para pruebas.

## Comprobaciones realizadas

El integrante ejecutó las 63 pruebas localmente y con Docker, ejecutó el ejemplo
con el trivial y aplicó el validador: victoria, 6 colocadas, 4 ocupadas y mayor 5.
También ejecutó la batería de 27 partidas de referencia sin fallos. Estas
comprobaciones son ejecuciones del programa y pruebas automatizadas; no equivalen
a una revisión manual completa del código.

En la revisión asistida se contrastó el ejemplo del enunciado con el motor y el
árbitro y se verificó el rechazo de una colocación en una celda ocupada.

## Revisión humana por completar

Antes de entregar, el integrante debe recorrer a mano el ejemplo del enunciado,
revisar el código del motor y del validador y comprobar una solución ilegal.
Después debe registrar aquí qué revisó personalmente y los resultados obtenidos.
También falta completar el uso real de IA de B y C. No se declara como realizada
una revisión humana que no está confirmada.

## Mejoras de la segunda etapa (Christian Rivas)

Christian Rivas usó Claude Code (asistente de programación de Anthropic) para la
segunda etapa del proyecto. La asistencia incluyó:

- revisar el enunciado, la rúbrica y el código existente, y medir con un
  perfilador en qué se gasta el tiempo de cada agente;
- buscar técnicas conocidas aplicables (evaluación incremental, huellas de
  Zobrist, colas por cubetas, mutación con enfriamiento) y probarlas;
- generar el código de la regla de última aparición del evolutivo, las versiones
  incrementales de ambos agentes, el desempate por bloqueos de la búsqueda, la
  función `colocar_en` del motor, el nuevo presupuesto del evolutivo y el script
  `experiments/ensayo.py`;
- generar las pruebas nuevas (`tests/unit/test_incremental.py`,
  `tests/integration/test_ensayo.py`), correr los experimentos y redactar las
  secciones nuevas del informe y del README.
- en una tercera ronda, medir el reloj del proceso completo y generar las
  optimizaciones que no cambian decisiones: hijos sin construir y corte temprano
  en la búsqueda, parada inmediata al llegar al óptimo y simulación sobre una
  lista propia en el evolutivo, tabla de vecinos en el motor y arranque del
  programa sin `dataclasses` ni `argparse` en el camino habitual.
- en una cuarta ronda, recalibrar dentro de Docker el presupuesto del evolutivo
  (y comprobar que el de la búsqueda no tenía margen), agregar la opción `--ritmo`
  al script de ajuste y preparar la tabla de decisión del concurso
  (`experiments/preparacion_concurso/`).

No se invoca un modelo de lenguaje durante la ejecución para decidir movimientos.
Todo el código usa solo la biblioteca estándar de Python.

### Comprobaciones automáticas de esta etapa

- Las versiones incrementales deciden exactamente lo mismo que las directas:
  1080 genomas aleatorios en el evolutivo y 279 corridas de la búsqueda (con el
  desempate nuevo apagado) dieron soluciones idénticas a las del código anterior.
  Las pruebas de `test_incremental.py` repiten esa comparación en cada ejecución.
  Después de la tercera ronda, la búsqueda volvió a dar las mismas jugadas y nodos
  en 366 corridas y el evolutivo las mismas soluciones en 135.
- El ajuste de la búsqueda reproduce en otra máquina las cifras originales del
  informe (272 y 255 ocupadas), lo que confirma el determinismo.
- Todas las soluciones de las baterías pasaron por el validador independiente.

### Revisión humana de esta etapa (por completar)

Christian debe registrar aquí qué revisó personalmente: por ejemplo, recorrer a
mano la decodificación incremental con el ejemplo del enunciado, leer el código de
`colocar_en` y de `_candidatos`, y repetir una corrida del ensayo. No se declara
como hecha una revisión humana que no esté confirmada.
