import socket


class Board:
    SEND_TIMEOUT = 20
    RECV_BUFFER = 2048

    def __init__(self, socket_path):
        self.sock_path = socket_path
        self.sock = None
        self._recv_buffer = []
        self._connect(socket_path)

    def _greeting_response(self, data):
        """Handle the response to the greeting command
        NOTE: This is called on reconnect in addition to first connection"""
        pass

    def _connect(self, socket_path):
        """
        (re)connect to a new socket
        :param socket_path: Path for the unix socket
        """
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        self.sock.settimeout(Board.SEND_TIMEOUT)
        self.sock.connect(socket_path)
        greeting = self._recv(_retry=True)
        self._greeting_response(greeting)

    def _get_lc_error(self):
        """
        :return: The text for a lost connection error
        """
        return "Lost Connection to {} at {}".format(str(self.__class__.__name__), self.sock_path)

    def _send_recv(self, message):
        self._send(message)
        return self._recv()

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
                raise ConnectionError(self._get_lc_error())
            else:
                try:
                    self._connect(self.sock_path)  # Reconnect
                except FileNotFoundError:
                    raise ConnectionError(self._get_lc_error())
                self._send(message, retry=True)  # Retry Recursively

    def _recv(self, _retry=False):
        """
        Receive a message from the robotd socket
        :return: the message
        """

        # TODO catch empty string receives as bad things
        unended_text = b''

        while not self._recv_buffer:
            strings = []
            try:
                output = self.sock.recv(Board.RECV_BUFFER)
            except (socket.timeout, BrokenPipeError, OSError) as e:
                if _retry:
                    raise ConnectionError(self._get_lc_error())
                else:
                    print("Connection", self.sock_path, e, "retrying")
                    self._connect(self.sock_path)
                    return self._recv(_retry=True)  # Retry recursively
            strings.extend((unended_text + output).split(b'\n'))
            if strings == [b'']:
                self._recv_buffer.append(b'')
            unended_text = strings.pop()
            if not unended_text:
                self._recv_buffer.extend([x for x in strings if x != b''])

        return self._recv_buffer.pop(0)

    def _clean_up(self):
        self.sock.detach()
