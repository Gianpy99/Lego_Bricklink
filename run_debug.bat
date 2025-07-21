@echo off
echo.
echo ================================================================
echo 🧱 LEGO Collection Analysis System - Debug Mode
echo ================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python non trovato! Installa Python 3.8+ da python.org
    pause
    exit /b 1
)

echo ✅ Python trovato
echo.

REM Install/upgrade dependencies
echo 📦 Installazione dipendenze...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Errore installazione dipendenze
    pause
    exit /b 1
)

echo ✅ Dipendenze installate
echo.

REM Create necessary directories
if not exist "uploads" mkdir uploads
if not exist "reports" mkdir reports
if not exist "templates" mkdir templates
echo ✅ Directory create

echo.
echo ================================================================
echo 🛠️ LEGO ANALYSIS SYSTEM - MODALITÀ DEBUG
echo ================================================================
echo ⚠️  ATTENZIONE: Modalità debug abilitata
echo    • Auto-reload dei file Python attivo
echo    • Directory uploads esclusa dal monitoring
echo    • Logging dettagliato abilitato
echo.
echo ================================================================

echo.
echo 🚀 Avvio server in modalità DEBUG...
echo 🌐 Il sistema sarà disponibile su: http://localhost:5000
echo 📊 Dashboard: http://localhost:5000/dashboard
echo 📋 Upload: http://localhost:5000/upload
echo.
echo 🛠️  MODALITÀ DEBUG: Server riavvia solo per modifiche al codice
echo ⏹️  Premi Ctrl+C per fermare il server
echo.

REM Start the web server in debug mode
python web_app.py --debug
