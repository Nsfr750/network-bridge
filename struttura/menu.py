import tkinter as tk
from tkinter import messagebox
import sys
from .about import About
from .help import Help
from .sponsor import Sponsor
from .log_viewer import LogViewer
from .version import show_version
from .lang import tr, set_language

LANG_OPTIONS = {'English': 'en', 'Italiano': 'it'}


def create_menu_bar(root, app):
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    
    # Set up window close handler
    def on_close():
        try:
            # Try to clean up the thread pool if it exists
            if hasattr(app, 'thread_pool'):
                app.thread_pool.shutdown(wait=False)
        except Exception as e:
            print(f"Error during cleanup: {e}")
        finally:
            root.quit()
    
    root.protocol("WM_DELETE_WINDOW", on_close)

    # File menu
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label=tr('exit'), command=on_close)
    menubar.add_cascade(label=tr('file'), menu=file_menu)

    # Log menu
    log_menu = tk.Menu(menubar, tearoff=0)
    log_menu.add_command(label=tr('view_log'), command=lambda: LogViewer.show_log(root))
    menubar.add_cascade(label=tr('log'), menu=log_menu)

    # Language menu
    def set_lang_and_restart(lang_code):
        set_language(lang_code)
        root.destroy()
        import os
        os.execl(sys.executable, sys.executable, *sys.argv)

    lang_menu = tk.Menu(menubar, tearoff=0)
    for label, code in LANG_OPTIONS.items():
        lang_menu.add_command(label=label, command=lambda c=code: set_lang_and_restart(c))
    menubar.add_cascade(label=tr('language'), menu=lang_menu)

# Help menu
    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label=tr('about'), command=lambda: About.show_about(root))
    help_menu.add_command(label=tr('help'), command=lambda: Help.show_help(root))
    help_menu.add_separator()    
    help_menu.add_command(label=tr('sponsor'), command=lambda: Sponsor(root).show_sponsor())
    menubar.add_cascade(label=tr('help'), menu=help_menu)

    return menubar
