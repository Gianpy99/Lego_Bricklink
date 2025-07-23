# 🧱 BrickLink Integration Guide

## Overview
Il sistema LEGO Analysis supporta l'integrazione con BrickLink per gestire le wanted list, ma con **differenze importanti** basate sul tipo di account.

## 🔍 Tipi di Account BrickLink

### 👤 Account BUYER (Normale)
- **Funzione Disponibile:** ✅ Download file XML
- **Funzione NON Disponibile:** ❌ Upload automatico via API
- **Motivo:** Le API BrickLink per creare/modificare wanted list sono riservate agli account SELLER

### 🛒 Account SELLER 
- **Funzione Disponibile:** ✅ Download file XML
- **Funzione Disponibile:** ✅ Upload automatico via API
- **Motivo:** Account seller hanno accesso completo alle API wanted list

## 📥 Per Account BUYER - Import Manuale

### Step 1: Genera e Scarica XML
1. Vai su **http://localhost:5000/bricklink**
2. Seleziona il file XML wanted list generato dal sistema
3. Clicca **"⬇️ Download File XML"**

### Step 2: Import su BrickLink
1. Vai su [BrickLink Wanted List Import](https://www.bricklink.com/wantedXML.asp)
2. Clicca **"Choose File"** e seleziona il file XML scaricato
3. Seleziona **"Import as New List"** o **"Replace Existing List"**
4. Clicca **"Upload"** per importare

**✅ Metodo garantito per tutti gli account!**

## 🚀 Per Account SELLER - Upload Automatico

### Step 1: Configurazione API (una volta sola)
1. Ottieni credenziali API da [BrickLink API Registration](https://www.bricklink.com/v2/api/register_consumer.page)
2. Vai su **http://localhost:5000/bricklink**
3. Inserisci:
   - **Consumer Key**
   - **Consumer Secret** 
   - **Token**
   - **Token Secret**
4. Clicca **"💾 Salva Credenziali"**

### Step 2: Upload Automatico
1. Seleziona il file XML wanted list
2. Inserisci nome lista (opzionale)
3. Clicca **"🚀 Upload su BrickLink"**

**✨ Funzionalità:**
- ✅ Upload diretto
- ✅ Sostituzione automatica liste esistenti
- ✅ Gestione errori avanzata
- ✅ Rate limiting per rispettare limiti API

## 🔧 Struttura File XML

I file XML generati sono compatibili con il formato BrickLink standard:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<INVENTORY>
  <ITEM>
    <ITEMTYPE>P</ITEMTYPE>
    <ITEMID>3001</ITEMID>
    <COLOR>1</COLOR>
    <MINQTY>4</MINQTY>
    <CONDITION>N</CONDITION>
    <REMARKS>Brick 2x4 White</REMARKS>
  </ITEM>
</INVENTORY>
```

## 🛠 Troubleshooting

### Errore "API not available for buyer account"
- **Causa:** Stai tentando l'upload automatico con account buyer
- **Soluzione:** Usa il download XML + import manuale

### Errore "Authentication failed"
- **Causa:** Credenziali API errate
- **Soluzione:** Verifica credenziali su BrickLink API console

### Errore "Rate limit exceeded"
- **Causa:** Troppe richieste API in poco tempo
- **Soluzione:** Attendi 1-2 minuti e riprova

## 🔐 Sicurezza

- ✅ Credenziali API salvate in modo crittografato
- ✅ Nessuna trasmissione di password in chiaro
- ✅ Token API con scadenza gestita automaticamente

## 📊 Statistiche Supportate

Il sistema rileva automaticamente:
- **Tipo account:** BUYER vs SELLER
- **Nome utente**
- **Nome store** (se account seller)
- **Numero wanted list esistenti**

## 🆘 Supporto

Se hai problemi:
1. Controlla i log del server Flask
2. Verifica connessione internet
3. Controlla validità credenziali API BrickLink
4. Usa sempre il download XML come fallback per account buyer
