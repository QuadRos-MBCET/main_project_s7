@echo off
title SafeAd AI - Unified Platform Launcher
echo =====================================================================
echo    Starting SafeAd AI Unified Platform Services...
echo =====================================================================
cd /d "%~dp0"
set PYTHONPATH=%CD%;%CD%\joseph_safead_core;%CD%\sooraj_face_age_core\face-age

echo [1/3] Starting SafeAd Backend API on Port 8002...
start "SafeAd Backend (Port 8002)" cmd /k "python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8002"

timeout /t 3 /nobreak >nul

echo [2/3] Starting Face-Age API on Port 8001...
start "Face-Age API (Port 8001)" cmd /k "python sooraj_face_age_core\face-age\face_age_api.py"

timeout /t 3 /nobreak >nul

echo [3/3] Starting Streamlit Web App on Port 8501...
start "Streamlit Frontend (Port 8501)" cmd /k "streamlit run frontend/app.py --server.port 8501"

echo.
echo =====================================================================
echo    All 3 services launched successfully!
echo    - Streamlit Frontend : http://localhost:8501
echo    - Backend API Health : http://127.0.0.1:8002/health
echo    - Face-Age API Docs  : http://127.0.0.1:8001/openapi.json
echo =====================================================================
pause
