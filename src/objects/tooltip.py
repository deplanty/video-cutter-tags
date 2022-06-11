import tkinter as tk
from tkinter import ttk


class Tooltip:
    def __init__(self, widget, text="", delay=800):
        self.__widget = widget
        self.__text = text
        self.__delay = delay
        self.__top = None
        self.__top_shadow = None
        self.__id_func = None

        self.__widget.bind("<Enter>", self.__onEnter)
        self.__widget.bind("<Leave>", self.__onLeave)

    def __createUI(self, *args):
        """
        Create the UI
        """

        self.__top = tk.Toplevel(self.__widget, background="#000000")
        self.__top.overrideredirect(True)
        l = tk.Label(self.__top, text=self.__text, bg="#FFFFDC")
        l.pack(padx=1, pady=1, ipadx=1, ipady=1)

        self.__top.update()
        h = self.__top.winfo_reqheight()
        x = self.__top.winfo_pointerx()
        y = self.__top.winfo_pointery()
        self.__top.geometry("+%s+%s" % (x, y - h))

        style = ttk.Style(self.__top)
        style.configure("Tooltip.TLabel", background="#FFFFDC")

    def __onEnter(self, *args):
        """
        Show the popup after the delay
        """

        if "disabled" not in self.__widget.state():
            self.__id_func = self.__widget.after(self.__delay, self.__createUI)

    def __onLeave(self, *args):
        """
        If the popup is already shown, destroy it
        Else remove the delay to display the popup
        """

        if self.__top is not None:
            self.__top.destroy()

        if self.__id_func is not None:
            self.__widget.after_cancel(self.__id_func)
            self.__id_func = None


def set(widget:tk.Widget, text:str, delay:int=800) -> None:
    """
    Sets the tooltip texdt for the widget.

    Args:
        widget (tk.Widget): widget where to add the widget.
        text (str): text to display.
        delay (int, optional): delay before the tooltip shows. Defaults to 800.
    """

    Tooltip(widget, text, delay)
