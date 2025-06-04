import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import socket
import requests
from urllib.parse import urlparse
import threading
import json
import os
import platform
import subprocess
import sys
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import webbrowser
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import the menu system from the struttura folder
import sys
import os
# Add the parent directory to Python path to import struttura modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from struttura.menu import create_menu_bar
from struttura.about import About
from struttura.help import Help
from struttura.sponsor import Sponsor
from struttura.log_viewer import LogViewer
from struttura.version import get_version
from struttura.lang import tr, set_language, get_language

class NetworkBridgeApp:
    def __init__(self, root):
        # Initialize the scan queue first
        self.scan_queue = queue.Queue()
        
        self.root = root
        self.root.title(tr('app_title'))
        self.root.geometry("1400x960")
        self.app_data_dir = os.path.join(os.path.expanduser('~'), '.network_bridge')
        self.config_file = os.path.join(self.app_data_dir, 'config.json')
        self.log_file = os.path.join(self.app_data_dir, 'app.log')
        
        # Crea la directory dell'applicazione se non esiste
        os.makedirs(self.app_data_dir, exist_ok=True)
        
        # Inizializza il sistema di logging
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Carica la configurazione
        self.config = self.load_config()
        
        # Stile
        self.setup_styles()
        
        # Variabili di stato
        self.credentials = {}
        self.stop_scan = False
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        self.scan_thread = None
        
        # Inizializza le variabili di connessione
        self.net1_connected = False
        self.net2_connected = False
        
        # Inizializza le variabili per i nomi delle reti
        self.net1_name = tk.StringVar(value="Rete 1")
        self.net2_name = tk.StringVar(value="Rete 2")
        
        # Inizializza le variabili per gli indirizzi delle reti
        self.net1_addr = tk.StringVar()
        self.net2_addr = tk.StringVar()
        
        # Inizializza le variabili per i pulsanti di connessione
        self.net1_btn = None
        self.net2_btn = None
        
        # Inizializza il tree widget
        self.tree = None
        
        # Setup the menu
        self.setup_menu()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Carica le reti salvate se presenti
        self.load_saved_networks()
        
        # Setup the main UI
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the main user interface"""
        # Create main paned window
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for network configuration
        self.left_panel = ttk.Frame(self.main_paned, padding="10")
        self.main_paned.add(self.left_panel, weight=1)
        
        # Right panel for logs
        self.right_panel = ttk.Frame(self.main_paned, padding="10")
        self.main_paned.add(self.right_panel, weight=1)
        
        # Setup left panel (network config)
        self.setup_left_panel(self.left_panel)
        
        # Setup right panel (logs)
        self.setup_right_panel(self.right_panel)
        
    def setup_logging(self):
        """Configura il sistema di logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                RotatingFileHandler(self.log_file, maxBytes=5*1024*1024, backupCount=3),
                logging.StreamHandler()
            ]
        )
    
    def load_config(self):
        """Carica la configurazione dal file"""
        default_config = {
            'networks': {},
            'theme': 'clam',
            'scan_ports': [21, 22, 80, 443, 8080, 8443],
            'ping_timeout': 2,
            'max_threads': 10
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Unisci con la configurazione di default
                    return {**default_config, **config}
        except Exception as e:
            self.logger.error(f"Errore nel caricamento della configurazione: {e}")
        
        return default_config
    
    def save_config(self):
        """Salva la configurazione su file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            self.logger.error(f"Errore nel salvataggio della configurazione: {e}")
    
    def setup_styles(self):
        """Configura gli stili dell'interfaccia"""
        style = ttk.Style()
        style.theme_use(self.config.get('theme', 'clam'))
        
        # Stili personalizzati
        style.configure('TButton', padding=5)
        style.configure('TLabel', padding=5)
        style.configure('Treeview', rowheight=25)
        style.configure('Treeview.Heading', font=('Helvetica', 10, 'bold'))
        
        # Colori per lo stato (using standard states)
        style.configure('Status.TLabel',
                      foreground='black',
                      font=('', 10, 'bold'))
        
        # Create custom styles for different statuses
        style.configure('Status.Online.TLabel',
                      foreground='green',
                      font=('', 10, 'bold'))
        style.configure('Status.Offline.TLabel',
                      foreground='red',
                      font=('', 10, 'bold'))
        style.configure('Status.Warning.TLabel',
                      foreground='orange',
                      font=('', 10, 'bold'))
        
        # Avvia il thread per l'elaborazione della coda di scansione
        self.process_scan_queue()
    
    def setup_menu(self):
        """Configura il menu principale"""
        # Create the menu bar using the struttura menu system
        menubar = create_menu_bar(self.root, self)
        
        # Add Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label=tr('ping_selected', default='Ping Selected'), command=self.ping_selected)
        tools_menu.add_command(label=tr('advanced_scan', default='Advanced Scan...'), command=self.advanced_scan)
        menubar.insert_cascade(2, label=tr('tools', default='Tools'), menu=tools_menu)
        
        # Update the window title with the application name and version
        self.update_window_title()
        
        # Set the menu bar
        self.root.config(menu=menubar)
        
        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def update_window_title(self):
        """Update the window title with the current language"""
        self.root.title(f"{tr('app_title')} - v{get_version()}")
    
    def on_close(self):
        """Handle application close event"""
        # Clean up resources
        self.thread_pool.shutdown(wait=False)
        self.root.quit()
    
    def show_about(self):
        """Show the about dialog"""
        About.show_about(self.root)
    
    def show_help(self):
        """Show the help dialog"""
        Help.show_help(self.root)
        
    def show_log_viewer(self):
        """Show the log viewer dialog"""
        LogViewer.show_log(self.root)
    
    def export_results(self):
        """Export scan results to a file"""
        # Implementation for exporting results
        pass
    
    def advanced_scan(self):
        """Show advanced scan options dialog"""
        # Implementation for advanced scan
        pass
    
    def ping_selected(self):
        """Ping selected devices"""
        # Implementation for pinging selected devices
        pass
    
    def show_preferences(self):
        """Show application preferences dialog"""
        # Implementation for preferences dialog
        pass
    
    def setup_left_panel(self, parent):
        """Configura il pannello sinistro con la configurazione delle reti"""
        # Notebook per le schede
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scheda Configurazione Reti
        config_frame = ttk.Frame(notebook, padding="10")
        notebook.add(config_frame, text="Configurazione Reti")
        
        # Frame per la configurazione delle reti
        self.setup_network_config(config_frame)
        
        # Scheda Risorse Trovate
        resources_frame = ttk.Frame(notebook, padding="10")
        notebook.add(resources_frame, text="Risorse Trovate")
        
        # Tabella delle risorse
        self.setup_resources_table(resources_frame)
    
    def stop_scanning(self):
        """Stops any ongoing scan operations"""
        self.stop_scan = True
        self.scan_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.log("Scanning stopped by user", "INFO")
        
    def scan_networks(self):
        """Scans the network for available devices and services"""
        if self.scan_thread and self.scan_thread.is_alive():
            return  # Already scanning
            
        self.stop_scan = False
        self.scan_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.log("Starting network scan...", "INFO")
        
        def _scan():
            try:
                # Simulate network scanning
                import time
                for i in range(1, 6):
                    if self.stop_scan:
                        break
                    time.sleep(1)  # Simulate work
                    self.log(f"Scanning... {i}/5", "INFO")
                
                if not self.stop_scan:
                    self.log("Network scan completed", "INFO")
                    # Update UI with scan results
                    self.root.after(0, self._update_scan_results, ["Device 1", "Device 2", "Device 3"])
                
            except Exception as e:
                self.log(f"Error during scan: {str(e)}", "ERROR")
            finally:
                self.root.after(0, self._scan_completed)
        
        # Start the scan in a separate thread
        self.scan_thread = threading.Thread(target=_scan, daemon=True)
        self.scan_thread.start()
    
    def _update_scan_results(self, devices):
        """Updates the UI with scan results"""
        # Clear existing items in the tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add new items
        for device in devices:
            self.tree.insert("", tk.END, values=(device, "Online", "192.168.1.x"))
    
    def _scan_completed(self):
        """Called when the scan is completed or stopped"""
        self.scan_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
    
    def on_close(self):
        """Handle application close event"""
        try:
            # Stop any ongoing scans
            self.stop_scan = True
            
            # Shutdown the thread pool
            if hasattr(self, 'thread_pool') and self.thread_pool:
                self.thread_pool.shutdown(wait=False)
                
            # Destroy the root window
            self.root.destroy()
        except Exception as e:
            print(f"Error during shutdown: {e}")
            self.root.destroy()

    def setup_network_config(self, parent):
        """Configura la sezione di configurazione delle reti"""
        # Main configuration frame
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Network 1 frame
        net1_frame = ttk.LabelFrame(main_frame, text=tr('network_1_config'), padding="10")
        net1_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Network 1 name
        ttk.Label(net1_frame, text=tr('network_name')).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.net1_name = ttk.Entry(net1_frame, width=30)
        self.net1_name.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Network 1 address
        ttk.Label(net1_frame, text=tr('network_address')).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.net1_addr = ttk.Entry(net1_frame, width=30)
        self.net1_addr.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Network 1 connect/disconnect button
        self.net1_btn = ttk.Button(net1_frame, text=tr('connect'),
                                 command=lambda: self.connect_to_network(1))
        self.net1_btn.grid(row=0, column=2, rowspan=2, padx=10, pady=5)
        
        # Network 2 frame
        net2_frame = ttk.LabelFrame(main_frame, text=tr('network_2_config'), padding="10")
        net2_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Network 2 name
        ttk.Label(net2_frame, text=tr('network_name')).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.net2_name = ttk.Entry(net2_frame, width=30)
        self.net2_name.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Network 2 address
        ttk.Label(net2_frame, text=tr('network_address')).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.net2_addr = ttk.Entry(net2_frame, width=30)
        self.net2_addr.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Network 2 connect/disconnect button
        self.net2_btn = ttk.Button(net2_frame, text=tr('connect'),
                                 command=lambda: self.connect_to_network(2))
        self.net2_btn.grid(row=0, column=2, rowspan=2, padx=10, pady=5)
        
        # Scan controls frame
        scan_frame = ttk.Frame(main_frame)
        scan_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Scan button
        self.scan_btn = ttk.Button(scan_frame, text=tr('quick_scan'),
                                command=self.quick_scan)
        self.scan_btn.pack(side=tk.LEFT, padx=5)
        
        # Stop scan button
        self.stop_btn = ttk.Button(scan_frame, text=tr('stop_scan'),
                                command=self.stop_scanning,
                                state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Bottom button frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10, padx=5, side=tk.BOTTOM)
        
        # Show logs button
        self.btn_show_logs = ttk.Button(btn_frame, text=tr('view_logs'),
                                      command=self.show_log_viewer)
        self.btn_show_logs.pack(side=tk.RIGHT, padx=5)
        
        # Preferences button
        self.btn_prefs = ttk.Button(btn_frame, text=tr('preferences'),
                                  command=self.show_preferences)
        self.btn_prefs.pack(side=tk.RIGHT, padx=5)
        
        # Barra di stato
        self.status_var = tk.StringVar()
        self.status_var.set("Pronto")
        
        self.status_bar = ttk.Label(parent, textvariable=self.status_var,
                                 relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Frame per la configurazione delle reti
        config_frame = ttk.LabelFrame(main_frame, text="Configurazione Reti", padding="10")
        config_frame.pack(fill=tk.X, pady=5)
        
        # Rete 1
        ttk.Label(config_frame, text="Rete 1:").grid(row=0, column=0, sticky=tk.W)
        self.net1_name = ttk.Entry(config_frame, width=20)
        self.net1_name.grid(row=0, column=1, padx=5, pady=2)
        self.net1_name.insert(0, "Rete Locale")
        
        ttk.Label(config_frame, text="Indirizzo IP/URL:").grid(row=0, column=2, padx=(20,0))
        self.net1_addr = ttk.Entry(config_frame, width=30)
        self.net1_addr.grid(row=0, column=3, padx=5, pady=2)
        self.net1_addr.insert(0, "http://localhost:8000")
        
        # Rete 2
        ttk.Label(config_frame, text="Rete 2:").grid(row=1, column=0, sticky=tk.W, pady=(10,0))
        self.net2_name = ttk.Entry(config_frame, width=20)
        self.net2_name.grid(row=1, column=1, padx=5, pady=2)
        self.net2_name.insert(0, "Rete Remota")
        
        ttk.Label(config_frame, text="Indirizzo IP/URL:").grid(row=1, column=2, padx=(20,0), pady=(10,0))
        self.net2_addr = ttk.Entry(config_frame, width=30)
        self.net2_addr.grid(row=1, column=3, padx=5, pady=2)
        self.net2_addr.insert(0, "http://192.168.1.100:8000")
        
        # Pulsanti di controllo
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.btn_connect_net1 = ttk.Button(btn_frame, text="Connetti a Rete 1", 
                                         command=lambda: self.connect_to_network(1))
        self.btn_connect_net1.pack(side=tk.LEFT, padx=5)
        
        self.btn_connect_net2 = ttk.Button(btn_frame, text="Connetti a Rete 2", 
                                         command=lambda: self.connect_to_network(2))
        self.btn_connect_net2.pack(side=tk.LEFT, padx=5)
        
        self.btn_scan = ttk.Button(btn_frame, text="Scansiona Reti", 
                                 command=self.scan_networks)
        self.btn_scan.pack(side=tk.LEFT, padx=5)
        
    def setup_resources_table(self, parent):
        """Configura la tabella delle risorse trovate"""
        # Frame per i controlli della tabella
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Pulsanti di azione rapida
        ttk.Button(controls_frame, text="Aggiorna", 
                  command=self.refresh_resources).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_frame, text="Esporta...",
                  command=self.export_results).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_frame, text="Ping Selezionati",
                  command=self.ping_selected).pack(side=tk.LEFT, padx=2)
        
        # Barra di ricerca
        search_frame = ttk.Frame(controls_frame)
        search_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        ttk.Label(search_frame, text="Cerca:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        search_entry.bind('<KeyRelease>', self.filter_resources)
        
        # Tabella delle risorse
        columns = ("#", "Rete", "Tipo", "Indirizzo", "Stato", "Risposta", "Ultima Verifica")
        self.tree = ttk.Treeview(parent, columns=columns, show='headings', selectmode='extended')
        
        # Configura le colonne
        col_widths = {
            "#": 40,
            "Rete": 150,
            "Tipo": 120,
            "Indirizzo": 200,
            "Stato": 100,
            "Risposta": 100,
            "Ultima Verifica": 150
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=col_widths.get(col, 100), minwidth=50, anchor=tk.W)
        
        # Aggiungi la tabella a un frame con scrollbar
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Menu contestuale
        self.setup_context_menu()
    
    def setup_right_panel(self, parent):
        """Configura il pannello destro con i log"""
        # Frame per i controlli del log
        log_controls = ttk.Frame(parent)
        log_controls.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(log_controls, text="Pulisci Log", 
                  command=self.clear_log).pack(side=tk.LEFT, padx=2)
        ttk.Button(log_controls, text="Salva Log...", 
                  command=self.save_log).pack(side=tk.LEFT, padx=2)
        
        # Filtri di log
        log_filters = ttk.Frame(log_controls)
        log_filters.pack(side=tk.RIGHT)
        
        self.log_level = tk.StringVar(value="INFO")
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in levels:
            rb = ttk.Radiobutton(log_filters, text=level, variable=self.log_level,
                               value=level, command=self.filter_log)
            rb.pack(side=tk.LEFT, padx=2)
        
        # Area di log
        log_frame = ttk.LabelFrame(parent, text="Log Attività", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_area = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.log_area.pack(fill=tk.BOTH, expand=True)
        
        # Configura il logger per scrivere anche nell'area di testo
        self.setup_text_handler()
    
    def setup_context_menu(self):
        """Configura il menu contestuale per la tabella"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Apri nel browser", 
                                    command=self.open_in_browser)
        self.context_menu.add_command(label="Ping", 
                                    command=self.ping_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Copia Indirizzo", 
                                    command=self.copy_address)
        self.context_menu.add_command(label="Copia Tutto", 
                                    command=self.copy_all)
        
        # Associa il tasto destro del mouse
        self.tree.bind("<Button-3>", self.show_context_menu)
    
    def setup_text_handler(self):
        """Configura l'handler per scrivere i log nell'area di testo"""
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
                self.text_widget.config(state=tk.DISABLED)
            
            def emit(self, record):
                msg = self.format(record)
                self.text_widget.config(state=tk.NORMAL)
                self.text_widget.insert(tk.END, msg + '\n')
                self.text_widget.see(tk.END)
                self.text_widget.config(state=tk.DISABLED)
        
        text_handler = TextHandler(self.log_area)
        text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(text_handler)
        
        # Variabili di stato
        self.net1_connected = False
        self.net2_connected = False
        self.scan_in_progress = False
        self.resources = []  # Lista per memorizzare tutte le risorse trovate
        
        # Carica le reti salvate se presenti
        self.load_saved_networks()
        
        self.log("Applicazione avviata. Configura le reti e connettiti.", "INFO")
    
    def log(self, message, level="INFO"):
        """Aggiunge un messaggio al log
        
        Args:
            message (str): Il messaggio da registrare
            level (str): Livello di log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        try:
            # Invia il messaggio al logger di Python
            logger = logging.getLogger(__name__)
            log_level = getattr(logging, level.upper(), logging.INFO)
            logger.log(log_level, message)
            
            # Aggiorna la barra di stato per i messaggi importanti
            if level in ("ERROR", "CRITICAL"):
                self.status_var.set(f"Errore: {message[:100]}")
            
            # Scrive anche nella console per debug
            print(f"[{level}] {message}")
        except Exception as e:
            print(f"Errore nel logging: {e}")
    
    def connect_to_network(self, net_number):
        """Tenta di connettersi alla rete specificata"""
        if net_number == 1:
            addr = self.net1_addr.get().strip()
            name = self.net1_name.get().strip() or f"Rete {net_number}"
            btn = self.btn_connect_net1
            connected = self.net1_connected
        else:
            addr = self.net2_addr.get().strip()
            name = self.net2_name.get().strip() or f"Rete {net_number}"
            btn = self.btn_connect_net2
            connected = self.net2_connected
        
        if not addr:
            messagebox.showerror("Errore", f"Inserisci un indirizzo valido per {name}")
            return
        
        if not connected:
            # Prova a connetterti
            self.log(f"Connessione a {name} ({addr}) in corso...", "INFO")
            
            # Disabilita i controlli durante la connessione
            self.toggle_connection_controls(False)
            
            # Avvia la connessione in un thread separato
            self.thread_pool.submit(self.try_network_connection, net_number, addr, name, btn)
        else:
            # Disconnessione
            self.disconnect_network(net_number, name, btn)
    
    def try_network_connection(self, net_number, addr, name, btn):
        """Tenta di stabilire una connessione alla rete"""
        try:
            # Verifica se l'URL è valido
            parsed_url = urlparse(addr if '://' in addr else f'http://{addr}')
            hostname = parsed_url.hostname or parsed_url.path
            port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
            
            # Prova a risolvere l'hostname
            ip_address = socket.gethostbyname(hostname)
            
            # Verifica se la porta è raggiungibile
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)  # Timeout di 3 secondi
            
            result = sock.connect_ex((ip_address, port))
            sock.close()
            
            if result == 0 or port == 0:  # Porta 0 per testare solo la risoluzione DNS
                # Salva le informazioni sulla connessione
                if net_number == 1:
                    self.net1_connected = True
                    self.net1_info = {
                        'name': name,
                        'addr': addr,
                        'ip': ip_address,
                        'port': port,
                        'connected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                else:
                    self.net2_connected = True
                    self.net2_info = {
                        'name': name,
                        'addr': addr,
                        'ip': ip_address,
                        'port': port,
                        'connected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                
                # Aggiorna l'interfaccia
                self.root.after(0, lambda: self.update_connection_status(
                    net_number, 
                    True, 
                    f"Connesso a {name} ({ip_address})"
                ))
                
                self.log(f"Connessione a {name} ({addr}) stabilita con successo", "INFO")
                
                # Salva la configurazione della rete
                self.save_network_config()
            else:
                raise ConnectionError(f"Porta {port} non raggiungibile")
                
        except Exception as e:
            error_msg = f"Errore durante la connessione a {name}: {str(e)}"
            self.root.after(0, lambda: messagebox.showerror("Errore di connessione", error_msg))
            self.log(error_msg, "ERROR")
        finally:
            self.root.after(0, lambda: self.toggle_connection_controls(True))
    
    def disconnect_network(self, net_number, name, btn):
        """Disconnette la rete specificata"""
        if net_number == 1:
            self.net1_connected = False
            if hasattr(self, 'net1_info'):
                delattr(self, 'net1_info')
        else:
            self.net2_connected = False
            if hasattr(self, 'net2_info'):
                delattr(self, 'net2_info')
        
        btn.config(text=f"Connetti a {name}")
        self.log(f"Disconnesso da {name}", "INFO")
        self.save_network_config()
    
    def toggle_connection_controls(self, enabled):
        """Abilita o disabilita i controlli di connessione"""
        state = tk.NORMAL if enabled else tk.DISABLED
        
        self.btn_connect_net1.config(state=state)
        self.btn_connect_net2.config(state=state)
        self.net1_addr.config(state=state)
        self.net2_addr.config(state=state)
        self.net1_name.config(state=state)
        self.net2_name.config(state=state)
        
        # Aggiorna lo stato del pulsante di scansione
        if self.net1_connected and self.net2_connected:
            self.btn_scan.config(state=tk.NORMAL)
        else:
            self.btn_scan.config(state=tk.DISABLED)
    
    def update_connection_status(self, net_number, connected, message):
        """Aggiorna lo stato della connessione nell'interfaccia"""
        try:
            if net_number == 1:
                self.net1_connected = connected
                name = self.net1_name.get().strip() or "Rete 1"
                btn = self.btn_connect_net1
                status_label = getattr(self, 'net1_status', None)
            else:
                self.net2_connected = connected
                name = self.net2_name.get().strip() or "Rete 2"
                btn = self.btn_connect_net2
                status_label = getattr(self, 'net2_status', None)
            
            # Aggiorna il testo del pulsante
            if connected:
                btn.config(text=f"Disconnetti da {name}", style='Accent.TButton')
                if status_label:
                    status_label.config(text="Online", style='Status.TLabel', foreground='green')
            else:
                btn.config(text=f"Connetti a {name}", style='TButton')
                if status_label:
                    status_label.config(text="Offline", style='Status.TLabel', foreground='red')
            
            # Aggiorna lo stato della barra di stato
            self.status_var.set(message)
            
            # Aggiorna lo stato del pulsante di scansione
            if self.net1_connected and self.net2_connected:
                self.btn_scan.config(state=tk.NORMAL)
                self.status_var.set("Entrambe le reti connesse. Pronto per la scansione.")
            else:
                self.btn_scan.config(state=tk.DISABLED)
                
            # Aggiorna la visualizzazione delle risorse
            self.refresh_resources()
            
        except Exception as e:
            self.log(f"Errore nell'aggiornamento dello stato: {e}", "ERROR")
    
    def quick_scan(self):
        """Esegue una scansione rapida delle reti connesse"""
        if not (self.net1_connected or self.net2_connected):
            messagebox.showwarning("Attenzione", "Connettersi ad almeno una rete prima di eseguire la scansione.")
            return
            
        self.log("Avvio scansione rapida delle reti...", "INFO")
        self.scan_in_progress = True
        self.btn_scan.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        
        # Pulisci la tabella delle risorse
        self.clear_resources_table()
        
        # Prepara i parametri per la scansione
        scan_params = []
        
        if self.net1_connected and hasattr(self, 'net1_info'):
            net_info = self.net1_info
            scan_params.append({
                'network': net_info['name'],
                'ip': net_info['ip'],
                'ports': [80, 443, 8080, 8443, 22, 21, 3389, 3306, 5432, 27017]
            })
            
        if self.net2_connected and hasattr(self, 'net2_info'):
            net_info = self.net2_info
            scan_params.append({
                'network': net_info['name'],
                'ip': net_info['ip'],
                'ports': [80, 443, 8080, 8443, 22, 21, 3389, 3306, 5432, 27017]
            })
            
        # Avvia la scansione in un thread separato
        self.thread_pool.submit(self.perform_network_scan, scan_params)
    
    def perform_network_scan(self, scan_params):
        """Esegue la scansione delle reti con i parametri specificati"""
        try:
            start_time = datetime.now()
            total_ports = sum(len(net['ports']) for net in scan_params)
            scanned_ports = 0
                
            self.log(f"Inizio scansione di {total_ports} porte su {len(scan_params)} reti...", "INFO")
                
            # Funzione per testare una singola porta
            def test_port(ip, port, timeout):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(timeout)
                    result = sock.connect_ex((ip, port))
                    sock.close()
                    return port, result == 0
                except Exception as e:
                    return port, False
            
            # Esegui la scansione per ogni rete
            for net in scan_params:
                network_name = net['network']
                ip = net['ip']
                ports = net['ports']
                timeout = net.get('timeout', 2)
                    
                self.log(f"Scansione di {network_name} ({ip})...", "INFO")
                    
                # Usa ThreadPoolExecutor per scansionare le porte in parallelo
                with ThreadPoolExecutor(max_workers=50) as executor:
                    futures = [executor.submit(test_port, ip, port, timeout) for port in ports]
                        
                    for future in as_completed(futures):
                        if self.stop_scan:
                            self.log("Scansione interrotta dall'utente", "WARNING")
                            return
                                
                        port, is_open = future.result()
                        scanned_ports += 1
                            
                        # Aggiorna la barra di stato
                        progress = (scanned_ports / total_ports) * 100
                        self.root.after(0, lambda p=progress: self.status_var.set(
                            f"Scansione in corso: {scanned_ports}/{total_ports} porte ({p:.1f}%)"
                        ))
                            
                        if is_open:
                            # Determina il servizio in base alla porta
                            service = self.get_service_name(port)
                                
                            # Aggiungi la risorsa alla tabella
                            self.root.after(0, lambda p=port, s=service, n=network_name: 
                                         self.add_resource(n, s, f"{ip}:{p}", "Online", "Risposta positiva"))
                
            # Scansione completata
            elapsed = (datetime.now() - start_time).total_seconds()
            self.log(f"Scansione completata in {elapsed:.2f} secondi", "INFO")
                
        except Exception as e:
            self.log(f"Errore durante la scansione: {e}", "ERROR")
            self.root.after(0, lambda: messagebox.showerror("Errore", f"Errore durante la scansione: {e}"))
        finally:
            self.scan_in_progress = False
            self.stop_scan = False
            self.root.after(0, lambda: self.btn_scan.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.btn_stop.config(state=tk.DISABLED))
            self.root.after(0, lambda: self.status_var.set("Scansione completata"))
    
    def get_service_name(self, port):
        """Restituisce il nome del servizio in base alla porta"""
        common_ports = {
            20: "FTP Data",
            21: "FTP Control",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            143: "IMAP",
            389: "LDAP",
            443: "HTTPS",
            445: "SMB",
            465: "SMTPS",
            514: "Syslog",
            587: "SMTP Submission",
            636: "LDAPS",
            993: "IMAPS",
            995: "POP3S",
            1433: "MSSQL",
            1521: "Oracle DB",
            2049: "NFS",
            3306: "MySQL",
            3389: "RDP",
            5432: "PostgreSQL",
            5900: "VNC",
            6379: "Redis",
            8000: "HTTP Alt",
            8080: "HTTP Proxy",
            8443: "HTTPS Alt",
            9000: "PHP-FPM",
            9090: "Openfire",
            9200: "Elasticsearch",
            10000: "Webmin"
        }
        return common_ports.get(port, f"Porta {port}")
        
    def add_resource(self, network, resource_type, address, status, response):
        """Aggiunge una risorsa alla tabella"""
        try:
            item_id = str(len(self.tree.get_children()) + 1)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
            self.tree.insert('', tk.END, values=(
                item_id, network, resource_type, address, status, response, timestamp
            ))
                
            # Aggiungi alla lista delle risorse
            self.resources.append({
                'id': item_id,
                'network': network,
                'type': resource_type,
                'address': address,
                'status': status,
                'response': response,
                'timestamp': timestamp
            })
                
            # Se la tabella ha molti elementi, mantieni solo gli ultimi 1000
            if len(self.resources) > 1000:
                self.resources = self.resources[-1000:]
                self.refresh_resources()
                    
        except Exception as e:
            self.log(f"Errore nell'aggiunta della risorsa: {e}", "ERROR")
        
    def clear_resources_table(self):
        """Pulisce la tabella delle risorse"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.resources = []
        
    def refresh_resources(self):
        """Aggiorna la visualizzazione delle risorse"""
        try:
            # Salva lo stato di espansione degli elementi
            expanded = {}
            for item in self.tree.get_children():
                expanded[item] = self.tree.item(item, 'open')
                
            # Ricrea la tabella
            self.clear_resources_table()
        except Exception as e:
            self.log(f"Errore nell'aggiornamento delle risorse: {e}", "ERROR")
            
    def filter_resources(self, event=None):
        """Filtra le risorse nella tabella in base al testo di ricerca"""
        if not hasattr(self, 'search_var') or not hasattr(self, 'tree'):
            return
            
        search_term = self.search_var.get().lower()
        
        # Se la barra di ricerca è vuota, mostra tutte le risorse
        if not search_term:
            for item in self.tree.get_children():
                self.tree.item(item, tags=())
                self.tree.detach(item)
                self.tree.reattach(item, '', 'end')
            return
            
        # Altrimenti, filtra le risorse
        for item in self.tree.get_children():
            values = self.tree.item(item, 'values')
            if any(search_term in str(value).lower() for value in values):
                self.tree.item(item, tags=())
                self.tree.detach(item)
                self.tree.reattach(item, '', 'end')
            else:
                self.tree.detach(item)
                
    def open_in_browser(self):
        """Apre la risorsa selezionata nel browser predefinito"""
        try:
            selected_items = self.tree.selection()
            if not selected_items:
                messagebox.showinfo("Info", "Seleziona una risorsa da aprire")
                return
                
            item = selected_items[0]
            values = self.tree.item(item, 'values')
            if not values or len(values) < 3:
                messagebox.showerror("Errore", "Impossibile aprire la risorsa: indirizzo non valido")
                return
                
            url = values[2]  # L'indirizzo è nel terzo campo
            
            # Verifica se l'URL inizia con http:// o https://
            if not (url.startswith('http://') or url.startswith('https://')):
                url = 'http://' + url
                
            # Apri l'URL nel browser predefinito
            import webbrowser
            webbrowser.open(url)
            self.log(f"Aperto nel browser: {url}", "INFO")
            
        except Exception as e:
            error_msg = f"Errore durante l'apertura nel browser: {str(e)}"
            messagebox.showerror("Errore", error_msg)
            self.log(error_msg, "ERROR")
            
    def copy_address(self):
        """Copia l'indirizzo della risorsa selezionata negli appunti"""
        try:
            selected_items = self.tree.selection()
            if not selected_items:
                messagebox.showinfo("Info", "Seleziona una risorsa da copiare")
                return
                
            item = selected_items[0]
            values = self.tree.item(item, 'values')
            if not values or len(values) < 3:
                messagebox.showerror("Errore", "Impossibile copiare l'indirizzo: indirizzo non valido")
                return
                
            address = values[2]  # L'indirizzo è nel terzo campo
            
            # Copia l'indirizzo negli appunti
            self.root.clipboard_clear()
            self.root.clipboard_append(address)
            self.root.update()  # Mantieni l'accesso agli appunti dopo la chiusura del programma
            
            self.log(f"Indirizzo copiato negli appunti: {address}", "INFO")
            
        except Exception as e:
            error_msg = f"Errore durante la copia dell'indirizzo: {str(e)}"
            messagebox.showerror("Errore", error_msg)
            self.log(error_msg, "ERROR")
            
    def copy_all(self):
        """Copia tutti i dettagli della risorsa selezionata negli appunti"""
        try:
            selected_items = self.tree.selection()
            if not selected_items:
                messagebox.showinfo("Info", "Seleziona una risorsa da copiare")
                return
                
            item = selected_items[0]
            values = self.tree.item(item, 'values')
            if not values:
                messagebox.showerror("Errore", "Impossibile copiare i dettagli: dati non validi")
                return
            
            # Crea una stringa formattata con tutti i dettagli
            details = []
            columns = self.tree['columns']
            for i, column in enumerate(columns):
                # Ottieni l'intestazione della colonna
                col_text = self.tree.heading(column)['text']
                # Aggiungi l'intestazione e il valore alla lista
                details.append(f"{col_text}: {values[i]}")
            
            # Unisci i dettagli con le nuove righe
            details_text = "\n".join(details)
            
            # Copia i dettagli negli appunti
            self.root.clipboard_clear()
            self.root.clipboard_append(details_text)
            self.root.update()  # Mantieni l'accesso agli appunti dopo la chiusura del programma
            
            self.log("Dettagli della risorsa copiati negli appunti", "INFO")
            
        except Exception as e:
            error_msg = f"Errore durante la copia dei dettagli: {str(e)}"
            messagebox.showerror("Errore", error_msg)
            self.log(error_msg, "ERROR")
            
    def show_context_menu(self, event):
        """Mostra il menu contestuale al click destro su una risorsa"""
        # Seleziona l'elemento cliccato
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            
            # Mostra il menu contestuale
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                # Assicurati che il menu venga rilasciato
                self.context_menu.grab_release()
                
    def clear_log(self):
        """Pulisce il contenuto della finestra di log"""
        if hasattr(self, 'log_area'):
            self.log_area.config(state=tk.NORMAL)
            self.log_area.delete(1.0, tk.END)
            self.log_area.config(state=tk.DISABLED)
            self.log("Log pulito", "INFO")
            
    def save_log(self):
        """Salva il contenuto del log in un file"""
        if not hasattr(self, 'log_area'):
            return
            
        try:
            # Chiedi all'utente dove salvare il file
            filename = filedialog.asksaveasfilename(
                defaultextension=".log",
                filetypes=[("Log files", "*.log"), ("All files", "*.*")],
                title="Salva log come"
            )
            
            if not filename:  # L'utente ha annullato il salvataggio
                return
                
            # Ottieni il contenuto del log
            log_content = self.log_area.get(1.0, tk.END)
            
            # Scrivi il contenuto nel file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(log_content)
                
            self.log(f"Log salvato in: {filename}", "INFO")
            messagebox.showinfo("Successo", f"Log salvato con successo in:\n{filename}")
            
        except Exception as e:
            error_msg = f"Errore durante il salvataggio del log: {str(e)}"
            messagebox.showerror("Errore", error_msg)
            self.log(error_msg, "ERROR")
            
    def filter_log(self):
        """Filtra i messaggi di log in base al livello selezionato"""
        if not hasattr(self, 'log_level') or not hasattr(self, 'log_area'):
            return
            
        selected_level = self.log_level.get()
        
        # Se è selezionato "Tutti", mostra tutti i messaggi
        if selected_level == "Tutti":
            for tag in self.log_area.tag_names():
                if tag != "sel":
                    self.log_area.tag_configure(tag, elide=False)
            return
            
        # Altrimenti, nascondi i messaggi con livello diverso da quello selezionato
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            if level == selected_level:
                self.log_area.tag_configure(level, elide=False)
            else:
                self.log_area.tag_configure(level, elide=True)
                
    def load_saved_networks(self):
        """Carica le configurazioni di rete salvate"""
        try:
            if not os.path.exists(self.config_file):
                self.log("Nessuna configurazione di rete salvata trovata", "INFO")
                return
                
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                
            # Carica le configurazioni delle reti
            if 'net1' in config:
                net1 = config['net1']
                self.net1_name.set(net1.get('name', 'Rete 1'))
                if 'address' in net1:
                    self.net1_addr.set(net1['address'])
                
            if 'net2' in config:
                net2 = config['net2']
                self.net2_name.set(net2.get('name', 'Rete 2'))
                if 'address' in net2:
                    self.net2_addr.set(net2['address'])
                    
            self.log("Configurazioni di rete caricate con successo", "INFO")
            
        except json.JSONDecodeError:
            self.log("Errore nel file di configurazione: formato non valido", "ERROR")
        except Exception as e:
            self.log(f"Errore durante il caricamento delle configurazioni: {str(e)}", "ERROR")
            
    def process_scan_queue(self):
        """Elabora la coda delle scansioni di rete"""
        try:
            while not self.scan_queue.empty():
                task = self.scan_queue.get_nowait()
                try:
                    task()
                except Exception as e:
                    self.log(f"Errore durante l'esecuzione del task di scansione: {str(e)}", "ERROR")
                finally:
                    self.scan_queue.task_done()
        except queue.Empty:
            pass
            
        # Ripianifica il controllo della coda
        self.root.after(1000, self.process_scan_queue)

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkBridgeApp(root)
    root.mainloop()
