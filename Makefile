# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Christian Rivas y Jozafath Perez
# Descripción: Comandos de construcción, ejecución, pruebas, validación y experimentos.
# ==============================

IMAGE ?= tileup
AGENTE ?= search
INSTANCIA ?= instances/ejemplo.txt
SEMILLA ?= 1
LIMITE ?= 10
N ?= 20
K ?= 50
M ?= 1200
SOLUCION ?= solutions/$(basename $(notdir $(INSTANCIA)))_$(AGENTE)_s$(SEMILLA).txt

.PHONY: build run test validate experiments ensayo
build:
	docker build -t $(IMAGE) .
run: build
	docker run --rm -v "$(CURDIR):/app" $(IMAGE) python -m tileup.main --instancia $(INSTANCIA) --agente $(AGENTE) --semilla $(SEMILLA) --limite $(LIMITE)
test: build
	docker run --rm $(IMAGE) python -m pytest -q
validate: build
	docker run --rm -v "$(CURDIR):/app" $(IMAGE) python -m validator.validate --instancia $(INSTANCIA) --solucion $(SOLUCION)
experiments: build
	docker run --rm -v "$(CURDIR):/app" $(IMAGE) python -m experiments.run_all
ensayo: build
	docker run --rm -v "$(CURDIR):/app" $(IMAGE) python -m experiments.ensayo --n $(N) --k $(K) --m $(M) --limite $(LIMITE)
