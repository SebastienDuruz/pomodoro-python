# Author : Sébastien Duruz
# Date : 19.01.2021
# Description : The client side socket code.

from socket_object import SocketObject
import socket


class Client(SocketObject):
    """
    Class Client, inherit socket
    """

    def __init__(self):

        # Set up the client
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(self.ADDR)

        self.send("Hello, I'm a client")

    def send(self, msg):
        """
        Send a message to server
        two steps:
            1) send a default length message to communicate the length of the message to server
            2) the actual message to send
        """

        message = msg.encode(self.FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(self.FORMAT)
        send_length += b' ' * (self.HEADER - len(send_length))
        self.client.send(send_length)
        self.client.send(message)
        print(self.client.recv(2048).decode(self.FORMAT))
