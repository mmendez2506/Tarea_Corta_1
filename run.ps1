# ==============================
# Tarea Corta 1 — Inteligencia Artificial
# Integrantes: María Felix Mendez Abarca, Cristhian Rivas y Jozafath Perez
# Descripción: Entrada de un solo comando para construir y ejecutar con Docker en PowerShell.
# ==============================

param(
    [ValidateSet('run','test','validate','experiments','ensayo')][string]$Accion = 'run',
    [string]$Instancia = 'instances/ejemplo.txt',
    [string]$Agente = 'search',
    [int]$Semilla = 1,
    [double]$Limite = 10,
    [string]$Solucion = '',
    [int]$N = 20,
    [int]$K = 50,
    [int]$M = 1200
)
$ErrorActionPreference = 'Stop'
if (-not $Solucion) {
    $base = [IO.Path]::GetFileNameWithoutExtension($Instancia)
    $Solucion = "solutions/${base}_${Agente}_s$Semilla.txt"
}
$raizProyecto = $PSScriptRoot
docker build -t tileup $raizProyecto
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$comando = switch ($Accion) {
    'run' { @('python','-m','tileup.main','--instancia',$Instancia,'--agente',$Agente,'--semilla',"$Semilla",'--limite',"$Limite") }
    'test' { @('python','-m','pytest','-q') }
    'validate' { @('python','-m','validator.validate','--instancia',$Instancia,'--solucion',$Solucion) }
    'experiments' { @('python','-m','experiments.run_all') }
    'ensayo' { @('python','-m','experiments.ensayo','--n',"$N",'--k',"$K",'--m',"$M",'--limite',"$Limite") }
}
docker run --rm -v "${raizProyecto}:/app" tileup @comando
exit $LASTEXITCODE
