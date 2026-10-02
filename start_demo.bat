@echo off
echo Starting Backend2JB (Port 8000)...
start "Backend2JB" cmd /c "cd C:\s7\main project\backend2jb && uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"

echo Starting Feature/Face-Age API (Port 8001)...
start "Face-Age Backend" cmd /c "cd C:\s7\main project\face-age && python face_age_api.py"

echo Starting Frontend Demo (Port 8501)...
start "Frontend Demo" cmd /c "cd C:\s7\main project && streamlit run website\instagram_demo.py"

echo.
echo All services launched!
echo - Frontend: http://localhost:8501
echo - Backend A (Moderation): http://localhost:8000
echo - Backend B (Face/Age): http://localhost:8001