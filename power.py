import json
import socket
from pathlib import Path


class PowerBoard:
    OUTPUTS = ['H0', 'H1', 'L0', 'L1', 'L2', 'L3']

    def __init__(self, socket_path):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        self.sock.connect(socket_path)
        self._serial = Path(socket_path).stem
        # Get the status message, throw it away
        _ = self.sock.recv(2048)

    @property
    def serial(self):
        """
        Serial number for the board
        """
        return self._serial

    def power_on(self):
        self.sock.send(json.dumps({'power': True}).encode('utf-8'))
        # Receive the response
        self.sock.recv(2048)

    def power_off(self):
        self.sock.send(json.dumps({'power': False}).encode('utf-8'))
        # Receive the response
        self.sock.recv(2048)
