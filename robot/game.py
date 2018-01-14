from enum import Enum
from pathlib import Path
from typing import NewType
from robot.board import Board

Zone = NewType('Zone', int)


class GameMode(Enum):
    """Possible modes the robot can be in."""

    COMPETITION = 'competition'
    DEVELOPMENT = 'development'


class GameState(Board):
    """A description of the initial game state the robot is operating under."""

    def __init__(self, socket_path):
        super().__init__(socket_path)
        self._serial = Path(socket_path).stem

    @property
    def serial(self):
        """Id of the game connection."""
        return self._serial

    @property
    def zone(self) -> Zone:
        """
        The zone in which the robot starts the match.

        This is configured by inserting a competition zone USB stick into the
        robot.

        :return: zone ID the robot started in (0-3)
        """
        return self.send_and_receive({})['zone']

    @property
    def mode(self) -> GameMode:
        """
        :return: The ``GameMode`` that the robot is currently in.
        """
        value = self.send_and_receive({})['mode']
        return GameMode(value)
