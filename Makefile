# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Christian Rivas y Jozafath Perez
# Descripción: Comandos de construcción, ejecución, pruebas, validación y experimentos.
# ==============================

IMAGE ?= tileup
AGENTE ?= trivial
INSTANCIA ?= instances/ejemplo.txt
SEMILLA ?= 1
LIMITE ?= 10

.PHONY: build run test validate experiments
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
