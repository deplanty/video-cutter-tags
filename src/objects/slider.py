from sqlite3 import SQLITE_DROP_TABLE
import tkinter as tk

from .slider_interval import SliderInterval


class Slider(tk.Canvas):
    state_slider_clicked = 1
    state_slider_idle = 0

    def __init__(self, master:tk.Widget, **args):
        super().__init__(master, **args)

        # Variables
        self.percent = 0.0
        self.state_click = self.state_slider_idle
        self.intervals = list()
        self.state_slider = "enabled"  # [enabled, disabled]
        # Colors
        self.color_unread = "#858585"
        self.color_read = "#2585ff"
        # Dimensions
        self.update()
        self.cursor_radius = 6
        self.can_w = self.winfo_width()
        self.can_h = self.winfo_height()
        self.pad_x = self.cursor_radius + 2
        self.pad_y = self.can_h // 2
        self.size = self.can_w - 2 * self.pad_x

        # Draw elements
        self.line_base_iid = self.create_line(
            self.pad_x, self.pad_y,              # Start
            self.size + self.pad_x, self.pad_y,  # End
            fill=self.color_unread,
            width=2,
            tag="slider"
        )

        self.line_current_iid = self.create_line(
            self.pad_x, self.pad_y,
            self.pad_x, self.pad_y,
            fill=self.color_read,
            width=4,
            tag="slider"
        )

        self.cursor_current_iid = self.create_oval(
            self.pad_x - self.cursor_radius, self.pad_y - self.cursor_radius,
            self.pad_x + self.cursor_radius, self.pad_y + self.cursor_radius,
            fill=self.color_read,
            outline="white",
            tags=("slider", "cursor")
        )

        # Bind events
        self.bind("<Configure>", self._on_configure)
        self.tag_bind("slider", "<Button-1>", self._on_click_slider)
        self.tag_bind("slider", "<Motion>", self._on_motion_slider)
        self.tag_bind("slider", "<ButtonRelease-1>", self._on_release_slider)

    # Events

    def _on_configure(self, event:tk.Event):
        """
        Updates the elements of the slider in the canvas.

        Args:
            event (tk.Event): not used.
        """
        self.update()
        # Get new dimensions
        self.can_w = self.winfo_width()
        self.can_h = self.winfo_height()
        self.pad_x = self.cursor_radius + 2
        self.pad_y = self.can_h // 2
        self.size = self.can_w - 2 * self.pad_x
        # Update elements
        self.coords(
            self.line_base_iid,
            self.pad_x, self.pad_y,
            self.size + self.pad_x, self.pad_y
        )
        self.set(self.percent)

        # Update intervals
        for interval in self.intervals:
            interval.update_line()

    def _on_click_slider(self, event:tk.Event):
        """
        Generates the event <<Changing>> when the slider's cursor is clicked.

        Args:
            event (tk.Event): not used.
        """
        if self.state_slider == "disabled":
            return

        # Place cursor where the user clicked if it's not the cursor
        item = self.find_closest(event.x, event.y)
        if "cursor" not in self.itemcget(item, "tag"):
            x = event.x - self.pad_x
            percent = x / self.size
            self.set(percent)

        self.state_click = self.state_slider_clicked
        self.event_generate("<<Changing>>", data=self.percent)

    def _on_motion_slider(self, event:tk.Event):
        """
        Updates the position of the cursor in the slider and the read line.

        Args:
            event (tk.Event): not used.
        """
        if self.state_click == self.state_slider_clicked:
            x = event.x - self.pad_x
            percent = x / self.size
            self.set(percent)

    def _on_release_slider(self, event:tk.Event):
        """
        Generates the event <<Changed>> when the slider's cursor is released.
        """
        self.state_click = self.state_slider_idle
        self.event_generate("<<Changed>>", data=self.percent)

    # Methods

    def get(self) -> float:
        """
        Returns the percent position of the slider.

        Returns:
            float: The position in percent.
        """
        return self.percent

    def get_interval_from_iid(self, iid) -> SliderInterval:
        """
        Returns the interval from the given iid.

        Returns:
            SliderInterval: The selected interval.
        """
        for interval in self.intervals:
            if interval.line_iid == iid:
                return interval

        return None

    def set(self, percent:float):
        """
        Sets the position of the slider in percent.

        Args:
            percent (float): The position in percent.
        """
        if percent < 0:
            percent = 0.0
        elif percent > 1:
            percent = 1.0

        self.percent = percent
        pos = self.size * percent
        self.coords(
            self.line_current_iid,
            self.pad_x, self.pad_y,
            self.pad_x + pos, self.pad_y
        )
        self.coords(
            self.cursor_current_iid,
            self.pad_x + pos - self.cursor_radius, self.pad_y - self.cursor_radius,
            self.pad_x + pos + self.cursor_radius, self.pad_y + self.cursor_radius,
        )

    def add_interval(self, start:float, stop:float) -> SliderInterval:
        """
        Adds an interval under the slider.

        Args:
            start (float): The starting position in percent.
            stop (float): The ending position in percent.

        Returns:
            SliderInterval: The returned interval.
        """
        interval = SliderInterval(self, start, stop)
        self.intervals.append(interval)
        self.intervals.sort(key=lambda interval: interval.start)
        return interval

    def clear_intervals(self):
        """
        Clears all intervals.
        """
        for interval in self.intervals:
            self.delete(interval.line_iid)
        self.intervals.clear()

    def set_state(self, state:str):
        """
        Sets the state of the slider.

        Args:
            state (str): The state of the slider [enabled, disabled].
        """
        if state in ["enabled", "disabled"]:
            self.state_slider = state
