import tkinter as tk
from tkinter import ttk

from src.objects import Slider, Table, Image


class MainWindowUI:
    def __init__(self, master:tk.Widget) -> None:
        self.master = master
        self.root = master._nametowidget(master.winfo_parent())

        # Menu
        self.menubar = tk.Menu(master)
        self.menubar_file = tk.Menu(self.menubar, tearoff=0)
        self.menubar_file.add_command(label="Open project")
        self.menubar_file.add_command(label="Save project")
        self.menubar_file.add_command(label="Save project as...")
        self.menubar_file.add_separator()
        self.menubar_file.add_command(label="Open video")
        self.menubar.add_cascade(label="File", menu=self.menubar_file)
        self.menubar_play = tk.Menu(self.menubar, tearoff=0)
        self.menubar_play.add_radiobutton(label="Speed x0.5", value=0.5)
        self.menubar_play.add_radiobutton(label="Speed x1", value=1.0)
        self.menubar_play.add_radiobutton(label="Speed x2", value=2.0)
        self.menubar_play.add_radiobutton(label="Speed x4", value=4.0)
        self.menubar.add_cascade(label="Play", menu=self.menubar_play)
        self.menubar.add_command(label="Info")
        self.root.config(menu=self.menubar)

        self.frame_main = ttk.Frame(master)
        self.frame_main.grid(row=0, column=0, sticky="nsew")
        # Frame player
        self.frame_player = ttk.Frame(self.frame_main)
        self.frame_player.pack(fill="both", expand=True)
        # Slider
        self.slider = Slider(self.frame_main, height=20)
        self.slider.pack(fill="x")
        # Frame player panel control
        self.frame_player_panel = ttk.Frame(self.frame_main)
        self.frame_player_panel.pack()
        self.button_prev_10s = ttk.Button(self.frame_player_panel, image=Image.backward_10s_16px)
        self.button_prev_10s.pack(side="left", padx=5, pady=5)
        self.button_prev_5s = ttk.Button(self.frame_player_panel, image=Image.backward_5s_16px)
        self.button_prev_5s.pack(side="left", padx=5, pady=5)
        self.button_play = ttk.Button(self.frame_player_panel, image=Image.play_16px)
        self.button_play.pack(side="left", padx=5, pady=5)
        self.button_next_5s = ttk.Button(self.frame_player_panel, image=Image.forward_5s_16px)
        self.button_next_5s.pack(side="left", padx=5, pady=5)
        self.button_next_10s = ttk.Button(self.frame_player_panel, image=Image.forward_10s_16px)
        self.button_next_10s.pack(side="left", padx=5, pady=5)
        # Frame cutting
        self.frame_cutting = ttk.Frame(self.frame_main)
        self.frame_cutting.pack()
        self.button_new_start_cut = ttk.Button(self.frame_cutting, image=Image.cut_start_16px)
        self.button_new_start_cut.pack(side="left", padx=5)
        self.button_new_end_cut = ttk.Button(self.frame_cutting, image=Image.cut_end_16px)
        self.button_new_end_cut.pack(side="left", padx=5)
        # Frame list of cuts
        self.frame_cuts = ttk.Frame(master)
        self.frame_cuts.grid(row=0, column=1, sticky="nsew")
        self.frame_cuts_buttons = ttk.Frame(self.frame_cuts)
        self.frame_cuts_buttons.pack(fill="x")
        self.button_remove_cut = ttk.Button(self.frame_cuts_buttons, image=Image.remove_16px)
        self.button_remove_cut.pack(side="left", padx=5, pady=5)
        self.button_play_cut = ttk.Button(self.frame_cuts_buttons, image=Image.play_16px)
        # self.button_play_cut.pack(side="left", padx=5, pady=5)
        self.button_play_cut_loop = ttk.Button(self.frame_cuts_buttons, image=Image.loop_on_16px)
        # self.button_play_cut_loop.pack(side="left", padx=5, pady=5)
        self.table_cuts = Table(self.frame_cuts)
        self.table_cuts.pack(fill="both", expand=True, padx=5, pady=5)
        self.frame_export = ttk.Frame(self.frame_cuts)
        self.frame_export.pack()
        self.button_cut = ttk.Button(self.frame_export, image=Image.cut_16px)
        self.button_cut.pack(side="left", padx=5, pady=5)
        self.button_cut_tags = ttk.Button(self.frame_export, image=Image.cut_tags_16px)
        self.button_cut_tags.pack(side="left", padx=5, pady=5)

        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)

    def video_paused(self) -> None:
        self.button_play.config(image=Image.pause_16px)

    def video_played(self) -> None:
        self.button_play.config(image=Image.play_16px)
