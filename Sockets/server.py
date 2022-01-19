# Author : Sébastien Duruz
# Date : 19.01.2021
# Description : The server side socket code.

from Sockets.socket_object import SocketObject
import socket
import threading


class Server(SocketObject):
    """
    Class Server, inherit socket
    """

    is_running = False

    def __init__(self):
        """
        Class Constructor
        """

        # build the parent
        super().__init__()

        # Prepare the server
        self.host = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.host.bind(self.ADDR)

    def start(self):
        """
        Start the server routine
        """

        # Try to start server, stop execution if failed
        try:
            self.host.listen()
            print(f"[LISTENING] Server is listening on {self.SERVER}")
            Server.is_running = True
        except ValueError:
            print(f"[ERROR] An error occurred, the server can't be start !")
            Server.is_running = False
            return

        # Server is connected
        while True:

            # Stop thread execution if needed
            if not Server.is_running:
                print(f"[SERVER STOP] Server is stopping on {self.SERVER}")
                return

            # Wait for a client to connect
            conn, addr = self.host.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.daemon = True
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

    def handle_client(self, conn, addr):
        """
        A new client is connected (used as a thread method)
        """

        print(f"[NEW CONNECTION] {addr} connected.")

        connected = True

        while connected and Server.is_running:

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


