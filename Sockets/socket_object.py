# Author : Sébastien Duruz
# Date : 19.01.2021
# Description : The base class for socket objects.

import socket


class SocketObject:
    """
    Class Socket
    """

    def __init__(self):
        """
        Class Constructor
        """

        # Communication settings
        self.HEADER = 64
        self.FORMAT = 'utf-8'

        # Set an unused port (used for server) and get the local IP
        # TODO: external access !
        self.PORT = 5050
        self.SERVER = socket.gethostbyname(socket.gethostname())
        self.ADDR = (self.SERVER, self.PORT)

        # Define the command used by the client
        self.DISCONNECT_MESSAGE = '!DISCONNECT'
        self.TIMER_VALUE = '!TIMER'
        self.TIMER_TYPE = '!TYPE'
        self.GET_TOTAL_TASKS = '!TOTAL'
        self.GET_REMAINING_TASKS = '!REMAINS'
