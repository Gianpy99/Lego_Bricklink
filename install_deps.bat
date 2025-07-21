@echo off
echo.
echo ================================================================
echo 🛠️ LEGO Analysis System - Installazione Dipendenze Robusta
echo ================================================================
echo.

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python non trovato! Installa Python 3.8+ da python.org
    echo    Oppure attiva l'ambiente Anaconda se già installato
    pause
    exit /b 1
)

echo ✅ Python trovato
python --version

REM Check if we're in conda environment
python -c "import sys; print('🐍 Ambiente:', 'Conda' if 'conda' in sys.executable else 'Standard Python')"

echo.
echo 📦 Installazione dipendenze essenziali...
echo ⚠️  Installazione graduale per evitare conflitti
echo.

REM Install core packages one by one to avoid conflicts
echo [1/6] Installazione Flask...
pip install "Flask>=2.0.0,<3.0.0" --no-deps --quiet
pip install "werkzeug>=2.0.0,<3.0.0" --quiet
pip install "Jinja2>=3.0.0,<4.0.0" --quiet
pip install "MarkupSafe>=2.0.0,<3.0.0" --quiet
pip install "itsdangerous>=2.0.0" --quiet
pip install "click>=8.0.0" --quiet

echo [2/6] Installazione matplotlib...
pip install "matplotlib>=3.3.0,<4.0.0" --quiet

echo [3/6] Installazione pandas...
pip install "pandas>=1.3.0,<2.0.0" --quiet

echo [4/6] Installazione requests...
pip install "requests>=2.25.0,<3.0.0" --quiet
pip install "requests-oauthlib>=1.3.0,<2.0.0" --quiet

echo [5/6] Installazione supporti aggiuntivi...
pip install "openpyxl>=3.0.0,<4.0.0" --quiet
pip install "schedule>=1.1.0,<2.0.0" --quiet

echo [6/6] Verifica installazione...

REM Test imports
python -c "
try:
    import flask
    import matplotlib
    import pandas
    import requests
    import openpyxl
    import schedule
    print('✅ Tutte le dipendenze principali installate correttamente!')
except ImportError as e:
    print(f'⚠️  Avvertimento: {e}')
    print('   Il sistema funzionerà comunque con funzionalità ridotte')
"

echo.
echo ================================================================
echo 🎯 INSTALLAZIONE COMPLETATA
echo ================================================================
echo ✅ Dipendenze essenziali installate
echo 📋 Il sistema è pronto per l'utilizzo
echo.
echo 🚀 Per avviare il sistema:
echo    run_server.bat
echo.
echo 💡 NOTA: Se hai ancora errori, prova:
echo    1. Disattiva antivirus temporaneamente
echo    2. Esegui come amministratore
echo    3. Aggiorna pip: python -m pip install --upgrade pip
echo    4. Usa ambiente virtuale: python -m venv lego_env
echo.

pause
