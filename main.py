import tkinter as tk
from tkinter import ttk
import tkinterDnD
import yaml

import src.frames
from src.objects import Image
import src.preload as pl

# TODO: Drag and drop file in the editor


class Application(tkinterDnD.Tk):
    def __init__(self) -> None:
        super().__init__()

        Image.load()

        # Load configuration files
        with open("resources/config/config.yaml") as fid:
            config = yaml.full_load(fid)

        self.title(config["name"])
        self.minsize(**config["minsize"])

        # Load mainframe
        self.frame = src.frames.MainWindow(self)
        self.frame.pack(fill="both", expand=True)

        # Save some parameters in preload
        # TODO: Load the data in the preload
        pl.root = self
        pl.config = config


if __name__ == "__main__":
    app = Application()
    app.mainloop()
