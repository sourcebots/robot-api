import json
import time
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
        self.socket_path = socket_path
        self.socket = None
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
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.settimeout(self.SEND_TIMEOUT_SECS)

        try:
            self.socket.connect(str(self.socket_path))
        except ConnectionRefusedError as e:
            print('Error connecting to:', socket_path)
            raise e

        greeting = self.receive()
        self._greeting_response(greeting)

    def _get_lc_error(self):
        """
        :return: The text for a lost connection error
        """
        return "Lost Connection to {conn} at {path}".format(
            conn=str(self.__class__.__name__),
            path=self.socket_path
        )

    def _socket_with_single_retry(self, handler):
        retryable_errors = (socket.timeout, BrokenPipeError, OSError)

        backoffs = [
            0.1,
            0.5,
            1.0,
            2.0,
            3.0,
        ]

        try:
            return handler()
        except retryable_errors as e:
            original_exception = e

        for backoff in backoffs:
            time.sleep(backoff)

            try:
                self._connect(self.socket_path)
            except ConnectionRefusedError:
                continue

            try:
                return handler()
            except retryable_errors:
                pass

        raise original_exception

    def send(self, message, should_retry=True):
        """
        Send a message to robotd
        :param retry: used internally
        :param message: message to send
        """

        data = (json.dumps(message) + '\n').encode('utf-8')

        def sendall():
            self.socket.sendall(data)

        if should_retry:
            return self._socket_with_single_retry(sendall)
        else:
            return sendall()

    def receive(self, should_retry=True):
        while b'\n' not in self.data:
            if should_retry:
                message = self._socket_with_single_retry(
                    lambda: self.socket.recv(4096)
                )
            else:
                message = self.socket.recv(4096)

            if message == b'':
                return {}

            self.data += message
        line = self.data.split(b'\n', 1)[0]
        self.data = self.data[len(line) + 1:]

        return json.loads(line.decode('utf-8'))

    def send_and_receive(self, message, should_retry=True):
        self.send(message, should_retry)
        return self.receive(should_retry)

    def _clean_up(self):
        self.socket.detach()
