@echo off
REM Quick start script for LEGO Analysis System (Windows)

echo 🟡 LEGO Analysis System - Quick Start
echo =====================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python non trovato. Installa Python 3.6+ e riprova.
    pause
    exit /b 1
)

echo ✅ Python trovato
python --version

REM Check if lego_env virtual environment exists (preferred)
if exist "lego_env" (
    echo 🔧 Usando ambiente virtuale 'lego_env' esistente...
    call lego_env\Scripts\activate.bat
    goto :install_deps
)

REM Check if venv virtual environment exists (fallback)
if exist "venv" (
    echo 🔧 Usando ambiente virtuale 'venv' esistente...
    call venv\Scripts\activate.bat
    goto :install_deps
)

REM Create new virtual environment
echo 🔧 Creando nuovo ambiente virtuale 'lego_env'...
python -m venv lego_env
call lego_env\Scripts\activate.bat

:install_deps
REM Install/upgrade dependencies
echo 📦 Installando/aggiornando dipendenze...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Check if config exists
if not exist "config.json" (
    echo ⚙️ Creando file di configurazione di esempio...
    echo {> config.json
    echo     "reports": [>> config.json
    echo         {>> config.json
    echo             "name": "Collezione di Test",>> config.json
    echo             "folder_path": "./examples",>> config.json
    echo             "color_mapping_path": "BL_color_mapping.json",>> config.json
    echo             "output_pdf": "test_report.pdf">> config.json
    echo         }>> config.json
    echo     ],>> config.json
    echo     "combiners": [>> config.json
    echo         {>> config.json
    echo             "name": "Lista Desiderata Test",>> config.json
    echo             "folder_path": "./examples",>> config.json
    echo             "filtered_folder": "./output",>> config.json
    echo             "output_file": "wanted_list.xml",>> config.json
    echo             "excluded_files": []>> config.json
    echo         }>> config.json
    echo     ],>> config.json
    echo     "logging": {>> config.json
    echo         "level": "INFO",>> config.json
    echo         "file": "lego_analysis.log">> config.json
    echo     }>> config.json
    echo }>> config.json
)

REM Create directories
if not exist "examples" mkdir examples
if not exist "output" mkdir output

echo.
echo 🚀 Setup completato!
echo.
echo Opzioni disponibili:
echo 1. Avvia interfaccia web:     python web_app.py
echo 2. Analisi command line:     python LegoStatusBuildAnalysis.py
echo 3. Jupyter notebook:         jupyter notebook LegoStatusBuildAnalysis.ipynb
echo.
echo 📁 Posiziona i tuoi file XML/CSV/JSON nella cartella 'examples\'
echo 🌐 Interfaccia web: http://localhost:5000
echo.
set /p choice="Vuoi avviare l'interfaccia web ora? (y/n): "
if /i "%choice%"=="y" (
    echo 🌐 Avviando interfaccia web...
    python web_app.py
)

pause
