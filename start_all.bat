@echo off
echo ===============================================
echo SHL Assessment Recommendation System
echo Starting API Server and Web UI...
echo ===============================================

REM Start API in background
echo Starting API server on port 8000...
start "SHL API" cmd /k "cd src && python api.py"

REM Wait a bit for API to start
timeout /t 5 /nobreak

REM Start Streamlit UI
echo Starting Streamlit UI on port 8501...
start "SHL UI" cmd /k "streamlit run src/app.py"

echo.
echo ===============================================
echo Services started!
echo API: http://localhost:8000
echo UI:  http://localhost:8501
echo API Docs: http://localhost:8000/docs
echo ===============================================
echo.
echo Press any key to open browser...
pause

start http://localhost:8501
