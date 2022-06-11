import tkinter as tk
from tkinter import ttk


class ExportWindowUI:
    def __init__(self, master:tk.Widget) -> None:
        self.master = master
        self.vars_tags = dict()

        self.frame_tags = ttk.LabelFrame(master, text="Tags")
        self.frame_tags.pack(fill="both", expand=True)

        self.button_validate = ttk.Button(master, text="Validate")
        self.button_validate.pack()

    # Methods

    def add_tags(self, tags:list) -> None:
        for tag in tags:
            self.add_tag(tag)

    def add_tag(self, tag:str, value:bool=False) -> None:
        var = tk.BooleanVar(self.master, value)
        self.vars_tags[tag] = var
        checkbutton = ttk.Checkbutton(self.frame_tags, text=tag, variable=var)
        checkbutton.pack()

    def set_tag(self, tag:str, value:bool) -> None:
        self.vars_tags[tag].set(value)
