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
