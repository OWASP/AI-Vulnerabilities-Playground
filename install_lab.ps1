param(
  [string]$ApiDir = "apps\api",
  [string]$WebDir = "apps\web",
  [string]$Port   = "8000"
)

function Ensure-Venv-And-Reqs {
  param([string]$apiPath)

  $venvPy = Join-Path $apiPath ".venv\Scripts\python.exe"

  if (!(Test-Path $venvPy)) {
    Write-Host "Creating venv..." -ForegroundColor Cyan
    if (Get-Command py -ErrorAction SilentlyContinue) {
      & py -3 -m venv (Join-Path $apiPath ".venv")
    } else {
      & python -m venv (Join-Path $apiPath ".venv")
    }
  }

  Write-Host "Installing backend requirements..." -ForegroundColor Cyan
  & $venvPy -m pip install --upgrade pip
  & $venvPy -m pip install -r (Join-Path $apiPath "requirements.txt")
}

function Ensure-Web-Env {
  param([string]$webPath)

  $envFile = Join-Path $webPath ".env"
  $envExample = Join-Path $webPath ".env.example"
  if (!(Test-Path $envFile)) {
    if (Test-Path $envExample) {
      Copy-Item $envExample $envFile
    } else {
      # minimal default
      "VITE_API_BASE=http://localhost:8000/api" | Out-File -Encoding utf8 $envFile
    }
  }
}

# --- Paths (handle spaces safely) ---
$root    = Split-Path -Parent $MyInvocation.MyCommand.Path
$apiPath = Join-Path $root $ApiDir
$webPath = Join-Path $root $WebDir

# --- Backend: venv + requirements ---
Ensure-Venv-And-Reqs -apiPath $apiPath

# --- Frontend: .env + deps ---
Ensure-Web-Env -webPath $webPath

Write-Host "Starting backend (Uvicorn) in a new window..." -ForegroundColor Green
$uvicornCmd = "Set-Location -LiteralPath '$apiPath'; & '.\.venv\Scripts\python.exe' -m uvicorn main:app --reload --port $Port"
Start-Process powershell -ArgumentList "-NoExit","-Command",$uvicornCmd | Out-Null

Write-Host "Starting frontend (Vite) in a new window..." -ForegroundColor Green
$viteCmd = "Set-Location -LiteralPath '$webPath'; if (!(Test-Path node_modules)) { npm install }; npm run dev"
Start-Process powershell -ArgumentList "-NoExit","-Command",$viteCmd | Out-Null

Write-Host "`nDev environment launched:"
Write-Host "  Backend → http://localhost:$Port"
Write-Host "  Frontend → http://localhost:5173" -ForegroundColor Cyan
