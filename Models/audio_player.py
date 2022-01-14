# Author : Sébastien Duruz
# Date : 13.01.2021
# Description : Play an audio file defined at object instantiation

import threading
import playsound


class AudioPlayer:
    """
    Class AudioPlayer
    """

    def __init__(self, file):
        """
        Class Constructor
        """

        self.__audio_file_path = file

    def play_audio(self):
        """
        Play the audio file with playsound library
        """

        def __thread_audio():
            """
            Called by the thread
            """

            playsound.playsound(self.__audio_file_path)

        # Play sound on a new thread
        threading.Thread(target=__thread_audio).start()

