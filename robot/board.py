import logging
import socket
from pathlib import Path
from typing import Mapping, TypeVar, Union

from .connection import Connection, Message

LOGGER = logging.getLogger(__name__)


class Board:
    """Base class for connections to ``robotd`` board sockets."""

    CONNECTION_TIMEOUT_SECS = 6

    def __init__(self, socket_path: Union[Path, str]) -> None:
        self.socket_path = Path(socket_path)

        self.connection = Connection(self._get_socket())
        self._greeting_response(self.connection.receive())

    @property
    def serial(self):
        """Serial number for the board."""
        return self.socket_path.stem

    def _greeting_response(self, data):
        """
        Handle the response to the greeting command.

        NOTE: This is called on reconnect in addition to first connection
        """
        pass

    def _get_socket(self):
        """
        Connect or reconnect to a socket.

        :param socket_path: Path for the unix socket
        """
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(self.CONNECTION_TIMEOUT_SECS)

        try:
            sock.connect(str(self.socket_path))
        except ConnectionRefusedError as e:
            LOGGER.exception("Error connecting to: '%s'", self.socket_path)
            raise

        return sock

    def _reconnect(self) -> None:
        self.connection.close()

        self.connection = Connection(self._get_socket())
        self._greeting_response(self.connection.receive())

    def _get_lc_error(self) -> str:
        """
        Describe a lost connection error.

        :return: The text for a lost connection error
        """
        return "Lost Connection to {conn} at {path}".format(
            conn=str(self.__class__.__name__),
            path=self.socket_path,
        )

    def _send(self, message: Message) -> None:
        """
        Send a message to robotd.

        :param message: message to send
        """
        try:
            self.connection.send(message)
        except (BrokenPipeError, ConnectionError):
            self._reconnect()
            self.connection.send(message)

    def _receive(self):
        """
        Receive a message from robotd.
        """
        try:
            return self.connection.receive()
        except (BrokenPipeError, ConnectionError):
            self._reconnect()
            return self.connection.receive()

    def _send_and_receive(self, message):
        """
        Send a message to robotd and wait for a response.
        """
        self._send(message)
        return self._receive()

    def close(self):
        """
        Close the the connection to the underlying robotd board.
        """
        self.connection.close()

    def __str__(self):
        return "{} - {}".format(self.__name__, self.serial)

    __del__ = close


TBoard = TypeVar('TBoard', bound=Board)


class BoardList(Mapping[Union[str, int], TBoard]):
    """A mapping of ``Board``s allowing access by index or identity."""

    def __init__(self, *args, **kwargs):
        self._store = dict(*args, **kwargs)
        self._store_list = sorted(self._store.values(), key=lambda board: board.serial)

    def __getitem__(self, attr: Union[str, int]) -> TBoard:
        if isinstance(attr, int):
            return self._store_list[attr]
        return self._store[attr]

    def __iter__(self):
        return iter(self._store_list)

    def __len__(self) -> int:
        return len(self._store_list)
