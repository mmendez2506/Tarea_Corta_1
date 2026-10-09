# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Christian Rivas y Jozafath Perez
# Descripción: Lectura y verificación del formato de las instancias de TileUp.
# ==============================

from collections import namedtuple

class InstanciaInvalida(ValueError):
    pass

class Instancia(namedtuple("Instancia", "n k fichas")):
    # Inmutable como una tupla: N, K y la secuencia de fichas (color, valor) en orden.
    # Se usa namedtuple en lugar de dataclass porque importar dataclasses cuesta
    # unos 45 ms en cada ejecución del programa.
    __slots__ = ()

    @property
    def m(self) -> int:
        return len(self.fichas)

def _lineas_utiles(texto: str):

    for numero, linea in enumerate(texto.splitlines(), start=1):
        contenido = linea.split("#", 1)[0].strip()
        if contenido:
            yield numero, contenido.split()

def _enteros(tokens, esperados: int, numero: int, que: str) -> list[int]:
    if len(tokens) != esperados:
        raise InstanciaInvalida(
            f"línea {numero}: se esperaban {esperados} valores ({que}), "
            f"se encontraron {len(tokens)}"
        )
    try:
        return [int(t) for t in tokens]
    except ValueError:
        raise InstanciaInvalida(
            f"línea {numero}: se esperaban enteros ({que}), se encontró '{' '.join(tokens)}'"
        ) from None

def parsear_instancia(texto: str) -> Instancia:
    lineas = list(_lineas_utiles(texto))
    if len(lineas) < 2:
        raise InstanciaInvalida("faltan las líneas de N K y de M")

    numero, tokens = lineas[0]
    n, k = _enteros(tokens, 2, numero, "N K")
    if n < 1:
        raise InstanciaInvalida(f"línea {numero}: N debe ser al menos 1, es {n}")
    if k < 1:
        raise InstanciaInvalida(f"línea {numero}: K debe ser al menos 1, es {k}")

    numero, tokens = lineas[1]
    (m,) = _enteros(tokens, 1, numero, "M")
    if m < 0:
        raise InstanciaInvalida(f"línea {numero}: M no puede ser negativo, es {m}")

    filas_fichas = lineas[2:]
    if len(filas_fichas) != m:
        raise InstanciaInvalida(
            f"se declararon {m} fichas pero el archivo tiene {len(filas_fichas)}"
        )

    fichas = []
    for numero, tokens in filas_fichas:
        color, valor = _enteros(tokens, 2, numero, "color valor")
        if not 1 <= color <= k:
            raise InstanciaInvalida(
                f"línea {numero}: el color {color} está fuera del rango 1..{k}"
            )
        if valor < 1:
            raise InstanciaInvalida(
                f"línea {numero}: el valor debe ser un entero positivo, es {valor}"
            )
        fichas.append((color, valor))

    return Instancia(n=n, k=k, fichas=tuple(fichas))

def leer_instancia(ruta: str) -> Instancia:
    try:
        with open(ruta, encoding="utf-8") as archivo:
            texto = archivo.read()
    except FileNotFoundError:
        raise InstanciaInvalida(f"no existe el archivo '{ruta}'") from None
    except (OSError, UnicodeDecodeError) as error:
        raise InstanciaInvalida(f"no se pudo leer '{ruta}': {error}") from None
    return parsear_instancia(texto)
