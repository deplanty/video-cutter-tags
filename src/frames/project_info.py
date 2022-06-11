import tkinter as tk
from tkinter import ttk

import src.preload as pl


class ProjectInfo(tk.Toplevel):
    def __init__(self, master:tk.Widget, filename:str=None, export_folder:str=None) -> None:
        super().__init__(master)

        self.title(f"{pl.root.title()} - Project Info")

        self.label_filename = ttk.Label(self, text=f"Filename:")
        self.label_filename.grid(row=0, column=0, sticky="w")
        self.label_filename_value = ttk.Label(self, text=filename if filename else "")
        self.label_filename_value.grid(row=0, column=1, sticky="w")
        self.label_export_folder = ttk.Label(self, text="Export Folder:")
        self.label_export_folder.grid(row=1, column=0, sticky="w")
        self.label_export_folder_value = ttk.Label(self, text=export_folder if export_folder else "")
        self.label_export_folder_value.grid(row=1, column=1, sticky="w")
