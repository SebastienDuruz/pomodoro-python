# ETML
# Author : Sébastien Duruz
# Date : 10.01.2021
# Description : The main page of the application

import sys
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
    break_counter = int(json_settings['clock']['short_break'])
    counter_minutes_str = json_settings['clock']['work_interval']
    tasks_counter = int(json_settings['clock']['tasks_counter'])
    current_tasks_counter = tasks_counter

    # The thread for clock timer related process (let us pause / stop timer any time)
    timer_thread = None

    # Objects required by different methods
    window = None
    app_notebook = None
    alarm_clock_tasks_counter_label = None
    alarm_clock_current_task_text = None
    alarm_clock_canvas = None
    alarm_clock_circle = None
    alarm_clock_text = None
    alarm_clock_start_button = None
    alarm_clock_pause_button = None
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
        MainPage.window.protocol("WM_DELETE_WINDOW", lambda: MainPage.on_closing())
        MainPage.app_notebook = ttk.Notebook(MainPage.window)
        MainPage.app_notebook.pack()
        MainPage.app_notebook.bind("<<NotebookTabChanged>>", MainPage.on_notebook_page_changed)

        # alarm clock notebook page
        alarm_clock_frame = Frame(MainPage.app_notebook, padx=25, pady=25)
        alarm_clock_frame.pack()
        MainPage.alarm_clock_tasks_counter_label = Label(alarm_clock_frame, text="Current session : 1 / " +
                                                                                 str(MainPage.tasks_counter))
        MainPage.alarm_clock_tasks_counter_label.pack(side=TOP)
        MainPage.alarm_clock_canvas = Canvas(alarm_clock_frame, width=300, height=300)
        MainPage.alarm_clock_current_task_text = MainPage.alarm_clock_canvas.create_text(150, 25,
                                                                                         font=('Arial', 24, 'bold'),
                                                                                         text="")
        MainPage.alarm_clock_circle = MainPage.alarm_clock_canvas.create_oval(50, 50, 250, 250, width=3)
        MainPage.alarm_clock_text = MainPage.alarm_clock_canvas.create_text(150, 150, font=('Arial', 30, 'bold'),
                                                                            text=MainPage.json_settings
                                                                            ['clock']['work_interval'] + ":00")
        MainPage.alarm_clock_canvas.pack()
        MainPage.alarm_clock_start_button = Button(alarm_clock_frame, text="Start", width=20,
                                                   command=MainPage.start_timer)
        MainPage.alarm_clock_pause_button = Button(alarm_clock_frame, text="Pause", width=20,
                                                   command=MainPage.pause_resume_timer)
        MainPage.alarm_clock_start_button.pack(side=LEFT)
        MainPage.alarm_clock_pause_button.pack(side=RIGHT)
        MainPage.alarm_clock_pause_button['state'] = "disabled"

        # alarm value notebook page
        alarm_values_frame = Frame(MainPage.app_notebook, pady=25, padx=25)
        alarm_values_frame.pack()

        # build the required elements
        short_break_label = Label(alarm_values_frame, text="Short Break", pady=10)
        work_interval_label = Label(alarm_values_frame, text="Work interval", pady=10)
        tasks_counter_label = Label(alarm_values_frame, text="Tasks", pady=10)
        MainPage.short_break_entry = Entry(alarm_values_frame, justify="center", width=10)
        MainPage.work_interval_entry = Entry(alarm_values_frame, justify="center", width=10)
        MainPage.tasks_counter_entry = Entry(alarm_values_frame, justify="center", width=10)
        update_values_button = Button(
            alarm_values_frame, text="Update", command=MainPage.validate_form_values, width=20
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
                                                   MainPage.tasks_counter_entry.get())

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

        # Start a timer
        if not MainPage.timer_is_running and not MainPage.timer_is_pause:

            # Notify the program that timer is currently running
            MainPage.timer_is_running = True

            # Switch state of the buttons
            MainPage.alarm_clock_pause_button['state'] = "normal"
            MainPage.alarm_clock_start_button.config(text="Stop")

            # Start the thread (The thread will be closed when application exit)
            MainPage.timer_thread = threading.Thread(target=MainPage.update_timer)
            MainPage.timer_thread.daemon = True
            MainPage.timer_thread.start()

        # Stop a running timer
        else:

            if messagebox.askokcancel("Stop timer", "Do you really want to stop ? The timer will be reset !"):
                MainPage.end_timer()

    @staticmethod
    def update_timer():
        """
        Update the timer with new values
        """

        # A task as to be run
        while int(MainPage.current_tasks_counter) > 0:

            # 0 ==> Work || 1 ==> Break
            for i in range(2):

                # Work period
                if i == 0:

                    MainPage.alarm_clock_tasks_counter_label.config(text="Current session : " +
                                                                         str(int(MainPage.tasks_counter) + 1 -
                                                                             int(MainPage.current_tasks_counter)) +
                                                                         " / " + str(MainPage.tasks_counter))

                    # Calculate the full time in second of the current running timer
                    MainPage.remaining_time_seconds = int(MainPage.json_settings['clock']['work_interval']) * 60

                    # Modify the elements with correct colors
                    MainPage.alarm_clock_canvas.itemconfigure(MainPage.alarm_clock_circle, outline="red")
                    MainPage.alarm_clock_canvas.itemconfigure(MainPage.alarm_clock_current_task_text, text="WORK")

                # Break period
                elif i == 1:

                    # Don't trigger when last tasks running (no break needed)
                    if MainPage.current_tasks_counter != 1:

                        # Calculate the full time in second of the current running timer
                        MainPage.remaining_time_seconds = int(MainPage.json_settings['clock']['short_break']) * 60

                        # Modify the elements with correct colors
                        MainPage.alarm_clock_canvas.itemconfigure(MainPage.alarm_clock_circle, outline="green")
                        MainPage.alarm_clock_canvas.itemconfigure(MainPage.alarm_clock_current_task_text, text="BREAK")

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
                    time.sleep(0.001)

            # Finish a full tasks (Work + Break)
            MainPage.current_tasks_counter -= 1

        # Triggered at the end of execution
        MainPage.end_timer()

    @staticmethod
    def pause_resume_timer():
        """
        Pause or resume the running timer
        :return:
        """

        # Pause the timer
        if not MainPage.timer_is_pause:

            MainPage.alarm_clock_pause_button.config(text="Resume")
            MainPage.timer_is_pause = True
            MainPage.timer_is_running = False

        # Resume the timer
        else:

            MainPage.alarm_clock_pause_button.config(text="Pause")
            MainPage.timer_is_pause = False
            MainPage.timer_is_running = True

    @staticmethod
    def end_timer():
        """
        The timer ended, clear the required values
        """

        # Set the timer to default values
        MainPage.timer_is_running = False
        MainPage.timer_is_pause = False
        MainPage.timer_thread = None

        # Print message to user
        messagebox.showinfo("Timer end", "Work Finished !")

        # Prepare the timer for a new start
        MainPage.get_settings()
        MainPage.update_page_info()
        MainPage.reset_page_graphics()

    @staticmethod
    def get_settings():
        """
        Get the settings from json settings file and update the current minutes string
        """

        # Update the settings fetched from json file
        MainPage.json_settings = SettingsReader().read_settings()

        # Only if timer is not running or paused
        if not MainPage.timer_is_running and not MainPage.timer_is_pause:

            # Update the required values
            MainPage.counter_minutes_str = int(MainPage.json_settings['clock']['work_interval'])
            MainPage.counter_seconds_str = 0
            MainPage.tasks_counter = int(MainPage.json_settings['clock']['tasks_counter'])
            MainPage.current_tasks_counter = MainPage.tasks_counter

    @staticmethod
    def update_page_info():
        """
        Update the information of the notebook pages
        """

        # Clock timer page, update the required elements (if timer not started or paused)
        if str(MainPage.app_notebook.index(MainPage.app_notebook.select())) == "0":
            if not MainPage.timer_is_running and not MainPage.timer_is_pause:
                MainPage.alarm_clock_canvas.itemconfigure(MainPage.alarm_clock_text,
                                                          text='{:02d}:{:02d}'.format(
                                                                int(MainPage.counter_minutes_str),
                                                                int(0)))
                MainPage.alarm_clock_tasks_counter_label.config(text="Current session : 0 / " +
                                                                     str(MainPage.tasks_counter))

    @staticmethod
    def reset_page_graphics():
        """
        Reset the default graphics of the timer
        """

        MainPage.alarm_clock_canvas.itemconfigure(MainPage.alarm_clock_circle, outline="black")
        MainPage.alarm_clock_canvas.itemconfigure(MainPage.alarm_clock_current_task_text, text="")
        MainPage.alarm_clock_start_button.config(text="Start")
        MainPage.alarm_clock_pause_button['state'] = "disabled"

    @staticmethod
    def on_notebook_page_changed(event):
        """
        On notebook page change, Update page with new json values
        """

        # Get the settings
        MainPage.get_settings()

        # Update the specific page information
        MainPage.update_page_info()

    @staticmethod
    def on_closing():
        """
        Occurred when the window is closed, ask confirmation to user
        """

        if MainPage.timer_is_running or MainPage.timer_is_pause:
            if messagebox.askokcancel("Quit", "Do you really want to quit ?\nClock is running !"):
                sys.exit()

        else:
            sys.exit()
