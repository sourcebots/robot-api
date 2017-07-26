import re
import socket


class Board:
    SEND_TIMEOUT_SECS = 2
    RECV_BUFFER_BYTES = 2048

    def __init__(self, socket_path):
        self.sock_path = socket_path
        self.sock = None
        self.data = b''
        self._connect(socket_path)

    def _greeting_response(self, data):
        """
        Handle the response to the greeting command
        NOTE: This is called on reconnect in addition to first connection
        """
        pass

    def _connect(self, socket_path):
        """
        (re)connect to a new socket
        :param socket_path: Path for the unix socket
        """
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        self.sock.settimeout(Board.SEND_TIMEOUT_SECS)
        self.sock.connect(socket_path)
        greeting = self._recv()
        self._greeting_response(greeting)

    def _get_lc_error(self):
        """
        :return: The text for a lost connection error
        """
        return "Lost Connection to {} at {}".format(str(self.__class__.__name__), self.sock_path)

    def _send_recv(self, message):
        self._send(message)
        return self._recv()

    def _send(self, message, _is_retry=False):
        """
        Send a message to robotd
        :param retry: used internally
        :param message: message to send
        """
        try:
            self.sock.send(message)
        except (socket.timeout, BrokenPipeError, OSError):
            if _is_retry:
                raise ConnectionError(self._get_lc_error())
            else:
                try:
                    self._connect(self.sock_path)  # Reconnect
                except FileNotFoundError:
                    raise ConnectionError(self._get_lc_error())
                self._send(message, _is_retry=True)  # Retry Recursively

    def _socket_with_single_retry(self, handler):
        retryable_errors = (socket.timeout, BrokenPipeError, OSError)

        try:
            return handler(self.sock)
        except retryable_errors:
            pass

        # Retry once, need to reconnect first
        try:
            self._connect(self.sock_path)
        except FileNotFoundError:
            raise ConnectionError(self._get_lc_error())

        try:
            return handler(self.sock)
        except retryable_errors:
            raise ConnectionError(self._get_lc_error())

    def receive_raw_from_socket_with_single_retry(self):
        return self._socket_with_single_retry(
            lambda s: s.recv(Board.RECV_BUFFER_BYTES),
        )

    def _recv(self, should_retry=True):
        while b'\n' not in self.data:
            if should_retry:
                message = self.receive_raw_from_socket_with_single_retry()
            else:
                message = self.sock.recv()
            if message == b'':
                # Received blank, return blank
                return b''

            self.data += message
        line = re.search(b'.*\n', self.data).group(0)
        self.data = self.data[len(line):]
        return line

    def _clean_up(self):
        self.sock.detach()
