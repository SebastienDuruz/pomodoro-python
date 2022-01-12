# ETML
# Author : Sébastien Duruz
# Date : 10.01.2021
# Description : The main page of the application

from tkinter import *
from tkinter import ttk
from Models.settings_reader import SettingsReader


class MainPage:
    """
    Class MainPage
    """

    # Content of the settings file
    json_settings = SettingsReader().read_settings()

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
        window = Tk()
        window.title("Pomodoro Timer")
        window.configure()
        app_notebook = ttk.Notebook(window)
        app_notebook.pack()

        # alarm clock notebook page
        alarm_clock_frame = Frame(app_notebook)
        alarm_clock_frame.grid()
        alarm_clock_canvas = Canvas(alarm_clock_frame, width=300, height=300)
        alarm_clock_canvas.create_oval(50, 50, 250, 250)
        alarm_clock_canvas.create_text(150, 150, font=('Arial', 30, 'bold'),
                                       text=MainPage.json_settings['clock']['work_interval'] + ":00")
        alarm_clock_canvas.pack()
        alarm_clock_start_button = Button(text="Start", width=20)
        alarm_clock_stop_button = Button(text="Stop", width=20)

        alarm_clock_start_button.pack(side=LEFT)
        alarm_clock_stop_button.pack(side=RIGHT)

        # alarm value notebook page
        alarm_values_frame = Frame(app_notebook)
        alarm_values_frame.grid()

        # build the required elements
        short_break_label = Label(alarm_values_frame, text="Short Break")
        work_interval_label = Label(alarm_values_frame, text="Work interval")
        tasks_counter_label = Label(alarm_values_frame, text="Tasks")
        short_break_entry = Entry(alarm_values_frame, justify="center")
        work_interval_entry = Entry(alarm_values_frame, justify="center")
        tasks_counter_entry = Entry(alarm_values_frame, justify="center")
        update_values_button = Button(
            alarm_values_frame, text="Update", command=MainPage.validate_form_values
        )

        # Update the values with current settings
        short_break_entry.insert(0, MainPage.json_settings['clock']['short_break'])
        work_interval_entry.insert(0, MainPage.json_settings['clock']['work_interval'])
        tasks_counter_entry.insert(0, MainPage.json_settings['clock']['tasks_counter'])

        # pack the elements
        short_break_label.pack()
        short_break_entry.pack()
        work_interval_label.pack()
        work_interval_entry.pack()
        tasks_counter_label.pack()
        tasks_counter_entry.pack()
        update_values_button.pack()

        # Add the notebook pages to the application
        app_notebook.add(alarm_clock_frame, text="Clock")
        app_notebook.add(alarm_values_frame, text="Clock Settings")

        # Main loop
        window.mainloop()

    def validate_form_values(self):
        """
        Validate the values entered by user
        """

        pass
