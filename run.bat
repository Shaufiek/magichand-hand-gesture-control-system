@echo off
echo =========================================
echo  MagicHand
echo =========================================
echo.
echo Zorg ervoor dat VLC-mediaspeler geopend en klaar voor gebruik is!
echo.
echo Virtuele omgeving aan het activeren...
echo.

REM Activate the virtual environment
call venv\Scripts\activate.bat

echo Web-applicatie aan het openen...
echo.
streamlit run app.py

echo.
echo =========================================
echo  Web-applicatie gesloten . Bedankt voor het gebruik maken van MagicHand!
echo =========================================
pause