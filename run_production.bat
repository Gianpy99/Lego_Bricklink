@echo off
echo.
echo ================================================================
echo 🧱 LEGO Collection Analysis System - Production Mode
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
pip install -r requirements.txt >nul 2>&1
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
echo 🎯 LEGO ANALYSIS SYSTEM - MODALITÀ PRODUZIONE
echo ================================================================
echo 📊 Dashboard Interattiva con Chart.js
echo    • Grafici interattivi per analisi colori e categorie
echo    • Filtri real-time e ricerca avanzata
echo    • Timeline progresso collezioni
echo    • Confronto multi-collezione
echo.
echo 🌐 Interfaccia Web Avanzata
echo    • Upload drag-and-drop per file multipli
echo    • Supporto XML, CSV, JSON
echo    • Generazione report PDF automatica
echo    • Esportazione dati Excel/CSV
echo.
echo 🔗 Integrazione BrickLink API
echo    • Download automatico inventari
echo    • Upload wanted list sincronizzate
echo    • Autenticazione OAuth 1.0a
echo    • Monitoraggio prezzi real-time
echo.
echo 📧 Sistema Notifiche Email
echo    • Alert automatici pezzi mancanti
echo    • Notifiche variazioni prezzi
echo    • Riepilogo settimanale collezioni
echo    • Template HTML personalizzabili
echo.
echo 🗄️ Database Analytics SQLite
echo    • Storico complete analisi
echo    • Statistiche avanzate collezioni
echo    • Tracking progressi nel tempo
echo    • Backup automatico dati
echo.
echo ================================================================

echo.
echo 🚀 Avvio server in modalità PRODUZIONE...
echo 🌐 Il sistema sarà disponibile su: http://localhost:5000
echo 📊 Dashboard: http://localhost:5000/dashboard
echo 📋 Upload: http://localhost:5000/upload
echo.
echo ⚠️  MODALITÀ PRODUZIONE: Server stabile, nessun riavvio automatico
echo ⏹️  Premi Ctrl+C per fermare il server
echo.

REM Start the web server in production mode (no debug)
python web_app.py
