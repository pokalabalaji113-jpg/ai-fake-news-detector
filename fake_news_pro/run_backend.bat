@echo off
echo.
echo ================================================
echo   AI Fake News Detector PRO - Backend
echo   FastAPI running on http://localhost:8000
echo   API Docs at http://localhost:8000/docs
echo ================================================
echo.
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
pause
