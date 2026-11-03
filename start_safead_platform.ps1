# SafeAd AI - Unified Platform Launcher (PowerShell)
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "   Starting SafeAd AI Unified Platform Services..." -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan

$root = $PSScriptRoot
if (-not $root) { $root = Get-Location }

$env:PYTHONPATH = "$root;$root\joseph_safead_core;$root\sooraj_face_age_core\face-age"
$env:HF_HUB_OFFLINE = "1"
$env:TRANSFORMERS_OFFLINE = "1"

Write-Host "`n[1/3] Starting SafeAd Backend API on Port 8002..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PYTHONPATH='$env:PYTHONPATH'; Set-Location '$root'; python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8002"

Start-Sleep -Seconds 3

Write-Host "[2/3] Starting Face-Age API on Port 8001..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PYTHONPATH='$env:PYTHONPATH'; `$env:HF_HUB_OFFLINE='1'; `$env:TRANSFORMERS_OFFLINE='1'; Set-Location '$root'; python sooraj_face_age_core\face-age\face_age_api.py"

Start-Sleep -Seconds 3

Write-Host "[3/3] Starting Streamlit Frontend on Port 8501..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PYTHONPATH='$env:PYTHONPATH'; `$env:HF_HUB_OFFLINE='1'; `$env:TRANSFORMERS_OFFLINE='1'; Set-Location '$root'; streamlit run frontend/app.py --server.port 8501"

Write-Host "`n=====================================================================" -ForegroundColor Cyan
Write-Host "   All 3 services launched successfully!" -ForegroundColor Cyan
Write-Host "   - Streamlit Frontend : http://localhost:8501" -ForegroundColor Yellow
Write-Host "   - Backend API Health : http://127.0.0.1:8002/health" -ForegroundColor Yellow
Write-Host "   - Face-Age API Docs  : http://127.0.0.1:8001/openapi.json" -ForegroundColor Yellow
Write-Host "=====================================================================" -ForegroundColor Cyan
