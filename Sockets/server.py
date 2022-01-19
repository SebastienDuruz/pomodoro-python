# Author : Sébastien Duruz
# Date : 19.01.2021
# Description : The server side socket code.

from socket_object import SocketObject
import socket
import threading


class Server(SocketObject):
    """
    Class Server, inherit socket
    """

    def __init__(self):
        """
        Class Constructor
        """

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDR)

    def start(self):
        """
        Start the server routine
        """

        # Try to start server, stop execution if failed
        try:
            self.server.listen()
            print(f"[LISTENING] Server is listening on {self.SERVER}")
        except ValueError:
            print(f"An error occurred, the server can't be start !")
            return

        # Server is connected
        while True:
            conn, addr = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

    def handle_client(self, conn, addr):
        """
        A new client is connected (used as a thread method)
        """

        print(f"[NEW CONNECTION] {addr} connected.")

        connected = True

        while connected:

            # Get the length of the message
            msg_length = conn.recv(self.HEADER).decode(self.FORMAT)

            # If a message as been sent by the client
            if msg_length:

                # Decode the message
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(self.FORMAT)
                print(f"[{addr}] sent {msg}")

                # Disconnect the client
                # TODO: Respond to client with specific response
                if msg == self.DISCONNECT_MESSAGE:
                    connected = False
                elif msg == self.TIMER_VALUE:
                    conn.send("12:15".encode(self.FORMAT))

        conn.close()

