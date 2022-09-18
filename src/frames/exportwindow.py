import tkinter as tk
from tkinter import ttk

from .exportwindow_ui import ExportWindowUI


class ExportWindow(tk.Toplevel):
    def __init__(self, master:tk.Widget, tags:list, tags_selected:list=list()) -> None:
        super().__init__(master)
        self.state_validation = False

        self.ui = ExportWindowUI(self)
        self.ui.button_validate.config(command=self._on_validate)

        self.ui.add_tags(tags)
        for tag in tags_selected:
            self.ui.set_tag(tag, True)

        self.minsize(250, 200)

    # Events

    def _on_validate(self) -> None:
        self.state_validation = True
        self.destroy()

    # Methods

    def get(self) -> dict:
        if self.state_validation is True:
            return {tag: var.get() for tag, var in self.ui.vars_tags.items()}
