import json
import threading
from collections.abc import MutableSequence
from pathlib import Path

import select

from enum import Enum

from robot.board import Board
from robot.markers import Marker


class GameMode(Enum):
    COMPETITION = 'competition'
    DEVELOPMENT = 'development'


class GameState(Board):
    """
    Object representing the game state
    """

    def __init__(self, socket_path):
        super().__init__(socket_path)
        self._serial = Path(socket_path).stem

    @property
    def serial(self):
        """
        name of the socket
        """
        return self._serial

    @property
    def zone(self):
        """
        get the zone the robot starts in. This is changed by inserting a competition zone USB stick in it,
        the value defaults to 0 if there is no stick plugged in.
        :return: zone ID the robot started in (0-3)
        """
        return json.loads(self._send_recv(b'{}'))['zone']

    @property
    def mode(self):
        """
        Whether or not the robot is in competition mode
        :return: if the robot is in competition mode
        """
        value = json.loads(self._send_recv(b'{}'))['mode']
        for enum in GameMode:
            if value == enum.value:
                return enum
