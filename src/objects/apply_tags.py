import tkinter as tk
from tkinter import ttk


class ApplyTags(tk.Canvas):
    def __init__(self, master:tk.Widget, tags:list, tags_selected:list=list()) -> None:
        super().__init__(master)
        self.state_validation = False

        self.tags = tags
        self.tags_selected = tags_selected




if __name__ == "__main__":
    root = tk.Tk()
    root.title("Apply tags")
    root.minsize(200, 200)

    app = ApplyTags(root, ["tag1", "tag2", "tag3"], ["tag1"])
    app.pack(fill="both", expand=True)

    root.mainloop()
