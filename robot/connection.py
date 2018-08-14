import json
import socket
from typing import Any, Dict

Message = Dict[str, Any]


class Connection:
    """
    A connection to a device.

    This wraps a ``socket.socket`` providing encoding and decoding so that
    consumers of this class can send and receive JSON-compatible typed data
    rather than needing to worry about lower-level details.
    """

    def __init__(self, socket: socket.socket) -> None:
        """Wrap the given socket."""
        self.socket = socket
        self.data = b''

    def close(self) -> None:
        """Close the connection."""
        self.socket.close()

    def send(self, message: Message) -> None:
        """Send the given JSON-compatible message over the connection."""
        line = json.dumps(message).encode('utf-8') + b'\n'
        self.socket.sendall(line)

    def receive(self) -> Message:
        """Receive a single message from the connection."""
        while b'\n' not in self.data:
            message = self.socket.recv(4096)
            if message == b'':
                raise BrokenPipeError()

            self.data += message
        line = self.data.split(b'\n', 1)[0]
        self.data = self.data[len(line) + 1:]

        return json.loads(line.decode('utf-8'))
