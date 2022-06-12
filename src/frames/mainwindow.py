import datetime
import os
from re import A
import time
import tkinter as tk
import tkinter.filedialog
from tkinter import N, Y, ttk
import vlc
import yaml

import src.frames
from src.objects import Image
import src.preload as pl
from src.objects import tooltip

from .mainwindow_ui import MainWindowUI


class MainWindow(ttk.Frame):
    def __init__(self, master:tk.Widget) -> None:
        super().__init__(master)

        # Variables
        self.project_filename = None
        self.media_filename = None
        self.media_length = 0
        self.loop_update_interval = 200  # In milliseconds
        self.loop_slider_update_iid = None
        self.loop_on_cut_state = True
        self.loop_on_cut_iid = None
        # Load UI
        self.ui = MainWindowUI(self)
        self.ui.menubar_file.entryconfig(0, command=self._on_menu_open_project)
        self.ui.menubar_file.entryconfig(1, command=self._on_menu_save_project)
        self.ui.menubar_file.entryconfig(2, command=self._on_menu_save_project_as)
        self.ui.menubar_file.entryconfig(4, command=self._on_menu_open_video)
        self.var_play_speed = tk.DoubleVar(self, 1.0)
        self.ui.menubar_play.entryconfig(0, variable=self.var_play_speed, command=self._on_menu_set_play_speed)
        self.ui.menubar_play.entryconfig(1, variable=self.var_play_speed, command=self._on_menu_set_play_speed)
        self.ui.menubar_play.entryconfig(2, variable=self.var_play_speed, command=self._on_menu_set_play_speed)
        self.ui.menubar_play.entryconfig(3, variable=self.var_play_speed, command=self._on_menu_set_play_speed)
        self.ui.menubar.entryconfig(3, command=self._on_menu_info)
        self.ui.button_play.configure(command=self._on_play)
        self.ui.button_prev_10s.configure(command=self._on_prev_10s)
        self.ui.button_prev_5s.configure(command=self._on_prev_5s)
        self.ui.button_next_5s.configure(command=self._on_next_5s)
        self.ui.button_next_10s.configure(command=self._on_next_10s)
        self.ui.button_new_start_cut.configure(command=self._on_start_cut)
        self.ui.button_new_end_cut.configure(command=self._on_end_cut)
        self.ui.button_remove_cut.configure(command=self._on_remove_cut)
        self.ui.button_play_cut.configure(command=self._on_play_cut)
        self.ui.button_play_cut_loop.configure(command=self._on_play_cut_loop)
        self.ui.button_cut.configure(command=self._on_export_cuts)
        self.ui.button_cut_tags.configure(command=self._on_export_cuts_tags)

        self.ui.slider.set_state("disabled")

        tooltip.set(self.ui.button_new_start_cut, "Start cut section.")
        tooltip.set(self.ui.button_new_end_cut, "End cut section.")
        tooltip.set(self.ui.button_cut, "Cuts all the sections and fuse them into a single video.")
        tooltip.set(self.ui.button_cut_tags, "Cuts all the sections containing the selected tags and fuse them into a single video.")
        tooltip.set(self.ui.button_remove_cut, "Remove the selected section.")

        # Setup VLC
        self.setup_vlc()

        self.ui.table_cuts.set([["Start", "End", "Tags"]], True, widths=[60, 60, 120])
        self.ui.table_cuts.choice_multiple_values_columns(2, list_choices=[])

    # Menu

    def _on_menu_open_project(self) -> None:
        """
        Opens and loads a project.
        """
        filename = tk.filedialog.askopenfilename(
            filetypes=(("Cuts project", "*.cut"), ("All files", "*.*"))
        )
        if not filename:
            return

        self.setup_bindings()
        self.ui.table_cuts.clear()
        self.load_project(filename)

    def _on_menu_save_project(self) -> None:
        """
        Saves the current project or asks for a filename if it's not saved.
        """
        if self.project_filename is None:
            self._on_menu_save_project_as()
            return

        self.save_project(self.project_filename)

    def _on_menu_save_project_as(self) -> None:
        """
        Asks for a filename and saves the current project.
        """
        file = os.path.basename(self.media_filename)
        file = os.path.splitext(file)[0]
        filename = tk.filedialog.asksaveasfilename(
            initialfile=f"{file}.cut",
            filetypes=(("Cuts project", "*.cut"), ("All files", "*.*")),
            defaultextension=".cut"
        )
        if not filename:
            return

        self.project_filename = filename
        self.save_project(filename)

    def _on_menu_open_video(self) -> None:
        filename = tk.filedialog.askopenfilename(
            filetypes=(("All files", "*.*"),)
        )
        if not filename:
            return

        # Set binding on slider after charging a first media
        self.setup_bindings()
        self.ui.table_cuts.clear()
        self.load_media(filename)
        self.project_filename = None

    def _on_menu_set_play_speed(self) -> None:
        speed = self.var_play_speed.get()
        if self.media_filename:
            self.vlc_player.set_rate(speed)

    def _on_menu_info(self) -> None:
        src.frames.ProjectInfo(self, self.media_filename)

    # Events

    def _on_slider_changing(self, event) -> None:
        # When slider is being dragger, stop loop to update slider
        if self.loop_slider_update_iid is not None:
            self.after_cancel(self.loop_slider_update_iid)
            self.loop_slider_update_iid = None

    def _on_slider_change(self, event):
        length = self.vlc_player.get_length()
        percent = self.ui.slider.get()
        self.vlc_player.set_time(round(length * percent))
        # Once slider is changed, start loop to update slider
        self.run_loop_update_slider()

    def _on_table_update(self, event) -> None:
        self.update_all_intervals()

    def _on_slider_interval_selected(self, event) -> None:
        interval_iid = event.x
        interval = self.ui.slider.get_interval_from_iid(interval_iid)
        i = self.ui.slider.intervals.index(interval)
        self.ui.table_cuts.select_row(i)

    def _on_play(self) -> None:
        if not self.media_filename:
            return

        # If playing, pause
        if self.vlc_player.is_playing():
            self.media_pause()
            self.ui.video_paused()
        # If paused, play
        elif self.vlc_player.get_media():
            self.media_play()
            self.ui.video_played()

    def _on_prev_5s(self) -> None:
        current_time = self.vlc_player.get_time()
        if current_time - 5 >= 0:
            self.vlc_player.set_time(current_time - 5_000)
        else:
            self.vlc_player.set_time(0)

    def _on_prev_10s(self) -> None:
        current_time = self.vlc_player.get_time()
        if current_time - 10 >= 0:
            self.vlc_player.set_time(current_time - 10_000)
        else:
            self.vlc_player.set_time(0)

    def _on_next_5s(self) -> None:
        current_time = self.vlc_player.get_time()
        if current_time + 5 <= self.vlc_player.get_length():
            self.vlc_player.set_time(current_time + 5_000)
        else:
            self.vlc_player.set_time(self.vlc_player.get_length())

    def _on_next_10s(self) -> None:
        current_time = self.vlc_player.get_time()
        if current_time + 10 <= self.vlc_player.get_length():
            self.vlc_player.set_time(current_time + 10_000)
        else:
            self.vlc_player.set_time(self.vlc_player.get_length())

    def _on_start_cut(self) -> None:
        # Add only if a media is loaded
        if not self.vlc_player.get_media():
            return

        current_time = self.vlc_player.get_time() // 1000  # In seconds
        current_time = time.strftime("%H:%M:%S", time.gmtime(current_time))

        # If in wait of end cut
        row = self.ui.table_cuts.get_selected_row()
        if row and row[1][1] == "":
            _, row = row
            # Update start cut
            row[0] = current_time
            row_index = self.ui.table_cuts.get_selected_row_index()
            self.ui.table_cuts.update_row(row_index, row)
        else:
            # Add new interval
            self.ui.table_cuts.add_row(values=[current_time, "", ""])
            self.ui.table_cuts.sort(func=lambda x: time.strptime(x[1], "%H:%M:%S"))

            # Select the new row
            data = self.ui.table_cuts.get()
            data.pop(0)
            for i, (_, start, stop, _) in enumerate(data):
                if start == current_time and stop == "":
                    self.ui.table_cuts.select_row(i)
                    break

    def _on_end_cut(self) -> None:
        # Add only if there is a start cut
        data = self.ui.table_cuts.get()
        if len(data) == 1:
            return

        current_time = self.vlc_player.get_time() // 1000  # In seconds
        current_time = time.strftime("%H:%M:%S", time.gmtime(current_time))
        # Check if a cut is selected
        row = self.ui.table_cuts.get_selected_row()
        if not row:
            return

        _, row = row
        # Check if end cut is after start cut
        start = time.strptime(row[0], "%H:%M:%S")
        end = time.strptime(current_time, "%H:%M:%S")
        if end > start:
            row[1] = current_time
            row_index = self.ui.table_cuts.get_selected_row_index()
            self.ui.table_cuts.update_row(row_index, row)

    def _on_remove_cut(self) -> None:
        """
        Removes a cut from the table and the slider.
        """
        row = self.ui.table_cuts.get_selected_row()
        if not row:
            return

        iid, _ = row
        self.ui.table_cuts.remove(iid)
        self.update_all_intervals()

    def _on_play_cut(self) -> None:
        """
        Plays a cut in loop or stop loop if playing.
        """
        row = self.ui.table_cuts.get_selected_row()
        if not row:
            return

        _, row = row
        start = self.get_seconds(row[0])
        self.vlc_player.set_time(round(start * 1000))
        self.loop_on_cut_iid = self.after(self.loop_update_interval, self.loop_on_cut)

    def _on_play_cut_loop(self) -> None:
        """
        Toogles loop on cut state.
        """
        if self.loop_on_cut_state is True:
            self.loop_on_cut_state = False
            self.ui.button_play_cut_loop.config(image=Image.loop_off_16px)
        else:
            self.loop_on_cut_state = True
            self.ui.button_play_cut_loop.config(image=Image.loop_on_16px)

    def _on_export_cuts(self) -> None:
        """
        Exports all the cuts and concatenates them
        """
        # Check if there is a file
        if not self.vlc_player.get_media():
            return
        # Check if there are cuts
        list_cuts = self.ui.table_cuts.get()
        list_cuts.pop(0)  # Remove the header
        if len(list_cuts) == 0:
            return

        self.master.configure(cursor="wait")

        # Create a folder to export all the cuts
        filename = os.path.basename(self.media_filename)
        filename = os.path.splitext(filename)[0]
        file_folder = os.path.dirname(self.media_filename)
        folder_export = os.path.abspath(os.path.join(file_folder, filename))
        os.makedirs(folder_export, exist_ok=True)
        # Export all the cuts
        n = len(list_cuts)
        progressbar = src.frames.Progressbar(self, "Exporting cuts", 0, n)
        list_files_exported = list()
        for i, (_, start, end, _) in enumerate(list_cuts):
            progressbar.step()
            filename_export = f"{self.media_filename.split('.')[0]}_{i:02d}.mp4"
            filename_export = f"{filename}_{i:02d}.mp4"
            file_export = os.path.join(folder_export, filename_export)
            list_files_exported.append(file_export)
            # Duration
            time_start = self.get_seconds(start)
            time_end = self.get_seconds(end)
            duration = time.strftime("%H:%M:%S", time.gmtime(time_end - time_start))
            cmd = f"ffmpeg -ss {start} -i {self.media_filename} -t {duration} -vcodec copy -acodec copy -y {file_export}"
            os.system(cmd)
        # Create a file with all the cuts
        file_list_exports = os.path.join(folder_export, "list_cuts.txt")
        output = os.path.join(folder_export, "output.mp4")
        with open(file_list_exports, "w") as fid:
            for file_export in list_files_exported:
                fid.write(f"file '{file_export}'\n")
        # Concatenate all the cuts
        progressbar.set(status="Concatenating cuts")
        progressbar.set_mode("indeterminate")
        cmd = f"ffmpeg -f concat -safe 0 -i {file_list_exports} -vcodec copy -acodec copy -y {output}"
        os.system(cmd)

        self.master.configure(cursor="arrow")
        print("Exported all the cuts")
        progressbar.set_mode("determinate")
        progressbar.set(n=100, n_max=100)
        progressbar.wait_ok()

    def _on_export_cuts_tags(self) -> None:
        # Check if there is a file
        if not self.vlc_player.get_media():
            return
        # Check if there are cuts
        list_cuts = self.ui.table_cuts.get()
        list_cuts.pop(0)  # Remove the header
        if len(list_cuts) == 0:
            return

        self.master.configure(cursor="wait")

        # Ask for tags to export
        tags = self.ui.table_cuts.choices_multiple[2]
        x = src.frames.ExportWindow(self, tags)
        x.wait_window()
        tags_export = x.get()

        tags_str = "-".join([tag for tag in tags_export if tags_export[tag]])

        # Create a folder to export all the cuts
        filename = os.path.basename(self.media_filename)
        filename = os.path.splitext(filename)[0]
        filename = f"{filename}_{tags_str}"
        file_folder = os.path.dirname(self.media_filename)
        folder_export = os.path.abspath(os.path.join(file_folder, filename))
        os.makedirs(folder_export, exist_ok=True)
        # Export all the cuts
        list_files_exported = list()
        for i, (_, start, end, tags) in enumerate(list_cuts):
            tags = tags.split(", ")


            # Check if at least one tag is in the list of tags to export
            if tags == [""]:  # Happens when there is no tag
                continue
            if not any(tags_export[t] for t in tags):
                continue

            filename_export = f"{self.media_filename.split('.')[0]}_{i:02d}.mp4"
            filename_export = f"{filename}_{i:02d}.mp4"
            file_export = os.path.join(folder_export, filename_export)
            list_files_exported.append(file_export)
            # Duration
            time_start = self.get_seconds(start)
            time_end = self.get_seconds(end)
            duration = time.strftime("%H:%M:%S", time.gmtime(time_end - time_start))
            cmd = f"ffmpeg -ss {start} -i {self.media_filename} -t {duration} -vcodec copy -acodec copy -y {file_export}"
            os.system(cmd)
        # Create a file with all the cuts
        file_list_exports = os.path.join(folder_export, "list_cuts.txt")
        output = os.path.join(folder_export, "output.mp4")
        with open(file_list_exports, "w") as fid:
            for file_export in list_files_exported:
                fid.write(f"file '{file_export}'\n")
        # Concatenate all the cuts
        cmd = f"ffmpeg -f concat -safe 0 -i {file_list_exports} -vcodec copy -acodec copy -y {output}"
        os.system(cmd)

        self.master.configure(cursor="arrow")
        print("Exported selected cuts")

    # Methods

    def save_project(self, filename:str) -> None:
        """
        Saves the project in a file.

        Args:
            filename (str): path where the file should be saved.
        """
        # Prepare data to save
        data = dict()
        data["version"] = pl.VERSION
        data["video_filename"] = self.media_filename
        data["tags"] = self.ui.table_cuts.choices_multiple[2]  # 2 is the index of the tags column
        data["cuts"] = list()
        # Get data to export
        cuts = self.ui.table_cuts.get()
        cuts.pop(0)  # Remove the header
        for _, start, stop, tags in cuts:
            data["cuts"].append(f"{start} - {stop} - {tags}")

        # Save the file
        with open(filename, "w") as fid:
            yaml.dump(data, fid, indent=2, sort_keys=False)

    def load_project(self, filename:str) -> None:
        """
        Loads the project from a file.

        Args:
            filename (str): path to the project file.
        """
        # Load the file
        with open(filename, "r") as fid:
            data = yaml.safe_load(fid)

        # Prepare the table
        self.ui.table_cuts.clear()

        # Set the video
        self.project_filename = filename
        self.load_media(data["video_filename"])
        # Set the cuts
        for cut in data["cuts"]:
            start, stop, tags = cut.split(" - ")
            self.ui.table_cuts.add_row(values=[start, stop, tags])

        if "version" in data:
            self.ui.table_cuts.choice_multiple_values_columns(2, list_choices=data["tags"])

    def load_media(self, filename:str) -> None:
        """
        Loads a media file.

        Args:
            filename (str): path to the media file.
        """

        # Update the title of the window
        pl.root.title(f"{pl.config['name']} - {os.path.basename(filename)}")
        # Load the media
        media = self.vlc_instance.media_new(filename)
        self.vlc_player.set_media(media)
        self.vlc_player.set_hwnd(self.ui.frame_player.winfo_id())
        self.vlc_player.play()
        self.vlc_player.pause()
        time.sleep(1)
        self.media_filename = filename
        self.media_length = self.vlc_player.get_length()
        self.vlc_player.play()
        self.run_loop_update_slider()

    def setup_bindings(self) -> None:
        """
        Setups the slider and table bindings.
        """
        self.ui.slider.bind("<<Changing>>", self._on_slider_changing)
        self.ui.slider.bind("<<Changed>>", self._on_slider_change)
        self.ui.slider.bind("<<IntervalSelected>>", self._on_slider_interval_selected)
        self.ui.table_cuts.bind("<<TableUpdated>>", self._on_table_update)
        self.ui.slider.set_state("enabled")

    def media_play(self, t:int=None) -> None:
        """
        Plays the media.

        Args:
            t: Time in seconds to start playing.
        """
        if t is not None:
            self.vlc_player.set_time(round(t * 1000))

        if not self.vlc_player.is_playing():
            self.vlc_player.play()
            # Start loop to update slider
            self.run_loop_update_slider()

    def media_pause(self) -> None:
        """
        Pauses the media.
        """
        self.vlc_player.pause()
        # Stop loop to update slider
        self.after_cancel(self.loop_slider_update_iid)
        self.loop_slider_update_iid = None

    def setup_vlc(self) -> None:
        self.vlc_instance = vlc.Instance()
        self.vlc_player = self.vlc_instance.media_player_new()

    def run_loop_update_slider(self) -> None:
        self.loop_slider_update_iid = self.after(self.loop_update_interval, self.loop_update_slider)

    def loop_update_slider(self) -> None:
        if self.loop_slider_update_iid is None:
            return

        percent = self.vlc_player.get_time() / self.media_length
        self.ui.slider.set(percent)
        self.ui.slider.update()

        self.run_loop_update_slider()

    def loop_on_cut(self) -> None:
        """
        Loops over the selected cut.
        """
        if self.loop_on_cut_iid is None:
            return None

        if self.loop_on_cut_state is False:
            self.after_cancel(self.loop_on_cut_iid)
            self.loop_on_cut_iid = None
            return None

        _, row = self.ui.table_cuts.get_selected_row()
        start = self.get_seconds(row[0])
        end = self.get_seconds(row[1])
        if self.vlc_player.get_time() >= end * 1000:
            self.vlc_player.set_time(round(start * 1000))

        self.loop_on_cut_iid = self.after(self.loop_update_interval, self.loop_on_cut)

    def update_all_intervals(self) -> None:
        """
        Updates all the intervals from the table of cuts.
        """

        self.ui.slider.clear_intervals()

        for _, start, end, _ in self.ui.table_cuts.get()[1:]:
            if start != "":
                start = self.time_to_percent(start)
            else:
                start = 0.0

            if end != "":
                end = self.time_to_percent(end)
            else:
                end = start

            self.ui.slider.add_interval(start, end)

    def update_interval(self, index:int) -> None:
        """
        Updates the interval at the given index.
        """

        list_cuts = self.ui.table_cuts.get()
        list_cuts.pop(0)  # Remove the header
        _, start, end = list_cuts[index]
        self.ui.slider.intervals[index].start = start
        self.ui.slider.intervals[index].stop = end
        self.ui.slider.intervals[index].update_line()

    def time_to_percent(self, t:str) -> float:
        """
        Converts a time string to a percentage.
        """
        return self.get_seconds(t) * 1000 / self.media_length

    def get_seconds(self, t:str) -> int:
        """
        Converts a time string to a number of seconds.
        """
        x = time.strptime(t, "%H:%M:%S")
        return datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()
