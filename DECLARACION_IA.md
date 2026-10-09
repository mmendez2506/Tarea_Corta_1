# Tarea Corta 1 — Inteligencia Artificial

**Integrantes:** María Felix Mendez Abarca, Cristhian Rivas y Jozafath Perez

**Descripción:** Declaración de la asistencia de inteligencia artificial utilizada.

# Declaración de uso de IA

Durante el desarrollo utilizamos herramientas de inteligencia artificial como apoyo
para consultas, revisión y propuestas de implementación. Cada integrante describe
abajo cómo las usó en su parte y qué revisó y probó por su cuenta.

La IA no se utiliza durante la ejecución del programa ni participa en las decisiones
de los agentes.

## María Felix Mendez Abarca

Utilicé herramientas de IA principalmente como apoyo para entender algunos puntos
del enunciado y para crear una propuesta inicial de organización de las carpetas y
archivos del proyecto.

También las utilicé para aclarar algunas dudas durante el desarrollo, revisar posibles
errores y apoyar la revisión de la documentación y de algunas partes del código.

Las sugerencias obtenidas fueron revisadas y adaptadas según las necesidades del
proyecto. Por mi parte realicé las pruebas correspondientes y comprobé el
funcionamiento del motor, el validador, el generador y la ejecución con Docker.

La IA no se utiliza durante la ejecución del programa ni participa en las decisiones
de los agentes.

## Jozafath Perez

[Lo completa Jozafath: herramientas que usó, en qué partes y qué revisó por su
cuenta.]

## Cristhian Rivas

Usé Claude Code (asistente de programación de Anthropic) en la segunda etapa del
proyecto. La asistencia incluyó:

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
  secciones nuevas del informe y del README;
- en una tercera ronda, medir el reloj del proceso completo y generar las
  optimizaciones que no cambian decisiones: hijos sin construir y corte temprano
  en la búsqueda, parada inmediata al llegar al óptimo y simulación sobre una
  lista propia en el evolutivo, tabla de vecinos en el motor y arranque del
  programa sin `dataclasses` ni `argparse` en el camino habitual;
- en una cuarta ronda, recalibrar dentro de Docker el presupuesto del evolutivo
  (y comprobar que el de la búsqueda no tenía margen), agregar la opción `--ritmo`
  al script de ajuste y preparar la tabla de decisión del concurso
  (`experiments/preparacion_concurso/`).

### Comprobaciones automáticas

- Las versiones incrementales deciden exactamente lo mismo que las directas:
  1080 genomas aleatorios en el evolutivo y 279 corridas de la búsqueda (con el
  desempate nuevo apagado) dieron soluciones idénticas a las del código anterior.
  Las pruebas de `test_incremental.py` repiten esa comparación en cada ejecución.
  Después de la tercera ronda, la búsqueda volvió a dar las mismas jugadas y nodos
  en 366 corridas y el evolutivo las mismas soluciones en 135.
- El ajuste de la búsqueda reproduce en otra máquina las cifras originales del
  informe (272 y 255 ocupadas), lo que confirma el determinismo.
- Todas las soluciones de las baterías pasaron por el validador independiente.

### Revisión personal

Revisé personalmente el código de la segunda etapa. Antes de hacerlo le pedí
varias veces a Claude Code que me explicara cómo funciona cada agente y en qué
consisten las mejoras, y con esas explicaciones leí el código.

También usé Claude Code para aprender a correr el proyecto con Docker: le pedí los
comandos de `run.ps1` y la diferencia entre pruebas, experimentos y ensayo del
concurso. Después ejecuté yo mismo esos comandos y revisé a mano las salidas.

No recorrí a mano la decodificación incremental paso a paso: su equivalencia con
el código anterior se respalda en las comprobaciones automáticas de arriba.
