# Tarea Corta 1 — Inteligencia Artificial

**Integrantes:** María Felix Mendez Abarca, Christian Rivas y Jozafath Perez

**Descripción:** Estado actual y comprobaciones de la parte A.

## Implementado

Motor, parser, CLI, escritura de soluciones, validador independiente, generador,
pruebas y batería experimental con CSV, dispersión y gráfica. Dockerfile, Makefile
y run.ps1 preparados. README e informe explican los contratos y la metodología.

## Comprobado

- 63 pruebas aprobadas en el entorno local del integrante.
- Construcción de la imagen y 63 pruebas aprobadas dentro de Docker.
- Ejemplo ejecutado y validado en Docker: victoria, 6 colocadas, 4 ocupadas, mayor 5.
- 27 partidas del trivial ejecutadas y validadas en la prueba de infraestructura.

La entrada de un comando en PowerShell está verificada. Makefile sigue pendiente
de ejecución en un entorno con Make.

## Pendiente para cerrar la entrega

B y C deben implementar y registrar sus agentes, documentar sus decisiones y
probar semilla y límite de tiempo. Después A corre la batería con ambos y completa
el análisis de escalabilidad. La comparación, video y revisión de autoría se cierran
entre todos. El resultado del trivial no reemplaza los agentes obligatorios.

El código está en tileup, validator, generator y experiments. La documentación
de la entrega está en README.md, INFORME.md y DECLARACION_IA.md.
