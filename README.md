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

## Integración de B y C

Actualmente solo `trivial` está implementado. Es una referencia para pruebas;
no sustituye ninguno de los dos agentes obligatorios. B y C deben implementar
`Agente.resolver(instancia, semilla, limite_s)` y retornar `Resultado` con
colocaciones y esfuerzo. Registren sus clases en `tileup.main.AGENTES`, con las
claves `search` y `evolutionary`; usen `random.Random(semilla)` y controlen el
tiempo dentro del algoritmo. El punto de entrada no interrumpe agentes: el plazo
debe respetarlo cada implementación. Deben documentar su formulación en el informe
y añadir integración y pruebas de determinismo y de límite temporal.

## Batería experimental de A

```powershell
python -m experiments.run_all --agentes search evolutionary --limite 10
```

También: `make experiments` o `run.ps1 -Accion experiments`. Si los agentes no
están registrados, el comando falla claramente sin inventar resultados.
Valores predeterminados: N=2,3,4; K=2,3,5; M=3*N*N; semillas=1,2,3.
Son nueve configuraciones, tres semillas y dos agentes: 54 ejecuciones.
Cada pareja utiliza las mismas instancias y semillas. Se guardan instancias,
soluciones, resultados individuales, media y desviación muestral de métricas,
y gráfica de tiempo con barras de dispersión en `experiments/resultados/`.
Los errores y excesos de tiempo quedan registrados y hacen retornar código 1;
no se incorporan silenciosamente al promedio.

Prueba de infraestructura: `python -m experiments.run_all --agentes trivial
--limite 1 --salida experiments/prueba_infraestructura` (una sola línea).
Estos resultados no constituyen la comparación final. Ver `INFORME.md`.

## Documentación y entrega

Consultar `ESTADO_A.md`, `INFORME.md` y `DECLARACION_IA.md`. El informe definitivo
requiere agentes, parámetros y resultados reales de B y C. Conservar las instancias
y soluciones experimentales para arbitraje. No subir `.venv` ni cachés. Cada
integrante debe aportar sus propios commits y poder explicar su código.

## Comprobaciones realizadas

Se verificaron las 63 pruebas localmente y dentro de Docker. También se construyó
la imagen y se ejecutaron run.ps1 -Accion run y -Accion validate: el ejemplo dio
victoria y el árbitro confirmó 6 colocadas, 4 ocupadas y mayor 5.
Makefile queda pendiente de probar con Make.
