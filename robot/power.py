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

        self.send_and_receive({'power': True})

    def power_off(self):
        """
        Turn off power to all power board outputs
        """

        self.send_and_receive({'power': False})
