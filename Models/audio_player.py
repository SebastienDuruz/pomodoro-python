# Author : Sébastien Duruz
# Date : 13.01.2021
# Description : Play an audio file defined at object instanciation

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

        self.audio_file_path = file

    def play_audio(self):
        """
        Play the audio file with playsound library
        """

        def thread_audio():
            """
            Called by the thread
            """

            playsound.playsound(self.audio_file_path)

        # Play sound on a new thread
        threading.Thread(target=thread_audio).start()

