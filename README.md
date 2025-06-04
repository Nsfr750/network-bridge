<div align="center">
  <h1>🌉 Network Bridge</h1>
  <h3>Monitoraggio e gestione avanzata di reti locali</h3>
  
  [![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
  [![License: GPL v3](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
  [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
  
  ![Network Bridge Screenshot](templates/images/screenshot.png)
</div>

> Un'applicazione avanzata per il monitoraggio e il bridging di reti locali, con supporto multilingua e un'interfaccia utente intuitiva.

## ✨ Caratteristiche principali

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem;">
  <div>
    <h4>🌐 Gestione Reti</h4>
    <ul>
      <li>Gestione di più reti contemporaneamente</li>
      <li>Monitoraggio in tempo reale</li>
      <li>Configurazione intuitiva</li>
    </ul>
  </div>
  <div>
    <h4>🔍 Analisi</h4>
    <ul>
      <li>Scansione avanzata delle risorse</li>
      <li>Logging dettagliato con filtri</li>
      <li>Esportazione dati in vari formati</li>
    </ul>
  </div>
  <div>
    <h4>🎨 Interfaccia</h4>
    <ul>
      <li>Interfaccia utente moderna</li>
      <li>Tema scuro/chiaro</li>
      <li>Supporto multilingua</li>
    </ul>
  </div>
</div>

## 🛠️ Requisiti di sistema

| Componente | Requisito |
|-----------|-----------|
| **Python** | 3.8 o superiore |
| **Sistema Operativo** | Windows 10/11, macOS 10.15+, Linux |
| **RAM** | Minimo 2GB (4GB consigliati) |
| **Spazio su disco** | 100MB liberi |
| **Connessione di rete** | Richiesta |
| **Permessi** | Amministratore (per alcune funzionalità) |

> **Nota:** Alcune funzionalità avanzate potrebbero richiedere ulteriori dipendenze.

## 🚀 Installazione

### Prerequisiti
Assicurati di avere [Python 3.8+](https://www.python.org/downloads/) installato.

### Passaggi di installazione

```bash
# 1. Clona il repository
git clone https://github.com/tuoutente/network-bridge.git
cd network-bridge

# 2. Crea e attiva un ambiente virtuale (consigliato)
python -m venv venv
# Su Windows:
.\venv\Scripts\activate
# Su macOS/Linux:
source venv/bin/activate

# 3. Installa le dipendenze
pip install -r requirements.txt
```

### Verifica l'installazione
```bash
python --version  # Dovrebbe mostrare Python 3.8 o superiore
pip list  # Mostra i pacchetti installati
```

## 🚀 Avvio rapido

### Avvia l'applicazione
```bash
python main.py
```

### Configurazione iniziale
1. **Aggiungi una nuova rete**
   - Clicca su "Nuova Rete"
   - Inserisci un nome descrittivo
   - Specifica l'indirizzo IP o hostname
   - Configura le impostazioni avanzate (opzionale)

2. **Connessione**
   - Seleziona la rete
   - Clicca su "Connetti"
   - Verifica lo stato della connessione

### Funzionalità principali
- **Scansione Rete**
  - Scopri dispositivi connessi
  - Analizza le porte aperte
  - Verifica i servizi attivi

- **Monitoraggio**
  - Visualizza statistiche in tempo reale
  - Imposta avvisi personalizzati
  - Esporta i dati di monitoraggio

- **Logging**
  - Visualizza log dettagliati
  - Applica filtri avanzati
  - Esporta i log in vari formati

## 🛠️ Struttura del progetto

```
network-bridge/
├── app/                 # Codice sorgente principale
│   ├── bridge.py        # Logica principale dell'applicazione
│   └── ...
├── struttura/           # Moduli di supporto
│   ├── lang.py          # Gestione lingue
│   └── ...
├── assets/              # Risorse (immagini, icone, ecc.)
├── tests/               # Test automatici
├── requirements.txt     # Dipendenze Python
├── README.md            # Questo file
└── main.py              # Punto di ingresso
```

## 🌍 Supporto lingue

Attualmente supportato:
- 🇬🇧 Inglese (predefinito)
- 🇮🇹 Italiano

## 🤝 Contributi

I contributi sono ben accetti! Per favore leggi le nostre [linee guida per i contributi](CONTRIBUTING.md) prima di inviare una pull request.

## 📄 Licenza

Questo progetto è concesso in licenza con la licenza GPL3 - vedi il file [LICENSE](LICENSE) per i dettagli.

## 📧 Contatti

Per domande o supporto, contattaci a: Nsfr750@yandex.com
- Alcune funzionalità potrebbero richiedere privilegi di amministratore
- L'applicazione è pensata per uso interno e non include misure di sicurezza avanzate per ambienti di produzione
