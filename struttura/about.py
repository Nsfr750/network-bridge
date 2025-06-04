import tkinter as tk
from tkinter import ttk
from .lang import tr

# Version information
VERSION = '1.0.0'  # Keep this in sync with __init__.py

class About:
    @staticmethod
    def show_about(root):
        about_dialog = tk.Toplevel(root)
        about_dialog.title(tr('about'))
        about_dialog.geometry('500x350')
        about_dialog.transient(root)
        about_dialog.grab_set()

        # Main container with padding
        container = ttk.Frame(about_dialog, padding="20")
        container.pack(fill=tk.BOTH, expand=True)

        # App title
        title = ttk.Label(
            container,
            text=tr('app_title'),
            font=('Helvetica', 16, 'bold')
        )
        title.pack(pady=10)

        # Version
        version = ttk.Label(
            container,
            text=f"{tr('version')} {VERSION}"
        )
        version.pack(pady=5)

        # Description
        description = ttk.Label(
            container,
            text=tr('about_description'),
            justify=tk.CENTER,
            wraplength=400
        )
        description.pack(pady=20, fill=tk.X)

        # Copyright
        copyright = ttk.Label(
            container,
            text='© 2025 Nsfr750',
            font=('Helvetica', 8)
        )
        copyright.pack(side=tk.BOTTOM, pady=10)

        # Close button
        close_btn = ttk.Button(
            container,
            text=tr('close'),
            command=about_dialog.destroy
        )
        close_btn.pack(pady=20)
