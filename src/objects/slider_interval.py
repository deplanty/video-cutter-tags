import tkinter as tk


class SliderInterval:
    def __init__(self, slider:tk.Canvas, start:float, stop:float):
        # Variables
        self.slider = slider
        self.start = start
        self.stop = stop
        self.state_selected = False
        # Colors
        self.color_normal = "#25d800"
        self.color_selected = "#45ff45"
        # Draw elements
        pad_x = self.slider.pad_x
        pad_y = self.slider.pad_y + self.slider.cursor_radius
        size = self.slider.size
        self.line_iid = self.slider.create_line(
            pad_x + size * self.start, pad_y + 1,
            pad_x + size * self.stop, pad_y + 1,
            fill=self.color_normal,
            width=4
        )
        self.slider.itemconfigure(self.line_iid, tag=f"interval{self.line_iid}")

        self.slider.tag_bind(f"interval{self.line_iid}", "<Button-1>", self._on_click_interval)

    # Magics

    def __repr__(self) -> str:
        return f"SliderInterval({round(self.start, 2)}, {round(self.stop, 2)})"

    def __str__(self) -> str:
        return f"SliderInterval({round(self.start, 2)}, {round(self.stop, 2)})"

    def __eq__(self, other) -> bool:
        """
        Returns if the interval is equal to another interval.

        Args:
            other (int or SliderInterval): The iid of the other interval or the interval.
        """
        if isinstance(other, SliderInterval):
            return self.line_iid == other.line_iid
        else:
            return self.line_iid == other

    # Events

    def _on_click_interval(self, event):
        """
        Updates the color when the interval is selected and generates an event of the state change.
        Generates <<IntervalSelected>> when the interval is clicked a first time.
        Genrates <<IntervalDeselected>> when the interval is clicked another time.
        """
        if not self.state_selected:
            self.state_selected = True
            self.slider.event_generate("<<IntervalSelected>>", x=self.line_iid)
        else:
            self.state_selected = False
            self.slider.event_generate("<<IntervalDeselected>>", x=self.line_iid)

    # Methods

    def is_selected(self) -> bool:
        """
        Returns the selection state of the interval.
        """
        return self.state_selected

    def update_line(self):
        """
        Updates the interval in the slider canvas.
        """
        # Get new dimensions
        pad_x = self.slider.pad_x
        pad_y = self.slider.pad_y + self.slider.cursor_radius
        size = self.slider.size
        # Update element
        self.slider.coords(
            self.line_iid,
            pad_x + size * self.start, pad_y + 1,
            pad_x + size * self.stop, pad_y + 1,
        )

    def update_color(self):
        """
        Updates the color of the interval based on its state.
        """
        if self.state_selected:
            self.slider.itemconfigure(self.line_iid, fill=self.color_selected)
        else:
            self.slider.itemconfigure(self.line_iid, fill=self.color_normal)
