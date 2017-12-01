from enum import Enum
import json
from pathlib import Path
from typing import Union
from robot.board import Board


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
    def zone(self) -> int:
        """
        get the zone the robot starts in. This is changed by inserting a competition zone USB stick in it,
        the value defaults to 0 if there is no stick plugged in.
        :return: zone ID the robot started in (0-3)
        """
        return self.send_and_receive({})['zone']

    @property
    def mode(self) -> GameMode:
        """
        Whether or not the robot is in competition mode
        :return: if the robot is in competition mode
        """
        value = self.send_and_receive({})['mode']
        return GameMode(value)
