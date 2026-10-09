# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Cristhian Rivas y Jozafath Perez
# Descripción: Interfaz común para conectar los agentes de búsqueda y evolutivo.
# ==============================

from abc import ABC, abstractmethod
import time

from tileup.io.instance import Instancia

class Resultado:
    # Lo que entrega un agente: (fila, columna) por ficha y su medida de esfuerzo.
    __slots__ = ("colocaciones", "esfuerzo")

    def __init__(self, colocaciones: list[tuple[int, int]] | None = None, esfuerzo: int = 0):
        self.colocaciones = [] if colocaciones is None else colocaciones
        self.esfuerzo = esfuerzo

# Instante en que empezó la ejecución del programa. main.py lo fija antes de
# llamar al agente, para que el plazo descuente el tiempo ya usado en leer la
# instancia. Si nadie lo fija (por ejemplo, en las pruebas), el plazo cuenta
# desde que el agente empieza.
_origen = None

def fijar_origen(instante: float | None) -> None:
    global _origen
    _origen = instante

def plazo(limite_s: float, margen: float, m: int) -> float:
    # Instante en que el agente debe detenerse por reloj. Además del margen, se
    # reserva el tiempo que main.py necesita después para verificar y escribir la
    # solución, que crece con la cantidad de fichas (se midieron unos 3 µs por
    # ficha; se reservan 6). Solo importa en tableros enormes.
    disponible = limite_s * margen
    inicio = time.perf_counter() if _origen is None else _origen
    return inicio + max(disponible - 6e-6 * m, disponible / 2)

class Agente(ABC):
    nombre: str = ""
    unidad_esfuerzo: str = "operaciones"

    @abstractmethod
    def resolver(self, instancia: Instancia, semilla: int, limite_s: float) -> Resultado:
        ...
