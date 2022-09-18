import time
import tkinter as tk
from tkinter import ttk


"""
This progress bar was an old project and could be better.
But it works.
"""


class Progressbar(tk.Toplevel):
    """
    Create a progress bar to display the progress of events

    Args:
        status (str)
        n (int > 0)
        n_max (int > n)
    """

    def __init__(self, master=None, status:str="", n:int=0, n_max:int=100):
        tk.Toplevel.__init__(self, master)

        self.mode = "determinate"
        self.status = ""

        self.n = tk.IntVar(0)
        self.n_max = 10
        self.percent = tk.StringVar("")

        self.__set_args(status, n, n_max)

        self.withdraw()
        self.createUI()
        self.centerUI()
        self.resizable(False, False)
        self.deiconify()
        self.grab_set()
        self.loop()

    def createUI(self):
        """
        Create the UI
        """

        self.title("Progression")

        f = ttk.Frame(self)
        f.pack(fill="both", padx=10, pady=10)

        l = ttk.Label(f, textvariable=self.percent, anchor="w")
        l.pack(fill="x")

        self.bar = ttk.Progressbar(
            f,
            orient="horizontal",
            length=400,
            mode=self.mode,
            maximum=self.n_max,
            variable=self.n,
        )
        self.bar.pack(padx=5, pady=5)

        f_btn = ttk.Frame(f)
        f_btn.pack(fill="x")
        self.b_ok = ttk.Button(f_btn, text="Ok", state="disabled", command=self.btn_ok)
        self.b_ok.pack(side="right", padx=5, pady=5)

        self.__update_percent()
        self.__update_progressbar()
        self.__update_btn_ok()

    def centerUI(self):
        """
        Center the UI on screen
        """

        self.update()
        w_screen = self.winfo_screenwidth()
        h_screen = self.winfo_screenheight()
        w = self.winfo_width()
        h = self.winfo_height()
        pos_x = w_screen // 2 - w // 2
        pos_y = h_screen // 2 - h // 2
        self.geometry("%dx%d+%d+%d" % (w, h, pos_x, pos_y))

    def loop(self):
        self.update()
        self.after(100, self.loop)

    def set(self, status:str=None, n:int=None, n_max:int=None):
        """
        Set variables values

        Args:
            status (str)
            n (int > 0)
            n_max (int > n)
        """

        self.__set_args(status, n, n_max)
        self.__update_percent()
        self.__update_progressbar()
        self.__update_btn_ok()
        self.update()

    def set_mode(self, mode:str="determinate"):
        """
        Set the mode of the progressbar

        Args:
            mode (str): [determinate, indeterminate]
        """

        self.mode = mode
        self.bar.configure(mode=mode)
        if mode == "indeterminate":
            self.bar.start()

    def step(self, delta=1, pause=0.01):
        """
        Next step of the progression
        A pause time can be set to let the changes be visible (in seconds)
        """

        time.sleep(pause)

        if self.n.get() + delta <= self.n_max:
            self.n.set(self.n.get() + delta)

        self.__update_percent()
        self.__update_btn_ok()
        self.update()

    def wait_ok(self):
        """
        Wait for the user to press "Ok" button
        """

        self.b_ok.config(state="enabled")
        self.wait_window()

    def btn_ok(self, *args):
        """
        Press ok to close the window when progress ends
        """

        self.grab_release()
        self.destroy()

    def __update_percent(self):
        """
        Update percentage
        """

        n = self.n.get()

        if self.mode == "indeterminate":
            self.percent.set(self.status)
        else:
            if self.n_max == 0:
                p = self.status
            else:
                if self.status != "":
                    p = "%03d%% - %s" % (100.0 * n / self.n_max, self.status)
                else:
                    p = "%03d%%" % (100.0 * n / self.n_max)
            self.percent.set(p)

    def __update_progressbar(self):
        """
        Update the progressbar
        """

        self.bar.config(maximum=self.n_max)

    def __update_btn_ok(self):
        """
        Update the Ok Button
        """

        if self.mode == "indeterminate":
            self.b_ok.config(state="disabled")
        else:
            if self.n.get() >= self.n_max:
                self.b_ok.config(state="enabled")
            else:
                self.b_ok.config(state="disabled")

    def __set_args(self, status:str=None, n:int=None, n_max:int=None):
        """
        Set variable values from the kwargs for the `init` and `set` function
        """

        if status is not None:
            self.status = status
        if n is not None:
            self.n.set(n)
        if n_max is not None:
            self.n_max = n_max

            if n_max < self.n.get():
                self.n_max = self.n.get()
                raise ValueError(f"n_max ({n_max}) must be greater than n ({self.n.get()}).")
