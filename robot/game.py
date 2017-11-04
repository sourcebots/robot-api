from enum import Enum
import json

from robot.board import Board


class GameMode(Enum):
    COMPETITION = 'competition'
    DEVELOPMENT = 'development'


class GameState(Board):
    """
    Object representing the game state
    """

    @property
    def zone(self):
        """
        get the zone the robot starts in. This is changed by inserting a competition zone USB stick in it,
        the value defaults to 0 if there is no stick plugged in.
        :return: zone ID the robot started in (0-3)
        """
        return self.send_and_receive({})['zone']

    @property
    def mode(self):
        """
        Whether or not the robot is in competition mode
        :return: if the robot is in competition mode
        """
        value = self.send_and_receive({})['mode']
        for enum in GameMode:
            if value == enum.value:
                return enum
