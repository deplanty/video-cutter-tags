import tkinter as tk


class Image:
    play_16px = "resources/images/play_16px.png"
    pause_16px = "resources/images/pause_16px.png"
    backward_5s_16px = "resources/images/backward_5s_16px.png"
    backward_10s_16px = "resources/images/backward_10s_16px.png"
    forward_5s_16px = "resources/images/forward_5s_16px.png"
    forward_10s_16px = "resources/images/forward_10s_16px.png"
    cut_start_16px = "resources/images/cut_start_16px.png"
    cut_end_16px = "resources/images/cut_end_16px.png"
    remove_16px = "resources/images/remove_16px.png"
    loop_on_16px = "resources/images/loop_on_16px.png"
    loop_off_16px = "resources/images/loop_off_16px.png"
    cut_16px = "resources/images/cut_16px.png"
    cut_tags_16px = "resources/images/cut_tags_16px.png"

    @classmethod
    def load(cls) -> None:
        cls.play_16px = tk.PhotoImage(file=cls.play_16px)
        cls.pause_16px = tk.PhotoImage(file=cls.pause_16px)
        cls.backward_5s_16px = tk.PhotoImage(file=cls.backward_5s_16px)
        cls.backward_10s_16px = tk.PhotoImage(file=cls.backward_10s_16px)
        cls.forward_5s_16px = tk.PhotoImage(file=cls.forward_5s_16px)
        cls.forward_10s_16px = tk.PhotoImage(file=cls.forward_10s_16px)
        cls.cut_start_16px = tk.PhotoImage(file=cls.cut_start_16px)
        cls.cut_end_16px = tk.PhotoImage(file=cls.cut_end_16px)
        cls.remove_16px = tk.PhotoImage(file=cls.remove_16px)
        cls.loop_on_16px = tk.PhotoImage(file=cls.loop_on_16px)
        cls.loop_off_16px = tk.PhotoImage(file=cls.loop_off_16px)
        cls.cut_16px = tk.PhotoImage(file=cls.cut_16px)
        cls.cut_tags_16px = tk.PhotoImage(file=cls.cut_tags_16px)
