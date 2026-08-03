@echo off
echo =========================================
echo  Gesture Media Control System
echo =========================================
echo.
echo Make sure VLC is open and ready!
echo.
echo Activating virtual environment...
echo.

REM Activate the virtual environment
call venv\Scripts\activate.bat

echo Starting web app...
echo.
streamlit run app.py

echo.
echo =========================================
echo  App closed. Thank you for using!
echo =========================================
pause