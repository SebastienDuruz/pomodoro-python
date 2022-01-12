# ETML
# Author : Sébastien Duruz
# Date : 12.01.2021
# Description : Model to access (Read and Write) to json settings file

import json
import os


class SettingsReader:

    # The file path of the json file that contains settings
    settings_file_path = "settings.json"

    def __init__(self):
        """
        Class Constructor
        """

        # Create the settings file if not already exists
        if not SettingsReader.settings_file_exists():
            SettingsReader.write_new_settings_file()

    @staticmethod
    def settings_file_exists():
        """
        Check if the settings file exists
        :return: True if exists, false if not
        """

        if os.path.isfile(SettingsReader.settings_file_path):
            return True
        return False

    @staticmethod
    def write_new_settings_file():
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
        with open(SettingsReader.settings_file_path, 'w') as outfile:
            json.dump(settings, outfile)

    @staticmethod
    def read_settings():
        """
        Read the settings from json file
        :return: The content of the json file
        """

        # If the file does not already exist, create it
        if not SettingsReader.settings_file_exists():
            SettingsReader.write_new_settings_file()

        # Return the content of the file
        with open(SettingsReader.settings_file_path) as json_file:
            return json.load(json_file)

