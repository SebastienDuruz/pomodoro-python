# Author : Sébastien Duruz
# Date : 19.01.2021
# Description : The client side socket code.

from Sockets.socket_object import SocketObject
import socket


class Client(SocketObject):
    """
    Class Client, inherit socket
    """

    is_connected = False

    def __init__(self):

        # Init the parent object
        super().__init__()

        Client.is_connected = True

        # Set up the client
        # TODO: Set up the given IP as server IP
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect(self.ADDR)
        except ValueError:
            Client.is_connected = False

    def send(self, msg):
        """
        Send a message to server
        two steps:
            1) send a default length message to communicate the length of the message to server
            2) the actual message to send
        """
        try:

            message = msg.encode(self.FORMAT)
            msg_length = len(message)
            send_length = str(msg_length).encode(self.FORMAT)
            send_length += b' ' * (self.HEADER - len(send_length))
            self.client.send(send_length)
            self.client.send(message)
            print(self.client.recv(2048).decode(self.FORMAT))

        except ValueError:
            pass

            # TODO: Notify user about send failed
