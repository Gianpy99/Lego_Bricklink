# 🛠️ Guida Risoluzione Problemi Installazione

## Problema: Errore "InvalidVersion: '4.0.0-unsupported'"

### Causa
Questo errore si verifica quando ci sono conflitti tra pacchetti installati tramite Anaconda e pip, o quando ci sono versioni corrotte nel sistema.

### Soluzioni (in ordine di preferenza)

### ✅ Soluzione 1: Usa il nostro installer robusto
```cmd
install_deps.bat
```
Questo script installa le dipendenze una per una evitando conflitti.

### ✅ Soluzione 2: Modalità Minimal
Se continui ad avere problemi, usa i requisiti minimi:
```cmd
pip install -r requirements_minimal.txt
```

### ✅ Soluzione 3: Ambiente Virtuale Pulito
```cmd
# Crea ambiente virtuale pulito
python -m venv lego_env
lego_env\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### ✅ Soluzione 4: Fix Anaconda
Se usi Anaconda:
```cmd
# Aggiorna conda
conda update conda
conda update anaconda

# Usa conda invece di pip per i pacchetti principali
conda install flask matplotlib pandas requests
pip install schedule requests-oauthlib openpyxl
```

### ✅ Soluzione 5: Pulizia Manuale
```cmd
# Disinstalla pacchetti problematici
pip uninstall pyodbc -y
pip uninstall pillow -y

# Reinstalla solo quello che serve
pip install -r requirements_minimal.txt
```

## Problemi Specifici e Soluzioni

### 🔧 "WARNING: Ignoring invalid distribution -illow"
```cmd
# Trova e rimuovi installazioni corrotte di Pillow
pip uninstall Pillow PIL -y
pip install Pillow --force-reinstall
```

### 🔧 "ERROR: Exception in pip"
```cmd
# Aggiorna pip
python -m pip install --upgrade pip
python -m pip install --upgrade setuptools wheel
```

### 🔧 "Permission denied"
```cmd
# Esegui come amministratore oppure:
pip install --user -r requirements.txt
```

### 🔧 "No module named 'flask'"
```cmd
# Installazione diretta Flask
pip install Flask==2.2.5
```

## Test Installazione

Dopo ogni tentativo, testa con:
```cmd
python -c "import flask, matplotlib; print('✅ Dipendenze base OK')"
```

## Modalità Emergenza

Se nulla funziona, il sistema può girare in modalità base con solo:
- Flask (per web interface)
- matplotlib (per grafici)

```cmd
pip install Flask matplotlib
python web_app.py
```

Il sistema rileverà automaticamente le dipendenze mancanti e adatterà le funzionalità.

## Supporto Anaconda

### Verifica ambiente Anaconda:
```cmd
conda info
conda list pip
```

### Se usi Anaconda, preferisci conda:
```cmd
conda install flask matplotlib pandas requests
conda install -c conda-forge openpyxl
pip install schedule requests-oauthlib
```

## File di Log

In caso di errori, controlla:
- `pip.log` nella directory di lavoro
- Output del terminale completo
- `lego_analysis.log` se il sistema parte

## Compatibilità Sistema

### Sistemi Testati:
- ✅ Windows 10/11 + Python 3.8-3.11
- ✅ Windows + Anaconda 3
- ✅ Python Standard (non Anaconda)

### Versioni Python Supportate:
- ✅ Python 3.8+
- ⚠️  Python 3.12+ (potrebbero servire adattamenti)

## Se Tutto Fallisce

1. **Usa requirements_minimal.txt** - funzionalità base garantite
2. **Installa manualmente** solo Flask e matplotlib
3. **Contatta supporto** con output completo errore
4. **Usa Docker** (se disponibile) per ambiente isolato

---

**La maggior parte dei problemi si risolve con `install_deps.bat` o ambiente virtuale pulito!** 🎯
