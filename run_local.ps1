param(
    [string]$ApiBaseUrl = "http://localhost",
    [string]$KeyFile = ".key.json"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Error "Environnement virtuel introuvable: .\.venv\Scripts\Activate.ps1"
}

if (-not (Test-Path -Path $KeyFile)) {
    Write-Error "Fichier de cle introuvable: $KeyFile"
}

. .\.venv\Scripts\Activate.ps1

$env:TIMBREUSE_API_BASE_URL = $ApiBaseUrl
$env:TIMBREUSE_API_KEY_FILE = $KeyFile

Write-Host "TIMBREUSE_API_BASE_URL=$($env:TIMBREUSE_API_BASE_URL)"
Write-Host "TIMBREUSE_API_KEY_FILE=$($env:TIMBREUSE_API_KEY_FILE)"
Write-Host "Lancement de Timbreuse..."

python .\main.py
