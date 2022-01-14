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
        self.__timer_is_running = False
        self.__timer_is_pause = False
        self.__total_time_seconds_task = None
        self.__remaining_time_seconds = None
        self.__break_counter = int(self.json_settings['clock']['short_break'])
        self.__counter_minutes_str = self.json_settings['clock']['work_interval']
        self.__tasks_counter = int(self.json_settings['clock']['tasks_counter'])
        self.__current_tasks_counter = self.__tasks_counter
        self.__last_clock_state_color = 'black'

        # File paths
        self.__application_dir_path = os.path.dirname(os.path.realpath(__file__))
        self.__work_sound_path = os.path.join(self.__application_dir_path + '/../Resources/work_sound.wav')

        # The thread for clock timer related process (let us pause / stop timer any time)
        self.__timer_thread = None

        # Objects required by different methods
        self.__window = None
        self.__app_notebook = None
        self.__alarm_clock_tasks_counter_label = None
        self.__alarm_clock_current_task_text = None
        self.__alarm_clock_canvas = None
        self.__alarm_clock_arc = None
        self.__alarm_clock_text = None
        self.__alarm_clock_start_button = None
        self.__alarm_clock_pause_button = None
        self.__short_break_entry = None
        self.__work_interval_entry = None
        self.__tasks_counter_entry = None

        self.__build_pages()

    def __build_pages(self):
        """
        Build the main page with required elements
        """

        # Main Window
        self.__window = Tk()
        self.__window.title("Pomodoro Timer")
        self.__window.resizable(False, False)
        self.__window.protocol("WM_DELETE_WINDOW", lambda: self.__on_closing())
        self.__app_notebook = ttk.Notebook(self.__window)
        self.__app_notebook.pack()
        self.__app_notebook.bind("<<NotebookTabChanged>>", self.__on_notebook_page_changed)

        # alarm clock notebook page
        alarm_clock_frame = Frame(self.__app_notebook, padx=25, pady=25)
        alarm_clock_frame.pack()
        self.__alarm_clock_tasks_counter_label = Label(alarm_clock_frame, text="Current session : 1 / " +
                                                                               str(self.__tasks_counter))
        self.__alarm_clock_tasks_counter_label.pack(side=TOP)
        self.__alarm_clock_canvas = Canvas(alarm_clock_frame, width=300, height=300)
        self.__alarm_clock_current_task_text = self.__alarm_clock_canvas.create_text(150, 35,
                                                                                     font=('Arial', 24, 'bold'),
                                                                                     text="")
        self.__alarm_clock_arc = self.__alarm_clock_canvas.create_arc(50, 70, 250, 270, start=90, extent=359.99,
                                                                      style=ARC, width=2, outline="black")
        self.__alarm_clock_text = self.__alarm_clock_canvas.create_text(150, 170, font=('Arial', 36, 'bold'),
                                                                        text=self.json_settings['clock']
                                                                        ['work_interval'] + ":00")
        self.__alarm_clock_canvas.pack()
        self.__alarm_clock_start_button = Button(alarm_clock_frame, text="Start", width=20, command=self.__start_timer)
        self.__alarm_clock_pause_button = Button(alarm_clock_frame, text="Pause", width=20,
                                                 command=self.__pause_resume_timer)
        self.__alarm_clock_start_button.pack(side=LEFT)
        self.__alarm_clock_pause_button.pack(side=RIGHT)
        self.__alarm_clock_pause_button['state'] = "disabled"

        # alarm value notebook page
        alarm_values_frame = Frame(self.__app_notebook, pady=25, padx=25)
        alarm_values_frame.pack()

        # build the required elements
        short_break_label = Label(alarm_values_frame, text="Short Break", pady=10)
        work_interval_label = Label(alarm_values_frame, text="Work interval", pady=10)
        tasks_counter_label = Label(alarm_values_frame, text="Tasks", pady=10)
        self.__short_break_entry = Entry(alarm_values_frame, justify="center", width=10)
        self.__work_interval_entry = Entry(alarm_values_frame, justify="center", width=10)
        self.__tasks_counter_entry = Entry(alarm_values_frame, justify="center", width=10)
        update_values_button = Button(
            alarm_values_frame, text="Update", command=self.__validate_form_values, width=20
        )

        # Update the values with current settings
        self.__short_break_entry.insert(0, self.json_settings['clock']['short_break'])
        self.__work_interval_entry.insert(0, self.json_settings['clock']['work_interval'])
        self.__tasks_counter_entry.insert(0, self.json_settings['clock']['tasks_counter'])

        # pack the elements
        short_break_label.pack()
        self.__short_break_entry.pack()
        work_interval_label.pack()
        self.__work_interval_entry.pack()
        tasks_counter_label.pack()
        self.__tasks_counter_entry.pack()
        update_values_button.pack(side=BOTTOM)

        # Add the notebook pages to the application
        self.__app_notebook.add(alarm_clock_frame, text="Clock")
        self.__app_notebook.add(alarm_values_frame, text="Settings")

        # Main loop
        self.__window.mainloop()

    def __validate_form_values(self):
        """
        Validate the values entered by user
        """

        try:

            # Check if values are int type and at least 1
            if int(self.__short_break_entry.get()) < 1 \
                    or int(self.__work_interval_entry.get()) < 1 or int(self.__short_break_entry.get()) < 1:
                raise ValueError("The value should be bigger or equal to 1.")

            # Update the settings with validated values
            SettingsReader().modify_clock_settings(self.__short_break_entry.get(),
                                                   self.__work_interval_entry.get(),
                                                   self.__tasks_counter_entry.get())

            # Display confirmation message to user
            messagebox.showinfo("Validation", "The new values as been saved !")

        except ValueError:

            # Display error message to user
            messagebox.showerror("Validation", "An error occurred, please check your entries !"
                                               "\n(Only positive numbers allowed)")

    def __start_timer(self):
        """
        Start a new timer with given settings
        """

        # Start a timer
        if not self.__timer_is_running and not self.__timer_is_pause:

            # Notify the program that timer is currently running
            self.__timer_is_running = True

            # Switch state of the buttons
            self.__alarm_clock_pause_button['state'] = "normal"
            self.__alarm_clock_start_button.config(text="Stop")

            # Start the thread (The thread will be closed when application exit)
            self.__timer_thread = threading.Thread(target=self.__update_timer)
            self.__timer_thread.daemon = True
            self.__timer_thread.start()

            AudioPlayer(self.__work_sound_path).play_audio()

        # Stop a running timer
        else:

            if messagebox.askokcancel("Stop timer", "Do you really want to stop ? The timer will be reset !"):
                self.__end_timer()

    def __update_timer(self):
        """
        Update the timer with new values
        """

        # A task as to be run
        while int(self.__current_tasks_counter) > 0:

            # 0 ==> Work || 1 ==> Break
            for i in range(2):

                # Work period
                if i == 0:

                    self.__alarm_clock_tasks_counter_label.config(text="Current session : " +
                                                                       str(int(self.__tasks_counter) + 1 -
                                                                           int(self.__current_tasks_counter)) +
                                                                       " / " + str(self.__tasks_counter))

                    # Calculate the full time in second of the current running timer
                    self.__remaining_time_seconds = int(self.json_settings['clock']['work_interval']) * 60

                    # Store it for animation calculation
                    self.__total_time_seconds_task = self.__remaining_time_seconds

                    # Modify the elements with correct colors
                    self.__alarm_clock_canvas.itemconfigure(self.__alarm_clock_arc, outline="red")
                    self.__alarm_clock_canvas.itemconfigure(self.__alarm_clock_current_task_text, text="WORK")

                # Break period
                elif i == 1:

                    # Don't trigger when last tasks running (no break needed)
                    if self.__current_tasks_counter != 1:

                        # Calculate the full time in second of the current running timer
                        self.__remaining_time_seconds = int(self.json_settings['clock']['short_break']) * 60

                        # Store it for animation calculation
                        self.__total_time_seconds_task = self.__remaining_time_seconds

                        # Modify the elements with correct colors
                        self.__alarm_clock_canvas.itemconfigure(self.__alarm_clock_arc, outline="green")
                        self.__alarm_clock_canvas.itemconfigure(self.__alarm_clock_current_task_text, text="BREAK")

                # Remains time to timer
                while self.__remaining_time_seconds > -1:

                    # Timer is running
                    if self.__timer_is_running:

                        # Split the seconds to mins and secs
                        mins, secs = divmod(self.__remaining_time_seconds, 60)

                        self.__alarm_clock_canvas.itemconfigure(self.__alarm_clock_arc, extent=self.__calculate_step())

                        # Update the output text value
                        self.__alarm_clock_canvas.itemconfigure(self.__alarm_clock_text,
                                                                text='{:02d}:{:02d}'.format(
                                                                      int(mins),
                                                                      int(secs)))

                        # remove 1 sec to total
                        self.__remaining_time_seconds -= 1

                    # The timer as been stopped : finish the execution of the thread
                    elif not self.__timer_is_running and not self.__timer_is_pause:
                        return

                    # Wait 1 sec before next cycle
                    time.sleep(1)

                # Play a sound between each period
                AudioPlayer(self.__work_sound_path).play_audio()

            # Finish a full tasks (Work + Break)
            self.__current_tasks_counter -= 1

        # Triggered at the end of execution
        self.__end_timer()

    def __pause_resume_timer(self):
        """
        Pause or resume the running timer
        """

        # Pause the timer
        if not self.__timer_is_pause:

            self.__last_clock_state_color = self.__alarm_clock_canvas.itemcget(self.__alarm_clock_arc, 'outline')
            self.__alarm_clock_pause_button.config(text="Resume")
            self.__alarm_clock_canvas.itemconfigure(self.__alarm_clock_arc, outline="orange")
            self.__timer_is_pause = True
            self.__timer_is_running = False

        # Resume the timer
        else:

            self.__alarm_clock_canvas.itemconfigure(self.__alarm_clock_arc, outline=self.__last_clock_state_color)
            self.__alarm_clock_pause_button.config(text="Pause")
            self.__timer_is_pause = False
            self.__timer_is_running = True

    def __end_timer(self):
        """
        The timer ended, clear the required values
        """

        # Set the timer to default values
        self.__timer_is_running = False
        self.__timer_is_pause = False

        # Print message to user
        messagebox.showinfo("Timer end", "Work Finished !")

        # Prepare the timer for a new start
        self.__get_settings()
        self.__update_page_info()
        self.__reset_page_graphics()

    def __calculate_step(self):
        """
        Calculate the step to apply to the arc animation
        :return: The calculated step (int)
        """

        # remaining_sec * 360 / total_sec == Angle to apply
        result = float(self.__remaining_time_seconds * 360 / self.__total_time_seconds_task)

        # Return the required value (359.99 if timer as not been started, prevent the ring to be hide)
        if result < 360:
            return result
        return 359.99


    def __get_settings(self):
        """
        Get the settings from json settings file and update the current minutes string
        """

        # Update the settings fetched from json file
        self.json_settings = SettingsReader().read_settings()

        # Only if timer is not running or paused
        if not self.__timer_is_running and not self.__timer_is_pause:

            # Update the required values
            self.__counter_minutes_str = int(self.json_settings['clock']['work_interval'])
            self.__tasks_counter = int(self.json_settings['clock']['tasks_counter'])
            self.__current_tasks_counter = self.__tasks_counter

    def __update_page_info(self):
        """
        Update the information of the notebook pages
        """

        # Clock timer page, update the required elements (if timer not started or paused)
        if str(self.__app_notebook.index(self.__app_notebook.select())) == "0":
            if not self.__timer_is_running and not self.__timer_is_pause:
                self.__alarm_clock_canvas.itemconfigure(self.__alarm_clock_text,
                                                        text='{:02d}:{:02d}'.format(
                                                                int(self.__counter_minutes_str),
                                                                int(0)))
                self.__alarm_clock_tasks_counter_label.config(text="Current session : 0 / " +
                                                                   str(self.__tasks_counter))

    def __reset_page_graphics(self):
        """
        Reset the default graphics of the timer
        """

        self.__alarm_clock_canvas.itemconfigure(self.__alarm_clock_arc, outline="black")
        self.__alarm_clock_canvas.itemconfigure(self.__alarm_clock_arc, extent=359.99)
        self.__alarm_clock_canvas.itemconfigure(self.__alarm_clock_current_task_text, text="")
        self.__alarm_clock_start_button.config(text="Start")
        self.__alarm_clock_pause_button['state'] = "disabled"

    def __on_notebook_page_changed(self, event):
        """
        On notebook page change, Update page with new json values
        """

        # Get the settings
        self.__get_settings()

        # Update the specific page information
        self.__update_page_info()

    def __on_closing(self):
        """
        Occurred when the window is closed, ask confirmation to user
        """

        if self.__timer_is_running or self.__timer_is_pause:
            if messagebox.askokcancel("Quit", "Do you really want to quit ?\nClock is running !"):
                sys.exit()

        else:
            sys.exit()
