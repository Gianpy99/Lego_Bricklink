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
├── BL_color_mapping.json              # Mappatura completa codici colore BrickLink
├── BL_color_mapping_FULL.txt          # Mappatura colori in formato testo
├── color_mapping.json                 # Mappatura colori semplificata
├── bricklink_to_rebrickable_color_map.csv # Conversione colori BrickLink-Rebrickable
├── Analysis.xlsx                      # Analisi dati in formato Excel
└── README.md                          # Documentazione del progetto
```

## 🚀 Funzionalità Principali

### 1. Analisi e Report PDF
- **Estrazione dati**: Analizza file XML degli inventari BrickLink
- **Grafici dettagliati**: Genera grafici a barre e a torta per ogni set
- **Statistiche complete**: Quantità minime, possedute e totali per colore
- **Report multi-pagina**: Salvataggio in un singolo file PDF strutturato
- **Rilevamento anomalie**: Evidenzia codici colore mancanti nella mappatura

### 2. Gestione XML Avanzata
- **Combinazione inventari**: Unisce più file XML in un unico inventario
- **Filtro intelligente**: Esclude elementi con quantità minima = 0
- **Deduplicazione**: Combina elementi identici sommando le quantità
- **File ottimizzati**: Genera XML pronti per l'importazione su BrickLink

### 3. Mappatura Colori
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
- Librerie Python richieste:
  ```bash
  pip install matplotlib xml.etree.ElementTree collections json
  ```

### Setup Rapido
1. Clona il repository:
   ```bash
   git clone https://github.com/Gianpy99/Lego_Bricklink.git
   cd Lego_Bricklink
   ```

2. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```

## 📖 Guida all'Uso

### Uso Base - Script Python

```python
# Configurazione percorsi
inventory_folder = "path/to/your/xml/files"
color_mapping_file = "BL_color_mapping.json"
output_pdf = "lego_analysis_report.pdf"

# Avvia l'analisi
python LegoStatusBuildAnalysis.py
```

### Uso Avanzato - Notebook Jupyter

Per analisi interattive e personalizzazioni:
```bash
jupyter notebook LegoStatusBuildAnalysis.ipynb
```

### Configurazione Personalizzata

Modifica i parametri nel script principale:
```python
# Personalizza cartelle e file
INVENTORY_FOLDER = "path/to/inventories"
COLOR_MAPPING = "BL_color_mapping.json"
OUTPUT_PDF = "my_collection_report.pdf"

# Esclusioni file XML
EXCLUDED_FILES = ["file1.xml", "file2.xml"]
```

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

- [ ] Interfaccia web per analisi
- [ ] Supporto per più formati di input
- [ ] Integrazione API BrickLink
- [ ] Dashboard interattivo
- [ ] Notifiche automatiche per parti mancanti

## 🐛 Troubleshooting

### Problemi Comuni
- **Errore mappatura colori**: Verifica che il file JSON sia presente e valido
- **File XML non trovati**: Controlla i percorsi delle cartelle
- **Errori grafici**: Assicurati che matplotlib sia installato correttamente

### Log e Debug
Il sistema genera log dettagliati per identificare problemi:
```python
# Abilita logging debug
import logging
logging.basicConfig(level=logging.DEBUG)
```

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
