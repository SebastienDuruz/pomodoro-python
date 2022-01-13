# Author : Sébastien Duruz
# Date : 10.01.2021
# Description : The main page of the application

import os.path
import sys
import time
import threading
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from Models.settings_reader import SettingsReader
from Models.audio_player import AudioPlayer


class MainPage:
    """
    Class MainPage
    """

    def __init__(self):
        """
        Class Constructor
        """

        # Content of the settings file
        self.json_settings = SettingsReader().read_settings()

        # Timer relative information
        self.timer_is_running = False
        self.timer_is_pause = False
        self.remaining_time_seconds = None
        self.break_counter = int(self.json_settings['clock']['short_break'])
        self.counter_minutes_str = self.json_settings['clock']['work_interval']
        self.tasks_counter = int(self.json_settings['clock']['tasks_counter'])
        self.current_tasks_counter = self.tasks_counter

        # File paths
        self.application_dir_path = os.path.dirname(os.path.realpath(__file__))
        self.work_sound_path = os.path.join(self.application_dir_path + '/../Resources/work_sound.wav')

        # The thread for clock timer related process (let us pause / stop timer any time)
        self.timer_thread = None

        # Objects required by different methods
        self.window = None
        self.app_notebook = None
        self.alarm_clock_tasks_counter_label = None
        self.alarm_clock_current_task_text = None
        self.alarm_clock_canvas = None
        self.alarm_clock_circle = None
        self.alarm_clock_text = None
        self.alarm_clock_start_button = None
        self.alarm_clock_pause_button = None
        self.short_break_entry = None
        self.work_interval_entry = None
        self.tasks_counter_entry = None

        self.build_pages()

    def build_pages(self):
        """
        Build the main page with required elements
        """

        # Main Window
        self.window = Tk()
        self.window.title("Pomodoro Timer")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", lambda: self.on_closing())
        self.app_notebook = ttk.Notebook(self.window)
        self.app_notebook.pack()
        self.app_notebook.bind("<<NotebookTabChanged>>", self.on_notebook_page_changed)

        # alarm clock notebook page
        alarm_clock_frame = Frame(self.app_notebook, padx=25, pady=25)
        alarm_clock_frame.pack()
        self.alarm_clock_tasks_counter_label = Label(alarm_clock_frame, text="Current session : 1 / " +
                                                                             str(self.tasks_counter))
        self.alarm_clock_tasks_counter_label.pack(side=TOP)
        self.alarm_clock_canvas = Canvas(alarm_clock_frame, width=300, height=300)
        self.alarm_clock_current_task_text = self.alarm_clock_canvas.create_text(150, 25,
                                                                                 font=('Arial', 24, 'bold'),
                                                                                 text="")
        self.alarm_clock_circle = self.alarm_clock_canvas.create_oval(50, 50, 250, 250, width=3)
        self.alarm_clock_text = self.alarm_clock_canvas.create_text(150, 150, font=('Arial', 30, 'bold'),
                                                                    text=self.json_settings['clock']
                                                                    ['work_interval'] + ":00")
        self.alarm_clock_canvas.pack()
        self.alarm_clock_start_button = Button(alarm_clock_frame, text="Start", width=20, command=self.start_timer)
        self.alarm_clock_pause_button = Button(alarm_clock_frame, text="Pause", width=20,
                                               command=self.pause_resume_timer)
        self.alarm_clock_start_button.pack(side=LEFT)
        self.alarm_clock_pause_button.pack(side=RIGHT)
        self.alarm_clock_pause_button['state'] = "disabled"

        # alarm value notebook page
        alarm_values_frame = Frame(self.app_notebook, pady=25, padx=25)
        alarm_values_frame.pack()

        # build the required elements
        short_break_label = Label(alarm_values_frame, text="Short Break", pady=10)
        work_interval_label = Label(alarm_values_frame, text="Work interval", pady=10)
        tasks_counter_label = Label(alarm_values_frame, text="Tasks", pady=10)
        self.short_break_entry = Entry(alarm_values_frame, justify="center", width=10)
        self.work_interval_entry = Entry(alarm_values_frame, justify="center", width=10)
        self.tasks_counter_entry = Entry(alarm_values_frame, justify="center", width=10)
        update_values_button = Button(
            alarm_values_frame, text="Update", command=self.validate_form_values, width=20
        )

        # Update the values with current settings
        self.short_break_entry.insert(0, self.json_settings['clock']['short_break'])
        self.work_interval_entry.insert(0, self.json_settings['clock']['work_interval'])
        self.tasks_counter_entry.insert(0, self.json_settings['clock']['tasks_counter'])

        # pack the elements
        short_break_label.pack()
        self.short_break_entry.pack()
        work_interval_label.pack()
        self.work_interval_entry.pack()
        tasks_counter_label.pack()
        self.tasks_counter_entry.pack()
        update_values_button.pack(side=BOTTOM)

        # Add the notebook pages to the application
        self.app_notebook.add(alarm_clock_frame, text="Clock")
        self.app_notebook.add(alarm_values_frame, text="Settings")

        # Main loop
        self.window.mainloop()

    def validate_form_values(self):
        """
        Validate the values entered by user
        """

        try:

            # Check if values are int type and at least 1
            if int(self.short_break_entry.get()) < 1 \
                    or int(self.work_interval_entry.get()) < 1 or int(self.short_break_entry.get()) < 1:
                raise ValueError("The value should be bigger or equal to 1.")

            # Update the settings with validated values
            SettingsReader().modify_clock_settings(self.short_break_entry.get(),
                                                   self.work_interval_entry.get(),
                                                   self.tasks_counter_entry.get())

            # Display confirmation message to user
            messagebox.showinfo("Validation", "The new values as been saved !")

        except ValueError:

            # Display error message to user
            messagebox.showerror("Validation", "An error occurred, please check your entries !"
                                               "\n(Only positive numbers allowed)")

    def start_timer(self):
        """
        Start a new timer with given settings
        """

        # Start a timer
        if not self.timer_is_running and not self.timer_is_pause:

            # Notify the program that timer is currently running
            self.timer_is_running = True

            # Switch state of the buttons
            self.alarm_clock_pause_button['state'] = "normal"
            self.alarm_clock_start_button.config(text="Stop")

            # Start the thread (The thread will be closed when application exit)
            self.timer_thread = threading.Thread(target=self.update_timer)
            self.timer_thread.daemon = True
            self.timer_thread.start()

            AudioPlayer(self.work_sound_path).play_audio()

        # Stop a running timer
        else:

            if messagebox.askokcancel("Stop timer", "Do you really want to stop ? The timer will be reset !"):
                self.end_timer()

    def update_timer(self):
        """
        Update the timer with new values
        """

        # A task as to be run
        while int(self.current_tasks_counter) > 0:

            # 0 ==> Work || 1 ==> Break
            for i in range(2):

                # Work period
                if i == 0:

                    self.alarm_clock_tasks_counter_label.config(text="Current session : " +
                                                                     str(int(self.tasks_counter) + 1 -
                                                                         int(self.current_tasks_counter)) +
                                                                     " / " + str(self.tasks_counter))

                    # Calculate the full time in second of the current running timer
                    self.remaining_time_seconds = int(self.json_settings['clock']['work_interval']) * 60

                    # Modify the elements with correct colors
                    self.alarm_clock_canvas.itemconfigure(self.alarm_clock_circle, outline="red")
                    self.alarm_clock_canvas.itemconfigure(self.alarm_clock_current_task_text, text="WORK")

                # Break period
                elif i == 1:

                    # Don't trigger when last tasks running (no break needed)
                    if self.current_tasks_counter != 1:

                        # Calculate the full time in second of the current running timer
                        self.remaining_time_seconds = int(self.json_settings['clock']['short_break']) * 60

                        # Modify the elements with correct colors
                        self.alarm_clock_canvas.itemconfigure(self.alarm_clock_circle, outline="green")
                        self.alarm_clock_canvas.itemconfigure(self.alarm_clock_current_task_text, text="BREAK")

                # Timer is running
                while self.remaining_time_seconds > -1:

                    if self.timer_is_running:
                        # Split the seconds to mins and secs
                        mins, secs = divmod(self.remaining_time_seconds, 60)

                        # remove 1 sec to total
                        self.remaining_time_seconds -= 1

                        # Update the output text value
                        self.alarm_clock_canvas.itemconfigure(self.alarm_clock_text,
                                                              text='{:02d}:{:02d}'.format(
                                                                      int(mins),
                                                                      int(secs)))
                    time.sleep(1)

                # Play a sound between each period
                AudioPlayer(self.work_sound_path).play_audio()

            # Finish a full tasks (Work + Break)
            self.current_tasks_counter -= 1

        # Triggered at the end of execution
        self.end_timer()

    def pause_resume_timer(self):
        """
        Pause or resume the running timer
        """

        # Pause the timer
        if not self.timer_is_pause:

            self.alarm_clock_pause_button.config(text="Resume")
            self.timer_is_pause = True
            self.timer_is_running = False

        # Resume the timer
        else:

            self.alarm_clock_pause_button.config(text="Pause")
            self.timer_is_pause = False
            self.timer_is_running = True

    def end_timer(self):
        """
        The timer ended, clear the required values
        """

        # Set the timer to default values
        self.timer_is_running = False
        self.timer_is_pause = False
        self.timer_thread = None

        # Print message to user
        messagebox.showinfo("Timer end", "Work Finished !")

        # Prepare the timer for a new start
        self.get_settings()
        self.update_page_info()
        self.reset_page_graphics()

    def get_settings(self):
        """
        Get the settings from json settings file and update the current minutes string
        """

        # Update the settings fetched from json file
        self.json_settings = SettingsReader().read_settings()

        # Only if timer is not running or paused
        if not self.timer_is_running and not self.timer_is_pause:

            # Update the required values
            self.counter_minutes_str = int(self.json_settings['clock']['work_interval'])
            self.tasks_counter = int(self.json_settings['clock']['tasks_counter'])
            self.current_tasks_counter = self.tasks_counter

    def update_page_info(self):
        """
        Update the information of the notebook pages
        """

        # Clock timer page, update the required elements (if timer not started or paused)
        if str(self.app_notebook.index(self.app_notebook.select())) == "0":
            if not self.timer_is_running and not self.timer_is_pause:
                self.alarm_clock_canvas.itemconfigure(self.alarm_clock_text,
                                                      text='{:02d}:{:02d}'.format(
                                                                int(self.counter_minutes_str),
                                                                int(0)))
                self.alarm_clock_tasks_counter_label.config(text="Current session : 0 / " +
                                                                 str(self.tasks_counter))

    def reset_page_graphics(self):
        """
        Reset the default graphics of the timer
        """

        self.alarm_clock_canvas.itemconfigure(self.alarm_clock_circle, outline="black")
        self.alarm_clock_canvas.itemconfigure(self.alarm_clock_current_task_text, text="")
        self.alarm_clock_start_button.config(text="Start")
        self.alarm_clock_pause_button['state'] = "disabled"

    def on_notebook_page_changed(self, event):
        """
        On notebook page change, Update page with new json values
        """

        # Get the settings
        self.get_settings()

        # Update the specific page information
        self.update_page_info()

    def on_closing(self):
        """
        Occurred when the window is closed, ask confirmation to user
        """

        if self.timer_is_running or self.timer_is_pause:
            if messagebox.askokcancel("Quit", "Do you really want to quit ?\nClock is running !"):
                sys.exit()

        else:
            sys.exit()
