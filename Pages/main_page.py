# ETML
# Author : Sébastien Duruz
# Date : 10.01.2021
# Description : The main page of the application
import time
import threading
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from Models.settings_reader import SettingsReader


class MainPage:
    """
    Class MainPage
    """

    # Content of the settings file
    json_settings = SettingsReader().read_settings()

    # Timer relative information
    timer_is_running = False
    timer_is_pause = False
    remaining_time_seconds = None
    counter_minutes_str = json_settings['clock']['work_interval']
    counter_seconds_str = "00"

    # The thread for clock timer related process (let us pause / stop timer any time)
    timer_thread = None

    # Objects required by different methods
    window = None
    app_notebook = None
    alarm_clock_recap = None
    alarm_clock_canvas = None
    alarm_clock_circle = None
    alarm_clock_text = None
    short_break_entry = None
    work_interval_entry = None
    tasks_counter_entry = None

    def __init__(self):
        """
        Class Constructor
        """

        MainPage.build_pages()

    @staticmethod
    def build_pages():
        """
        Build the main page with required elements
        """

        # Main Window
        MainPage.window = Tk()
        MainPage.window.title("Pomodoro Timer")
        MainPage.window.resizable(False, False)
        MainPage.app_notebook = ttk.Notebook(MainPage.window)
        MainPage.app_notebook.pack()
        MainPage.app_notebook.bind("<<NotebookTabChanged>>", MainPage.on_notebook_page_changed)

        # alarm clock notebook page
        alarm_clock_frame = Frame(MainPage.app_notebook, padx=25, pady=25)
        alarm_clock_frame.grid()
        MainPage.alarm_clock_recap = Label(alarm_clock_frame, text="Current session : 1/5")
        MainPage.alarm_clock_recap.pack(side=TOP)
        MainPage.alarm_clock_canvas = Canvas(alarm_clock_frame, width=300, height=300)
        MainPage.alarm_clock_circle = MainPage.alarm_clock_canvas.create_oval(50, 50, 250, 250)
        MainPage.alarm_clock_text = MainPage.alarm_clock_canvas.create_text(150, 150, font=('Arial', 30, 'bold'),
                                                                            text=MainPage.json_settings
                                                                            ['clock']['work_interval'] + ":00")
        MainPage.alarm_clock_canvas.pack()
        alarm_clock_start_button = Button(alarm_clock_frame, text="Start", width=20, command=MainPage.start_timer)
        alarm_clock_stop_button = Button(alarm_clock_frame, text="Stop", width=20)
        alarm_clock_start_button.pack(side=LEFT)
        alarm_clock_stop_button.pack(side=RIGHT)

        # alarm value notebook page
        alarm_values_frame = Frame(MainPage.app_notebook)
        alarm_values_frame.grid()

        # build the required elements
        short_break_label = Label(alarm_values_frame, text="Short Break")
        work_interval_label = Label(alarm_values_frame, text="Work interval")
        tasks_counter_label = Label(alarm_values_frame, text="Tasks")
        MainPage.short_break_entry = Entry(alarm_values_frame, justify="center")
        MainPage.work_interval_entry = Entry(alarm_values_frame, justify="center")
        MainPage.tasks_counter_entry = Entry(alarm_values_frame, justify="center")
        update_values_button = Button(
            alarm_values_frame, text="Update", command=MainPage.validate_form_values
        )

        # Update the values with current settings
        MainPage.short_break_entry.insert(0, MainPage.json_settings['clock']['short_break'])
        MainPage.work_interval_entry.insert(0, MainPage.json_settings['clock']['work_interval'])
        MainPage.tasks_counter_entry.insert(0, MainPage.json_settings['clock']['tasks_counter'])

        # pack the elements
        short_break_label.pack()
        MainPage.short_break_entry.pack()
        work_interval_label.pack()
        MainPage.work_interval_entry.pack()
        tasks_counter_label.pack()
        MainPage.tasks_counter_entry.pack()
        update_values_button.pack(side=BOTTOM)

        # Add the notebook pages to the application
        MainPage.app_notebook.add(alarm_clock_frame, text="Clock")
        MainPage.app_notebook.add(alarm_values_frame, text="Settings")

        # Main loop
        MainPage.window.mainloop()

    @staticmethod
    def validate_form_values():
        """
        Validate the values entered by user
        """

        try:

            # Check if values are int type and at least 1
            if int(MainPage.short_break_entry.get()) < 1 \
                    or int(MainPage.work_interval_entry.get()) < 1 or int(MainPage.short_break_entry.get()) < 1:
                raise ValueError("The value should be bigger or equal to 1.")

            # Update the settings with validated values
            SettingsReader().modify_clock_settings(MainPage.short_break_entry.get(),
                                                   MainPage.work_interval_entry.get(),
                                                   MainPage.short_break_entry.get())

            # Display confirmation message to user
            messagebox.showinfo("Validation", "The new values as been saved !")

        except ValueError:

            # Display error message to user
            messagebox.showerror("Validation", "An error occurred, please check your entries !"
                                               "\n(Only positive numbers allowed)")

    @staticmethod
    def start_timer():
        """
        Start a new timer with given settings
        """
        if not MainPage.timer_is_running:

            # Notify the program that timer is currently running
            MainPage.timer_is_running = True

            # Calculate the full time in second of the current
            MainPage.remaining_time_seconds = int(MainPage.json_settings['clock']['work_interval']) * 60

            # Start the thread
            MainPage.timer_thread = threading.Timer(1.0, MainPage.update_timer)
            MainPage.timer_thread.start()

    @staticmethod
    def update_timer():
        """
        Update the timer with new values
        """

        # Timer is running
        while MainPage.remaining_time_seconds > -1:
            if MainPage.timer_is_running:

                # Split the seconds to mins and secs
                mins, secs = divmod(MainPage.remaining_time_seconds, 60)

                # remove 1 sec to total
                MainPage.remaining_time_seconds -= 1

                # Update the output text value
                MainPage.alarm_clock_canvas.itemconfigure(MainPage.alarm_clock_text,
                                                          text='{:02d}:{:02d}'.format(
                                                              int(mins),
                                                              int(secs)))

                time.sleep(1)

        # Triggered at the end of execution
        MainPage.end_timer()

    @staticmethod
    def end_timer():
        """
        The timer ended, clear the required values
        """

        MainPage.timer_is_running = False
        MainPage.timer_thread = None

    @staticmethod
    def get_settings():
        """
        Get the settings from json settings file and update the current minutes string
        """

        # Update the settings fetched from json file
        MainPage.json_settings = SettingsReader().read_settings()

        # Update the required values
        MainPage.counter_minutes_str = MainPage.json_settings['clock']['work_interval']
        MainPage.counter_seconds_str = 0

    @staticmethod
    def update_page_info():
        """
        Update the information of the notebook pages
        """

        # Clock timer page, update the required elements (if timer not started)
        if str(MainPage.app_notebook.index(MainPage.app_notebook.select())) == "0":
            if not MainPage.timer_is_running and not MainPage.timer_is_pause:
                MainPage.alarm_clock_canvas.itemconfigure(MainPage.alarm_clock_text,
                                                          text='{:02d}:{:02d}'.format(
                                                                int(MainPage.counter_minutes_str),
                                                                int(MainPage.counter_seconds_str)))

    @staticmethod
    def on_notebook_page_changed(event):
        """
        On notebook page change, Update page with new json values
        """

        # Get the settings
        MainPage.get_settings()

        # Update the specific page information
        MainPage.update_page_info()
