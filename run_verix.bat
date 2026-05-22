@echo off
echo Starting Verix AI Platform...

cd backend
start cmd /k "uvicorn app.main:app --reload --port 8000"

cd ../frontend
start cmd /k "python -m http.server 3000"

echo Verix AI is starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to stop all servers...
pause > nul
taskkill /f /im python.exe
taskkill /f /im cmd.exe
