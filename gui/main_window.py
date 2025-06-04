import tkinter as tk
from struttura.menu import create_menu_bar
from struttura.logger import log_info, log_error
from struttura.lang import tr

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(tr('app_title'))
        # Menu bar
        create_menu_bar(self, self)
        # Variables
        self.file_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.output_filename = tk.StringVar()
        # Log box
        self.log_box = tk.Text(self, height=12, state='disabled', wrap='word')
        self.log_box.grid(row=5, column=0, columnspan=3, sticky="we", padx=5, pady=5)
  
    def append_log(self, text):
        self.log_box.config(state='normal')
        self.log_box.insert(tk.END, text)
        self.log_box.see(tk.END)
        self.log_box.config(state='disabled')
        log_info(text.strip())

    def _show_success(self, msg):
        log_info(tr('success', msg=msg))
        self.append_log(f"{tr('success', msg=msg)}\n")

    def _show_error(self, msg):
        log_error(tr('error', msg=msg))
        self.append_log(f"{tr('error', msg=msg)}\n")
