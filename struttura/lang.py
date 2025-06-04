# Simple multilanguage support for English and Italian

LANGUAGES = {
    'en': {
        'app_title': 'Network Bridge Pro',
        'success': 'SUCCESS: {msg}',
        'error': 'ERROR: {msg}',
        'file': 'File',
        'exit': 'Exit',
        'log': 'Log',
        'view_log': 'View Traceback',
        'help': 'Help',
        'about': 'About',
        'sponsor': 'Sponsor',
        'version': 'Version',
        'language': 'Language',
        'log_viewer_title': 'Traceback Log',
        'close': 'Close',
        'log_file_not_found': 'Log file not found.',
        'no_log_entries': 'No log entries for {level}',
        'usage_tab': 'Usage',
        'features_tab': 'Features',
        'sponsor_on_github': 'Sponsor on GitHub',
        'join_discord': 'Join Discord',
        'buy_me_a_coffee': 'Buy Me a Coffee',
        'join_the_patreon': 'Join the Patreon',
        'about_title': 'About',
        'about_project': 'Project',
        'about_description': 'A LAN Bridge app.',
        'copyright': '\u00a9 2025 Nsfr750',
        'show_version': 'Show Version',
        'version_info': 'Version Information',
        'help_usage': "1. Network Configuration:\n   - Enter the network names for both networks\n   - Enter the IP address or hostname for each network\n   - Click 'Connect' to establish the connection\n\n2. Scanning Networks:\n   - Click 'Scan Networks' to discover devices\n   - Right-click on a device for more options\n   - Use the search box to filter results\n\n3. Logs:\n   - View application logs in the bottom panel\n   - Filter logs by level (All, Info, Warning, Error)\n   - Save logs to a file using the save button\n   - Clear logs with the clear button\n\n4. Context Menu (Right-click on a device):\n   - Open in browser\n   - Copy address to clipboard\n   - Copy all details\n   - Ping selected device",
        'help_features': "• Bridge multiple network connections\n• Scan and discover devices on connected networks\n• Detailed device information and status\n• Real-time logging with filtering options\n• Save and load network configurations\n• Support for both IPv4 and IPv6\n• Cross-platform compatibility\n• Intuitive user interface\n• Responsive design\n• Multi-language support",
        'tools': 'Tools',
        'ping_selected': 'Ping Selected',
        'advanced_scan': 'Advanced Scan...',
    },
    'it': {
        'app_title': 'Network Bridge Pro',
        'success': 'SUCCESSO: {msg}',
        'error': 'ERRORE: {msg}',
        'file': 'File',
        'exit': 'Esci',
        'log': 'Log',
        'view_log': 'Visualizza Traceback',
        'help': 'Aiuto',
        'about': 'Informazioni',
        'sponsor': 'Sostieni',
        'version': 'Versione',
        'language': 'Lingua',
        'log_viewer_title': 'Traceback',
        'close': 'Chiudi',
        'log_file_not_found': 'File di log non trovato.',
        'no_log_entries': 'Nessuna voce di log per {level}',
        'usage_tab': 'Utilizzo',
        'features_tab': 'Funzionalità',
        'sponsor_on_github': 'Sponsorizza su GitHub',
        'join_discord': 'Unisciti a Discord',
        'buy_me_a_coffee': 'Offrimi un caffè',
        'join_the_patreon': 'Unisciti a Patreon',
        'about_title': 'Informazioni',
        'about_project': 'Progetto',
        'about_description': "Un'applicazione di Bridge tra reti.",
        'copyright': '\u00a9 2025 Nsfr750',
        'show_version': 'Mostra Versione',
        'version_info': 'Informazioni Versione',
        'help_usage': "1. Configurazione Rete:\n   - Inserisci i nomi per entrambe le reti\n   - Inserisci l'indirizzo IP o il nome host per ogni rete\n   - Fai clic su 'Connetti' per stabilire la connessione\n\n2. Scansione Reti:\n   - Fai clic su 'Scansiona Reti' per scoprire i dispositivi\n   - Fai clic destro su un dispositivo per ulteriori opzioni\n   - Usa la barra di ricerca per filtrare i risultati\n\n3. Log:\n   - Visualizza i log dell'applicazione nel pannello inferiore\n   - Filtra i log per livello (Tutti, Info, Avvisi, Errori)\n   - Salva i log su file utilizzando il pulsante di salvataggio\n   - Pulisci i log con il pulsante apposito\n\n4. Menu Contestuale (Tasto destro su un dispositivo):\n   - Apri nel browser\n   - Copia indirizzo negli appunti\n   - Copia tutti i dettagli\n   - Esegui ping del dispositivo selezionato",
        'help_features': "• Bridge tra più connessioni di rete\n• Scansione e individuazione dispositivi sulle reti connesse\n• Informazioni dettagliate e stato dei dispositivi\n• Log in tempo reale con opzioni di filtraggio\n• Salvataggio e caricamento delle configurazioni di rete\n• Supporto per IPv4 e IPv6\n• Compatibilità multipiattaforma\n• Interfaccia utente intuitiva\n• Design reattivo\n• Supporto multilingua",
        'tools': 'Strumenti',
        'ping_selected': 'Ping Selezionati',
        'advanced_scan': 'Scansione Avanzata...',
    }
}

import os
import json

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

def _load_lang():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('language', 'en')
    except Exception:
        return 'en'

def _save_lang(lang):
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump({'language': lang}, f)
    except Exception:
        pass

_current_lang = _load_lang()

def set_language(lang):
    global _current_lang
    if lang in LANGUAGES:
        _current_lang = lang
    else:
        _current_lang = 'en'
    _save_lang(_current_lang)

def get_language():
    return _current_lang

def tr(key, **kwargs):
    text = LANGUAGES.get(_current_lang, LANGUAGES['en']).get(key, key)
    return text.format(**kwargs)
