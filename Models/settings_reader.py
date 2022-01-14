# Author : Sébastien Duruz
# Date : 12.01.2021
# Description : Model to access (Read and Write) to json settings file

import json
import os


class SettingsReader:

    def __init__(self):
        """
        Class Constructor
        """

        # The file path of the json file that contains settings
        self.settings_file_path = "settings.json"

        # Create the settings file if not already exists
        if not SettingsReader.settings_file_exists(self):
            SettingsReader.write_new_settings_file(self)

    def settings_file_exists(self):
        """
        Check if the settings file exists
        :return: True if exists, false if not
        """

        if os.path.isfile(self.settings_file_path):
            return True
        return False

    def write_new_settings_file(self):
        """
        Write a new settings file with default values
        """

        # Build default settings
        settings = {'clock': {
            'short_break': '5',
            'work_interval': '25',
            'tasks_counter': '5'
        }}

        # Write the settings to the json file
        with open(self.settings_file_path, 'w') as outfile:
            json.dump(settings, outfile)

    def modify_clock_settings(self, short_break, work_interval, task_counter):
        """
        Modify the clock settings with new values
        """

        # Read the current state of the json file
        json_content = SettingsReader.read_settings(self)

        # Modify the required settings
        json_content['clock']['short_break'] = short_break
        json_content['clock']['work_interval'] = work_interval
        json_content['clock']['tasks_counter'] = task_counter

        # Write the new content to json file
        with open(self.settings_file_path, "w") as outfile:
            json.dump(json_content, outfile)

    def read_settings(self):
        """
        Read the settings from json file
        :return: The content of the json file
        """

        # If the file does not already exist, create it
        if not SettingsReader.settings_file_exists(self):
            SettingsReader.write_new_settings_file(self)

        # Return the content of the file
        with open(self.settings_file_path) as json_file:
            return json.load(json_file)
