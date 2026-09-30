# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Christian Rivas y Jozafath Perez
# Descripción: Interfaz común para conectar los agentes de búsqueda y evolutivo.
# ==============================

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from tileup.io.instance import Instancia

@dataclass
class Resultado:
    colocaciones: list[tuple[int, int]] = field(default_factory=list)
    esfuerzo: int = 0

class Agente(ABC):
    nombre: str = ""
    unidad_esfuerzo: str = "operaciones"

    @abstractmethod
    def resolver(self, instancia: Instancia, semilla: int, limite_s: float) -> Resultado:
        ...
