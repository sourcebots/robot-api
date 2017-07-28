import json
import socket

import collections
from collections import OrderedDict


class BoardList(collections.MutableMapping):
    def __init__(self, *args, **kwargs):
        self.store = OrderedDict(*args, **kwargs)
        self.store_list = list(self.store.values())

    def __getitem__(self, attr):
        if type(attr) is int:
            return self.store_list[attr]
        return self.store[attr]

    def __setitem__(self, key, value):
        raise NotImplementedError("Cannot mutate board list")

    def __delitem__(self, key):
        raise NotImplementedError("Cannot mutate board list")

    def __iter__(self):
        return iter(self.store_list)

    def __len__(self):
        return len(self.store_list)


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

    def _receive_raw_from_socket_with_single_retry(self):
        return self._socket_with_single_retry(
            lambda s: s.recv(Board.RECV_BUFFER_BYTES),
        )

    def _send_raw_from_socket_with_single_retry(self, message):
        return self._socket_with_single_retry(
            lambda s: s.send(message),
        )

    def _send(self, message, should_retry=True):
        """
        Send a message to robotd
        :param retry: used internally
        :param message: message to send
        """
        return self._send_raw_from_socket_with_single_retry(message) if should_retry else self.sock.send(message)

    def _recv(self, should_retry=True):
        while b'\n' not in self.data:
            message = self._receive_raw_from_socket_with_single_retry() if should_retry else self.sock.recv()
            if message == b'':
                # Received blank, return blank
                return b''

            self.data += message
        line = self.data.split(b'\n', 1)[0]
        self.data = self.data[len(line) + 1:]
        return line

    def _send_recv(self, message):
        self._send(message)
        return self._recv()

    def _send_recv_data(self, data):
        return json.loads(self._send_recv(json.dumps(data).encode('utf-8')).decode("utf-8"))

    def _clean_up(self):
        self.sock.detach()
