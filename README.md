# LEGO BrickLink Wanted List Management

[![Python](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Un sistema completo per l'analisi e la gestione degli inventari LEGO tramite file XML di BrickLink, con generazione di report PDF dettagliati e strumenti per la gestione delle liste desiderate.

## 🎯 Panoramica del Progetto

Questo progetto fornisce strumenti per:
- **Analisi inventari LEGO**: Generazione di report PDF dettagliati con grafici e statistiche
- **Gestione file XML**: Combinazione e filtraggio di inventari per ottimizzare gli ordini
- **Mappatura colori**: Conversione tra codici colore BrickLink e Rebrickable
- **Monitoraggio progresso**: Tracking della completezza delle collezioni LEGO

## 📁 Struttura del Progetto

```
Lego_Bricklink/
├── LegoStatusBuildAnalysis.py          # Script principale per analisi e report
├── LegoStatusBuildAnalysis.ipynb       # Notebook Jupyter per analisi interattiva
├── config.json                        # File di configurazione (NUOVO!)
├── requirements.txt                   # Dipendenze Python (NUOVO!)
├── BL_color_mapping.json              # Mappatura completa codici colore BrickLink
├── BL_color_mapping_FULL.txt          # Mappatura colori in formato testo
├── color_mapping.json                 # Mappatura colori semplificata
├── bricklink_to_rebrickable_color_map.csv # Conversione colori BrickLink-Rebrickable
├── Analysis.xlsx                      # Analisi dati in formato Excel
├── lego_analysis.log                  # File di log (generato automaticamente)
└── README.md                          # Documentazione del progetto
```

### File Generati
Dopo l'esecuzione, troverai:
```
Output/
├── my_lego_report.pdf                 # Report PDF con grafici e statistiche
├── Filtered/
│   ├── filtered_set1.xml             # File XML filtrati per set
│   ├── filtered_set2.xml
│   └── wanted_list.xml               # Lista desiderata combinata
└── lego_analysis.log                 # Log dettagliati dell'esecuzione
```

## 🚀 Funzionalità Principali

### ✨ Nuove Funzionalità Implementate

#### 📊 Dashboard Interattiva con Chart.js
- **Grafici Real-time**: Visualizzazioni interattive per distribuzione colori, categorie e progressi
- **Filtri Avanzati**: Ricerca e filtraggio real-time dei dati
- **Confronto Collezioni**: Analisi comparativa tra multiple collezioni
- **Timeline Progressi**: Tracciamento del completamento nel tempo
- **Export Multi-formato**: Esportazione in PDF, Excel, CSV con un click

#### 🔗 Integrazione BrickLink API
- **Autenticazione OAuth 1.0a**: Connessione sicura all'account BrickLink
- **Download Automatico**: Scaricamento inventari e wanted list
- **Sincronizzazione Bidirezionale**: Upload/download dati automatico
- **Monitoraggio Prezzi**: Tracking prezzi real-time per ottimizzazione acquisti
- **Gestione Credenziali**: Sistema sicuro per memorizzazione token

#### 📧 Sistema Notifiche Email
- **Alert Automatici**: Notifiche per pezzi mancanti critici
- **Variazioni Prezzi**: Alert per cambiamenti significativi prezzi
- **Riepilogo Settimanale**: Summary automatico progressi collezioni
- **Template HTML**: Email personalizzabili con design professionale
- **Configurazione Flessibile**: Setup facile via interfaccia web

#### 🗄️ Database Analytics Avanzato
- **SQLite Integrato**: Storage persistente per analisi storiche
- **Statistiche Dettagliate**: Metriche avanzate per ogni collezione
- **Backup Automatico**: Protezione dati con snapshot periodici
- **Query Ottimizzate**: Performance elevate anche con grandi dataset

### 1. Analisi e Report PDF
- **Estrazione dati**: Analizza file XML degli inventari BrickLink
- **Grafici dettagliati**: Genera grafici a barre e a torta per ogni set
- **Statistiche complete**: Quantità minime, possedute e totali per colore
- **Report multi-pagina**: Salvataggio in un singolo file PDF strutturato
- **Rilevamento anomalie**: Evidenzia codici colore mancanti nella mappatura

### 2. Generazione Wanted List XML ✨ **NUOVO!**
- **Combinazione intelligente**: Unisce più inventari in un'unica wanted list
- **Filtraggio automatico**: Include solo elementi con quantità mancanti (MINQTY > 0)
- **Deduplicazione**: Combina elementi identici sommando le quantità richieste
- **Formato BrickLink**: XML pronto per importazione diretta su BrickLink
- **Interfaccia web**: Generazione con un click dall'interfaccia di analisi

### 3. Gestione XML Avanzata
- **Combinazione inventari**: Unisce più file XML in un unico inventario
- **Filtro intelligente**: Esclude elementi con quantità minima = 0
- **Deduplicazione**: Combina elementi identici sommando le quantità
- **File ottimizzati**: Genera XML pronti per l'importazione su BrickLink

### 4. Mappatura Colori
- **Database completo**: Oltre 200 colori BrickLink mappati
- **Conversione cross-platform**: Supporto per Rebrickable
- **Formato multiplo**: JSON, CSV e TXT per diverse esigenze

## 📊 Analisi Dati

Il sistema fornisce:
- **Grafici per set**: Distribuzione colori e stato completezza
- **Analisi globale**: Statistiche complete della collezione
- **Tracking progresso**: Percentuali di completamento per colore e set
- **Report warnings**: Identificazione di problemi nei dati

## 🛠️ Installazione

### Requisiti di Sistema
- Python 3.6 o superiore
- Librerie Python richieste (installate automaticamente)

### Setup Completo

1. **Clona il repository**:
   ```bash
   git clone https://github.com/Gianpy99/Lego_Bricklink.git
   cd Lego_Bricklink
   ```

2. **Installa le dipendenze**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepara i tuoi dati**:
   - Esporta gli inventari LEGO da BrickLink in formato XML
   - Posiziona i file XML in una cartella dedicata
   - Verifica che il file `BL_color_mapping.json` sia presente

4. **Configura il sistema**:
   - Modifica il file `config.json` con i tuoi percorsi
   - Oppure modifica direttamente le variabili nel codice Python

### Test Rapido
Per verificare che tutto funzioni:
```bash
python LegoStatusBuildAnalysis.py
```

Se vedi il messaggio "No configuration file found", crea o modifica il file `config.json`.

## 📖 Guida all'Uso

### 🚀 Metodo Raccomandato - Configurazione JSON

1. **Personalizza il file di configurazione** `config.json`:
   ```json
   {
     "reports": [
       {
         "name": "La mia collezione LEGO",
         "folder_path": "C:\\path\\to\\your\\xml\\files",
         "color_mapping_path": "BL_color_mapping.json",
         "output_pdf": "my_lego_report.pdf"
       }
     ],
     "combiners": [
       {
         "name": "Lista desiderata combinata",
         "folder_path": "C:\\path\\to\\your\\xml\\files",
         "filtered_folder": "C:\\path\\to\\output\\folder",
         "output_file": "wanted_list.xml",
         "excluded_files": ["set1.xml", "set2.xml"]
       }
     ]
   }
   ```

2. **Esegui lo script**:
   ```bash
   python LegoStatusBuildAnalysis.py
   ```

### 🔧 Metodo Alternativo - Modifica Diretta

Se preferisci non usare il file di configurazione, puoi modificare direttamente le variabili nel codice:

```python
# Nell'ultima parte del file LegoStatusBuildAnalysis.py
reports = [
    {
        "folder_path": r'C:\path\to\your\xml\files',
        "color_mapping_path": 'BL_color_mapping.json',
        "output_pdf": 'my_lego_report.pdf'
    }
]
```

### 📓 Uso Interattivo - Notebook Jupyter

Per analisi esplorative e personalizzazioni avanzate:
```bash
jupyter notebook LegoStatusBuildAnalysis.ipynb
```

### 🌐 Interfaccia Web ✨ **NUOVA!**

Per un'esperienza utente semplice e intuitiva:

1. **Avvia il server web**:
   ```bash
   python web_app.py
   ```

2. **Apri il browser** su `http://localhost:5000`

3. **Carica i tuoi file XML**:
   - Trascina i file nella zona di upload
   - Oppure clicca per selezionare manualmente
   - Supporta upload multipli simultanei

4. **Analizza e genera report**:
   - **Report PDF**: Analisi completa con grafici e statistiche
   - **Wanted List XML**: File pronto per importazione su BrickLink
   - **Visualizzazione real-time**: Statistiche aggiornate istantaneamente

#### Funzionalità Web Interface
- ✅ **Upload drag-and-drop** per file XML/CSV/JSON
- ✅ **Analisi multi-formato** con rilevamento automatico
- ✅ **Generazione report PDF** con un click
- ✅ **Creazione wanted list XML** per BrickLink
- ✅ **Statistiche real-time** (colori, elementi, completezza)
- ✅ **Download immediato** di report e wanted list

### ⚙️ Passaggi Dettagliati

#### 1. Preparazione dei File
- Esporta i tuoi inventari LEGO da BrickLink in formato XML
- Posiziona i file XML in una cartella (es. `C:\MyLego\Inventories\`)
- Assicurati che il file `BL_color_mapping.json` sia nella stessa cartella dello script

#### 2. Configurazione
- Modifica il file `config.json` con i tuoi percorsi
- Specifica quali file XML escludere (opzionale)
- Configura le cartelle di output

#### 3. Esecuzione
```bash
# Naviga nella cartella del progetto
cd C:\Development\Lego_Bricklink

# Esegui il script
python LegoStatusBuildAnalysis.py
```

#### 4. Verifica Output
- **Report PDF**: Generato nella cartella specificata
- **File XML filtrati**: Creati nella cartella `Filtered`
- **Log**: Controlla il file `lego_analysis.log` per eventuali errori

## 📈 Output e Report

### Report PDF Generato
- **Pagina per set**: Grafici dettagliati per ogni inventario
- **Riassunto globale**: Statistiche complete della collezione
- **Pagina warnings**: Problemi identificati durante l'analisi

### File XML Processati
- **Inventari filtrati**: Un file XML pulito per ogni inventario originale
- **Inventario combinato**: File XML unificato per ordini ottimizzati
- **Formato BrickLink**: Compatibile per importazione diretta

## 🎨 Mappatura Colori

Il sistema include mappature complete per:
- **BrickLink**: Oltre 200 colori con codici numerici
- **Rebrickable**: Conversione per compatibilità cross-platform
- **Formati multipli**: JSON, CSV e TXT per diverse applicazioni

### Esempio Mappatura
```json
{
  "1": "White",
  "5": "Red",
  "6": "Blue",
  "11": "Black"
}
```

## 🔧 Sviluppo e Contribuzioni

### Struttura del Codice
- **`LegoColorReport`**: Classe per generazione report PDF
- **`LegoXmlCombiner`**: Classe per gestione e combinazione XML
- **Notebook Jupyter**: Ambiente di sviluppo interattivo

### Come Contribuire
1. Fork del repository
2. Crea un feature branch
3. Commit delle modifiche
4. Push al branch
5. Crea una Pull Request

## 📋 Roadmap

- [x] **Supporto per più formati di input** ✅ *IMPLEMENTATO*
  - XML (BrickLink), CSV (Rebrickable/BrickOwl), JSON
  - Parser automatico con rilevamento formato
  - Mappatura colonne flessibile per CSV

- [x] **Interfaccia web per analisi** ✅ *IMPLEMENTATO*
  - Dashboard web con Bootstrap
  - Upload drag-and-drop
  - Generazione report online
  - Statistiche in tempo reale

- [ ] **Integrazione API BrickLink** 🚧 *IN SVILUPPO*
  - Autenticazione OAuth
  - Download automatico inventari
  - Sincronizzazione liste desiderate

- [ ] **Dashboard interattivo** 📋 *PIANIFICATO*
  - Grafici interattivi con Chart.js
  - Filtri dinamici per collezione
  - Confronto tra set

- [ ] **Notifiche automatiche per parti mancanti** 📋 *PIANIFICATO*
  - Sistema di alert email
  - Monitoraggio prezzi
  - Suggerimenti acquisti ottimizzati

### 🆕 Nuove Funzionalità Disponibili

#### **Multi-Format Parser**
```python
from input_handlers import MultiFormatInputParser

parser = MultiFormatInputParser()
results = parser.parse_folder("path/to/mixed/files")
```

#### **Web Interface**
```bash
# Avvia il server web
python web_app.py

# Apri http://localhost:5000 nel browser
```

#### **Formati Supportati**
- **XML**: File inventario BrickLink standard
- **CSV**: Rebrickable, BrickOwl, o formato personalizzato
- **JSON**: Struttura flessibile per API esterne

## 🐛 Troubleshooting

### Problemi Comuni

#### 📁 **"No configuration file found"**
**Soluzione**: Crea o modifica il file `config.json` nella cartella principale:
```json
{
  "reports": [{
    "name": "Test",
    "folder_path": "C:\\path\\to\\xml\\files",
    "color_mapping_path": "BL_color_mapping.json",
    "output_pdf": "test_report.pdf"
  }]
}
```

#### 🎨 **"Color code not found in color mapping"**
**Soluzione**: 
- Verifica che il file `BL_color_mapping.json` sia presente
- Controlla che il file sia un JSON valido
- Il sistema continuerà comunque a funzionare usando i codici numerici

#### 📂 **"Folder not found" o "File not found"**
**Soluzione**:
- Usa percorsi assoluti (es. `C:\MyFolder\`)
- Su Windows usa `\\` o `/` per i separatori
- Verifica i permessi di lettura/scrittura

#### 📊 **Errori nella generazione grafici**
**Soluzione**:
```bash
pip install --upgrade matplotlib
```

#### 🔍 **File XML non processati**
**Soluzione**:
- Verifica che i file abbiano estensione `.xml`
- Controlla che non siano nella lista `excluded_files`
- Assicurati che contengano elementi con `MINQTY > 0`

### 🔧 Debug Avanzato

#### Abilita Logging Dettagliato
Modifica il file `config.json`:
```json
{
  "logging": {
    "level": "DEBUG",
    "file": "debug.log"
  }
}
```

#### Controlla i Log
```bash
# Visualizza gli ultimi log
tail -f lego_analysis.log

# Su Windows
type lego_analysis.log
```

#### Test Singolo File
Per testare un singolo file XML:
```python
from LegoStatusBuildAnalysis import LegoColorReport

report = LegoColorReport(
    folder_path="path/to/single/file/folder",
    color_mapping_path="BL_color_mapping.json", 
    output_pdf="test.pdf"
)
report.process()
```

### 💡 Suggerimenti
- **Backup**: Fai sempre un backup dei tuoi file XML originali
- **Nomi file**: Evita caratteri speciali nei nomi dei file XML
- **Dimensioni**: Per collezioni molto grandi, il processo può richiedere alcuni minuti
- **Memoria**: File XML molto grandi potrebbero richiedere più RAM

## 📞 Supporto

Per problemi, suggerimenti o domande:
- Crea un [Issue](https://github.com/Gianpy99/Lego_Bricklink/issues) su GitHub
- Consulta la [documentazione](https://github.com/Gianpy99/Lego_Bricklink/wiki)

## 📄 Licenza

Questo progetto è distribuito sotto licenza MIT. Vedi il file `LICENSE` per dettagli.

## 🙏 Ringraziamenti

- **BrickLink**: Per la piattaforma e i dati degli inventari
- **Rebrickable**: Per i database dei colori e parti
- **Comunità LEGO**: Per il supporto e i feedback

---

*Sviluppato con ❤️ per la comunità LEGO*
