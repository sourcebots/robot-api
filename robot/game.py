import logging
import signal
from enum import Enum
from typing import NewType

from robot.board import Board

Zone = NewType('Zone', int)

LOGGER = logging.getLogger(__name__)


def timeout_handler(signum, stack):
    """
    Handle the `SIGALRM` to kill the current process.
    """
    raise SystemExit("Timeout expired: Game Over!")


def kill_after_delay(timeout_seconds):
    """
    Interrupts main process after the given delay.
    """

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)


class GameMode(Enum):
    """Possible modes the robot can be in."""

    COMPETITION = 'competition'
    DEVELOPMENT = 'development'


class GameState(Board):
    """A description of the initial game state the robot is operating under."""

    @property
    def zone(self) -> Zone:
        """
        The zone in which the robot starts the match.

        This is configured by inserting a competition zone USB stick into the
        robot.

        :return: zone ID the robot started in (0-3)
        """
        return self._send_and_receive({})['zone']

    @property
    def mode(self) -> GameMode:
        """
        :return: The ``GameMode`` that the robot is currently in.
        """
        value = self._send_and_receive({})['mode']
        return GameMode(value)
