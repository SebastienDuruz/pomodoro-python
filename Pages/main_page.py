# ETML
# Author : Sébastien Duruz
# Date : 10.01.2021
# Description : The main page of the application

import tkinter as tk


class MainPage:

    def __init__(self):
        """
        Class Constructor
        """

        # Build the window
        window = tk.Tk()
        window.title("Pomodoro Timer")
        window.geometry("500x600")
        window.configure(bg="black")

        # Current timer Canvas
        alarm_clock_canvas = tk.Canvas(window, background="black", width=300, height=300)
        alarm_clock_canvas.create_oval(50, 50, 250, 250, outline="white")
        alarm_clock_canvas.create_text(150, 150, text="15:32", fill="white")
        alarm_clock_canvas.pack()

        # Start button
        start_clock_button = tk.Button(window, text="Start")
        start_clock_button.pack()

        window.mainloop()



