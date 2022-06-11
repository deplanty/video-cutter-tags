import tkinter as tk
from tkinter import ttk
from unittest import main



class Table(ttk.Frame):
    """
    Table with editable cells

    Args:
        master (tk.Widget): master of the table
        *args: ttk.Treeview arguments
        **kwargs: ttk.Treeview keyword arguments
    """

    def __init__(self, master, *args, **kwargs):
        ttk.Frame.__init__(self, master, *args, **kwargs)

        self.list_id = list()
        self.header = None
        self.blocked = set()
        self.toggled = dict()
        self.choices = dict()
        self.choices_multiple = dict()
        self.n_rows = 1
        self.n_cols = 0

        self.var_entry = tk.StringVar(self, "")

        self.tv = ttk.Treeview(self, selectmode="browse")
        self.tv.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(self, command=self.tv.yview)
        self.tv.configure(yscrollcommand=sb.set)
        sb.pack(side="left", fill="y")

        self.tv.bind("<Double-Button-1>", self._on_double_click)

    # Events

    def _on_double_click(self, event):
        """
        Manage event when double clic on cell
        """

        # If no item is focused
        iid = self.tv.focus()
        if iid == "":
            return

        # Cannot select first column
        col = self.tv.identify_column(event.x)
        col = int(col.lstrip("#")) - 1
        if col < 0:
            return

        if col in self.blocked:
            return
        elif col in self.toggled:
            vals = list(self.tv.item(iid, "values"))
            vals[col] = self.toggle_next(col, vals[col])
            self.tv.item(iid, values=vals)
        else:
            self.ask_entry_value(iid, col)

    # Methods

    def ask_entry_value(self, iid, col):
        """
        Show the entry at the correct location on the treeview
        """

        def save_and_close(*args):
            new = self.var_entry.get()
            item["values"][col] = new
            self.tv.item(iid, values=item["values"])
            self.event_generate("<<TableUpdated>>")
            close()

        def close(*args):
            e.destroy()

        def onTab(*args):
            def nextCol(iid, col):
                if col + 1 < self.n_cols:
                    new_col = col + 1
                else:
                    self.tv.focus_set()
                    ID_prev = self.tv.focus()
                    self.tv.event_generate("<Down>")
                    ID_cur = self.tv.focus()
                    if ID_prev != ID_cur:
                        iid = ID_cur
                        new_col = 0
                    else:
                        return iid, -1

                if new_col not in self.blocked and new_col not in self.toggled:
                    return iid, new_col
                else:
                    return nextCol(iid, new_col)

            save_and_close()
            # Current row
            ID, new_col = nextCol(iid, col)
            if new_col != -1:
                self.ask_entry_value(ID, new_col)

        item = self.tv.item(iid)
        self.var_entry.set(item["values"][col])

        bbox = self.tv.bbox(iid, column=col)
        bbox = {k: v for k, v in zip(["x", "y", "width", "height"], bbox)}

        if col in self.choices:
            e = ttk.Combobox(self, textvariable=self.var_entry, state="readonly")
            e.configure(values=self.choices[col])
            e.place(**bbox)
            e.bind("<<ComboboxSelected>>", save_and_close)
            e.select_clear()
            e.grab_set()
            e.focus_set()
            e.after(100, lambda: e.event_generate("<Down>"))
        if col in self.choices_multiple:
            selected = self.var_entry.get()
            selected = selected.split(", ")
            choices = dict()
            for choice in self.choices_multiple[col]:
                if choice in selected:
                    choices[choice] = True
                else:
                    choices[choice] = False
            top = tk.Toplevel(self)
            e = ListOfChoices(top, choices)
            e.pack(fill="both", expand=True)
            x, y = self.winfo_rootx(), self.winfo_rooty()
            top.geometry(f"+{x + self.winfo_x()}+{y + bbox['y'] + bbox['height']}")
            top.grab_set()
            top.wait_window()
            choices = e.get()
            answer = ", ".join([choice for choice, value in choices.items() if value])
            self.choices_multiple[col] = list(choices.keys())
            self.var_entry.set(answer)
            save_and_close()
            return
        else:
            e = ttk.Entry(self, textvariable=self.var_entry)
            e.place(**bbox)
            e.select_range(0, "end")
            e.icursor("end")
            e.focus_set()
            e.bind("<FocusOut>", save_and_close)

        e.bind("<Escape>", close)
        e.bind("<Return>", save_and_close)
        e.bind("<Tab>", onTab)

    def update_table(self, matrix, id_col=None):
        """
        Update the data contained in the table

        Args:
            matrix (list): matrix to set in the table
        """

        # Clear previous data
        for child in self.tv.get_children():
            self.tv.delete(child)

        self.list_id.clear()
        self.n_rows = 1

        # Set the data
        for line in matrix:
            if id_col is not None:
                iid = line.pop(id_col)
            else:
                iid = None

            iid = self.tv.insert("", "end", iid, text=self.n_rows, values=line)
            self.list_id.append(iid)
            self.n_rows += 1
        self.event_generate("<<TableUpdated>>")

    def update_row(self, row, values):
        """
        Update a row of the table

        Args:
            row (int): row to update
            values (list): values to set
        """

        iid = self.list_id[row]
        self.tv.item(iid, values=values)
        self.event_generate("<<TableUpdated>>")

    def set(self, matrix, header=False, id_col=None, widths=None):
        """
        Set the data in the table

        Args:
            matrix (list): data the display
            header (bool or list, optional): if False then do not set header, if True then use the first line oh the matrix, if list then use it as header
            id_col (int): column containing the IDs, if None, create them
            widths (list): size of each column
        """

        # Get the header
        self.header = header
        if header is True:
            head = matrix.pop(0)
        elif isinstance(header, (list, tuple)):
            head = [x for x in header]
        else:
            n = len(matrix[0])
            head = [""] * n

        if id_col is not None:
            head.pop(id_col)

        # Set the header
        self.n_cols = len(head)
        self.tv.configure(columns=head)
        self.tv.column("#0", width=50)
        for i, label in enumerate(head, 1):
            iid = f"#{i}"
            self.tv.heading(iid, text=label)

        # Set columns size
        if widths is not None:
            for i, w in enumerate(widths, 1):
                iid = f"#{i}"
                self.tv.column(iid, width=w, minwidth=w, stretch=True)

        # Set the data
        self.update_table(matrix, id_col)
        self.event_generate("<<TableUpdated>>")

    def get(self):
        """
        Return the data of the table

        Returns:
            list: matrix of the table data
        """

        data = list()

        # Manage the header
        # If there is a header
        if self.header is True:
            # Get the titles (without the ID column)
            head = list()
            for i in range(self.n_cols):
                item = self.tv.heading(f"#{i+1}")
                head.append(item["text"])
            head.insert(0, "ID")
            data.append(head)
        # If the header was a list
        elif isinstance(self.header, list):
            data.append(self.header)

        # Stack data
        for iid in self.list_id:
            item = self.tv.item(iid)
            line = item["values"]
            # If the line is not empty
            if not all(x == "" for x in line):
                line = [str(x) for x in line]
                data.append([iid] + line)

        return data

    def add_row(self, iid=None, values=None, edit=False):
        """
        Add a new line to the table.
        If values is not None, add values as the new line
        """

        if values is None:
            values = [""] * self.n_cols

        iid = self.tv.insert("", "end", iid, text=self.n_rows, values=values)
        self.list_id.append(iid)
        self.n_rows += 1

        self.tv.focus(iid)
        self.tv.selection_set(iid)

        if edit:
            # Find the first editable column
            for col in range(len(self.tv.item(iid, "values"))):
                if col not in self.blocked:
                    # Edit it
                    self.ask_entry_value(iid, col)
                    break
        self.event_generate("<<TableUpdated>>")

    def remove(self, iid):
        """
        Remove the element from its identifier

        Args:
            iid (int or str): identifier of the element
        """

        self.list_id.remove(iid)

        # Update line numbers
        data = self.get()
        data.pop(0)
        self.update_table(data, 0)

    def clear(self):
        """
        Remove all the elements in the table.
        """

        for iid in self.list_id:
            self.tv.delete(iid)
        self.list_id.clear()
        self.n_rows = 1
        self.event_generate("<<TableUpdated>>")

    def block_columns(self, *cols):
        """
        Block the edition of some columns

        Args:
            cols (int): column numbers blocked
        """

        self.blocked.update(cols)

    def unblock_columns(self, *cols):
        """
        Unblock the edition of some columns

        Args:
            cols (int or str): column numbers unblocked, if "all", unblock all
        """

        if cols == "all":
            self.blocked.clear()
        else:
            for c in cols:
                try:
                    self.blocked.remove(c)
                except:
                    pass

    def toggle_values_columns(self, *cols, values=["•", "◘"]):
        """
        Toggle values of some columns

        Args:
            cols (int or str): column numbers affected
            values (list): list of item to cycle
        """

        for col in cols:
            self.toggled[col] = values

    def toggle_next(self, col, item):
        """
        Go to next item for the column from an item
        """

        i = self.toggled[col].index(item)
        if i + 1 >= len(self.toggled[col]):
            i = 0
        else:
            i += 1

        return self.toggled[col][i]

    def choice_values_columns(self, *cols, list_choices):
        """
        Set the columns that are limited by some choices

        Args:
            cols (int): columns affected by the choices
            list_choices (list): list of selectable items
        """

        for col in cols:
            self.choices[col] = list_choices

    def choice_multiple_values_columns(self, *cols, list_choices):
        """
        Set the columns that are limited by some choices

        Args:
            cols (int): columns affected by the choices
            list_choices (list): list of selectable items
        """

        for col in cols:
            self.choices_multiple[col] = list_choices

    def sort(self, with_col=0, func=None):
        """
        Sort the table using values of the given column

        Args:
            with_col (int, optional): Defaults to 0. column used to sort the table
        """

        def sort(line):
            return str(line[with_col]).lower()

        # Get table data
        data = self.get()

        # Remove header to sort only the data
        header = data.pop(0)
        if func is None:
            data.sort(key=sort)
        else:
            data.sort(key=func)
        data.insert(0, header)

        # Set the sorted data in the table
        data.pop(0)
        self.update_table(data, 0)

    def get_selected(self):
        """
        Return the selected item
        """

        select = self.tv.selection()
        if len(select) == 0:
            return None
        else:
            return select[0]

    def get_selected_row(self):
        """
        Return the selected row
        """

        select = self.tv.selection()
        if len(select) == 0:
            return None

        iid = select[0]
        return iid, list(self.tv.item(iid, "values"))

    def get_selected_row_index(self):
        """
        Return the selected row index
        """

        select = self.tv.selection()
        if len(select) == 0:
            return None

        iid = select[0]
        return self.tv.index(iid)

    def select_row(self, row):
        """
        Selects the given row.
        """

        data = self.get()
        iid = data[row + 1][0]
        self.tv.selection_set(iid)



