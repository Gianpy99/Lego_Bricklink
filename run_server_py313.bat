@echo off
:: =============================================================================
:: LEGO Analysis Web Server Launcher (Python 3.13)
:: Utilizza Python 3.13 in ambiente virtuale pulito
:: =============================================================================

title LEGO Analysis Server (Python 3.13)

echo.
echo ========================================
echo 🧱 LEGO Analysis Web Server (Python 3.13)
echo ========================================
echo.

:: Controlla se l'ambiente virtuale esiste
if not exist "lego_env\Scripts\python.exe" (
    echo ❌ Ambiente virtuale non trovato!
    echo 🔧 Creazione ambiente virtuale Python 3.13...
    py -3.13 -m venv lego_env
    if errorlevel 1 (
        echo ❌ Errore nella creazione dell'ambiente virtuale
        echo 💡 Verifica che Python 3.13 sia installato: py -3.13 --version
        pause
        exit /b 1
    )
    echo ✅ Ambiente virtuale creato
)

:: Attiva l'ambiente virtuale
echo 🔄 Attivazione ambiente Python 3.13...
call lego_env\Scripts\activate.bat

:: Verifica versione Python
echo 🐍 Versione Python:
python --version

:: Controlla dipendenze e installa se necessario
echo 📦 Controllo dipendenze...
python -c "import flask, matplotlib, requests, openpyxl, schedule, pandas; print('✅ Tutte le dipendenze presenti')" 2>nul
if errorlevel 1 (
    echo 🔧 Installazione dipendenze mancanti...
    pip install flask matplotlib requests openpyxl schedule requests-oauthlib pandas
    if errorlevel 1 (
        echo ❌ Errore nell'installazione delle dipendenze
        pause
        exit /b 1
    )
)

:: Configura modalità produzione (evita riavvii automatici)
set FLASK_ENV=production
set FLASK_DEBUG=false
set WERKZEUG_RUN_MAIN=false

:: Disabilita completamente il file watcher di Werkzeug
set PYTHONDONTWRITEBYTECODE=1

:: Avvia il server
echo.
echo 🚀 Avvio server LEGO Analysis...
echo 🌐 Server disponibile su: http://localhost:5000
echo 📊 Dashboard: http://localhost:5000/dashboard
echo 📧 Email Config: http://localhost:5000/email-config
echo.
echo ⚠️  Per fermare il server: Ctrl+C
echo.

python web_app.py

:: Se il server si chiude, mostra messaggio
echo.
echo 🛑 Server fermato.
pause
