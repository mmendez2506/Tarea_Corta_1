# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Christian Rivas y Jozafath Perez
# Descripción: Entrada de un solo comando para construir y ejecutar con Docker en PowerShell.
# ==============================

param(
    [ValidateSet('run','test','validate','experiments')][string]$Accion = 'run',
    [string]$Instancia = 'instances/ejemplo.txt',
    [string]$Agente = 'trivial',
    [int]$Semilla = 1,
    [double]$Limite = 10,
    [string]$Solucion = 'solutions/ejemplo_trivial_s1.txt'
)
$ErrorActionPreference = 'Stop'
$raizProyecto = $PSScriptRoot
docker build -t tileup $raizProyecto
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$comando = switch ($Accion) {
    'run' { @('python','-m','tileup.main','--instancia',$Instancia,'--agente',$Agente,'--semilla',"$Semilla",'--limite',"$Limite") }
    'test' { @('python','-m','pytest','-q') }
    'validate' { @('python','-m','validator.validate','--instancia',$Instancia,'--solucion',$Solucion) }
    'experiments' { @('python','-m','experiments.run_all') }
}
docker run --rm -v "${raizProyecto}:/app" tileup @comando
exit $LASTEXITCODE
