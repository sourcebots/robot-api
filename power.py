import json
from pathlib import Path

from robot.board import Board


class PowerBoard(Board):

    def __init__(self, socket_path):
        super().__init__(socket_path)
        self._serial = Path(socket_path).stem

    @property
    def serial(self):
        """
        Serial number for the board
        """
        return self._serial

    def power_on(self):
        """
        Turn on power to all power board outputs
        """
        self._send(json.dumps({'power': True}).encode('utf-8'))
        self._recv()

    def power_off(self):
        """
        Turn off power to all power board outputs
        """
        self._send(json.dumps({'power': False}).encode('utf-8'))
        self._recv()
