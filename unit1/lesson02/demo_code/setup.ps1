$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$versionCheck = @"
import sys

if sys.version_info < (3, 10):
    print("Python 3.10+ is required. Current version:", sys.version.split()[0])
    raise SystemExit(1)
print("Using Python", sys.version.split()[0])
"@

$pythonCommand = $null
$pythonArgs = @()
$candidates = @(
    @{ Command = "py"; Args = @("-3.12") },
    @{ Command = "py"; Args = @("-3.11") },
    @{ Command = "py"; Args = @("-3.10") },
    @{ Command = "py"; Args = @("-3.13") },
    @{ Command = "python"; Args = @() }
)

foreach ($candidate in $candidates) {
    $cmd = Get-Command $candidate.Command -ErrorAction SilentlyContinue
    if (-not $cmd) {
        continue
    }

    $versionCheck | & $cmd.Source @($candidate.Args) - *> $null
    if ($LASTEXITCODE -eq 0) {
        $pythonCommand = $cmd.Source
        $pythonArgs = $candidate.Args
        break
    }
}

if (-not $pythonCommand) {
    Write-Host "Could not find Python 3.10+. Please install Python 3.10+ first."
    exit 1
}

$versionCheck | & $pythonCommand @pythonArgs -

& $pythonCommand @pythonArgs -m venv .venv

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt

Write-Host ""
Write-Host "Setup complete."
Write-Host ""
Write-Host "Next steps:"
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  python 01_hello_agent.py"
Write-Host ""
Write-Host "Model setup:"
Write-Host "  OpenAI: setx OPENAI_API_KEY ""sk-..."""
Write-Host "  Ollama: install Ollama, then run: ollama pull qwen2.5:7b"
Write-Host "  Other OpenAI-compatible model: set OPENAI_BASE_URL, OPENAI_API_KEY, OPENAI_MODEL, OPENAI_API_MODE=chat_completions"