class ListOfChoices(ttk.Frame):
    def __init__(self, master:tk.Widget, choices:dict):
        super().__init__(master)

        self.choices = choices

        # All the checkboxes
        self.frame_choices = ttk.Frame(self)
        self.frame_choices.pack(fill="x")
        self.list_vars = list()
        for choice, value in self.choices.items():
            self.add_checkbox(choice, value)
        # Add a new checkbox
        self.frame_add = ttk.Frame(self)
        self.frame_add.pack(fill="x")
        self.entry = ttk.Entry(self.frame_add)
        self.entry.pack(fill="x", side="left", padx=5, pady=2)
        self.button_add = ttk.Button(self.frame_add, text="+", command=self.on_button_add_choice)
        self.button_add.pack(fill="x", padx=5, pady=2)
        # Validate the checkboxes
        self.button_validate = ttk.Button(self.master, text="Validate", command=self.on_button_validate)
        self.button_validate.pack(fill="x", padx=5, pady=2)

    def add_checkbox(self, choice:str, value:bool=False):
        var = tk.BooleanVar(self, value, choice)
        cb = ttk.Checkbutton(self.frame_choices, text=choice, variable=var)
        cb.pack(fill="x", padx=5, pady=2)
        self.list_vars.append(var)

    # Events

    def on_button_add_choice(self):
        if self.entry.get():
            self.choices[self.entry.get()] = False
            self.add_checkbox(self.entry.get())

        self.entry.delete(0, tk.END)

    def on_button_validate(self):
        self.master.destroy()

    # Methods

    def get(self) -> dict:
        return {str(var): var.get() for var in self.list_vars}


if __name__ == "__main__":
    root = tk.Tk()
    table = Table(root)
    table.pack(fill="both", expand=True)
    table.set([["Value", "Text"], [1, "Yes"], [2, "No"]], True)
    table.choice_multiple_values_columns(1, 2, list_choices=["Yes", "No", "Maybe"])
    root.mainloop()
