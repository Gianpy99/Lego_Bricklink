#!/bin/bash
# Quick start script for LEGO Analysis System

echo "🟡 LEGO Analysis System - Quick Start"
echo "====================================="

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python non trovato. Installa Python 3.6+ e riprova."
    exit 1
fi

echo "✅ Python trovato: $(python --version)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🔧 Creando ambiente virtuale..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Attivando ambiente virtuale..."
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
echo "📦 Installando dipendenze..."
pip install -r requirements.txt

# Check if config exists
if [ ! -f "config.json" ]; then
    echo "⚙️ Creando file di configurazione di esempio..."
    cat > config.json << EOF
{
    "reports": [
        {
            "name": "Collezione di Test",
            "folder_path": "./examples",
            "color_mapping_path": "BL_color_mapping.json",
            "output_pdf": "test_report.pdf"
        }
    ],
    "combiners": [
        {
            "name": "Lista Desiderata Test",
            "folder_path": "./examples",
            "filtered_folder": "./output",
            "output_file": "wanted_list.xml",
            "excluded_files": []
        }
    ],
    "logging": {
        "level": "INFO",
        "file": "lego_analysis.log"
    }
}
EOF
fi

# Create example directory
mkdir -p examples output

echo ""
echo "🚀 Setup completato!"
echo ""
echo "Opzioni disponibili:"
echo "1. Avvia interfaccia web:     python web_app.py"
echo "2. Analisi command line:     python LegoStatusBuildAnalysis.py"
echo "3. Jupyter notebook:         jupyter notebook LegoStatusBuildAnalysis.ipynb"
echo ""
echo "📁 Posiziona i tuoi file XML/CSV/JSON nella cartella 'examples/'"
echo "🌐 Interfaccia web: http://localhost:5000"
echo ""
read -p "Vuoi avviare l'interfaccia web ora? (y/n): " choice
if [[ $choice == "y" || $choice == "Y" ]]; then
    echo "🌐 Avviando interfaccia web..."
    python web_app.py
fi
