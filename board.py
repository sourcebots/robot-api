import socket


class Board:
    SEND_TIMEOUT = 2
    RECV_BUFFER = 2048

    def __init__(self, socket_path):
        self.sock_path = socket_path
        self.sock = None
        self._connect(socket_path)
        print("Receiving response:")
        data = self._recv()
        self._init_response(data)
        print("Response:", data)

    def _init_response(self, data):
        pass  # Handle the response to the init command

    def _connect(self, socket_path):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        self.sock.settimeout(Board.SEND_TIMEOUT)
        self.sock.connect(socket_path)

    def _get_lc_error(self):
        raise ConnectionError("Lost Connection to {} at {}".format(str(self.__class__.__name__), self.sock_path))

    def _send(self, message, retry=False):
        """
        Send a message to robotd
        :param retry: used internally
        :param message: message to send
        """
        try:
            self.sock.send(message)
        except (socket.timeout, BrokenPipeError, OSError):
            if retry:
                raise self._get_lc_error()
            else:
                try:
                    self._connect(self.sock_path)  # Reconnect
                except FileNotFoundError:
                    raise self._get_lc_error()
                self._send(message, retry=True)  # Retry Recursively

    def _recv(self, retry=False):
        """
        Receive a message from the robotd socket
        :return: message
        """
        try:
            return self.sock.recv(Board.RECV_BUFFER)
        except (socket.timeout, BrokenPipeError, OSError):
            if retry:
                raise self._get_lc_error()
            else:
                self._connect(self.sock_path)  # Reconnect
                return self._recv(retry=True)  # Retry recursively

    def clean_up(self):
        self.sock.detach()
