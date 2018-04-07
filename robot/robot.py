import functools
import logging
from pathlib import Path
from typing import Callable, List, Set, Type, Union  # noqa: F401

from robot import __VERSION__
from robot.board import BoardList, TBoard
from robot.camera import Camera
from robot.game import GameMode, GameState, Zone, kill_after_delay
from robot.game_specific import GAME_DURATION_SECONDS, GAME_EXIT_MESSAGE
from robot.motor import MotorBoard
from robot.power import PowerBoard
from robot.servo import ServoBoard

_PathLike = Union[str, Path]

LOGGER = logging.getLogger(__name__)


def configure_logging() -> None:
    """
    Configure basic logging.

    This has us outputting ``logging.INFO`` and higher messages. This function
    is called within ``Robot.__init__`` for convenience, though as it uses
    ``logging.basicConfig`` it is a no-op if logging has already been configured.
    """
    logging.basicConfig(level=logging.INFO)


class Robot:
    """
    Core class of the Robot API.

    This class provides access to the various boards which comprise the API.

    Internally it:
    - Speaks to robotd over unix socket
    - Always grabs from sockets, avoids caching
    """

    ROBOTD_ADDRESS = "/var/robotd"

    def __init__(
        self,
        robotd_path: _PathLike=ROBOTD_ADDRESS,
        wait_for_start_button: bool=True,
    ) -> None:
        self.robotd_path = Path(robotd_path)
        self.known_power_boards = []  # type: List[PowerBoard]
        self.known_motor_boards = []  # type: List[MotorBoard]
        self.known_servo_boards = []  # type: List[ServoBoard]
        self.known_cameras = []  # type: List[Camera]
        self.known_gamestates = []  # type: List[GameState]

        configure_logging()

        LOGGER.info("Robot (v{}) Initialising...".format(__VERSION__))
        self._assert_has_power_board()
        self.power_board.power_on()

        if wait_for_start_button:
            self.power_board.wait_start()

    def _assert_has_power_board(self):
        power_boards = self.power_boards
        if not power_boards:
            raise RuntimeError('Cannot find Power Board!')

    def _update_boards(
        self,
        known_boards: List[TBoard],
        board_type: Callable[[_PathLike], TBoard],
        directory_name: _PathLike,
    ) -> BoardList[TBoard]:
        """
        Update the number of boards against the known boards.

        :param known_boards: The list of all currently known boards; this list
                             will be updated with any newly found boards.
        :param board_type: The type of board to create.
        :param directory_name: The relative directory to look in for new boards.
        :return: A ``BoardList[TBoard]`` of all the known boards (both
                 previously known and newly found).
        """
        known_paths = {x.socket_path for x in known_boards}  # type: Set[Path]
        boards_dir = self.robotd_path / directory_name  # type: Path
        new_paths = set(boards_dir.glob('*'))  # type: Set[Path]
        # Add all boards that weren't previously there
        for board_path in new_paths - known_paths:
            LOGGER.info("New board found: '%s'", board_path)

            try:
                new_board = board_type(board_path)
                known_boards.append(new_board)
            except (FileNotFoundError, ConnectionRefusedError):
                LOGGER.warning(
                    "Could not connect to the board: '%s'",
                    board_path,
                    exc_info=True,
                )

        return BoardList(known_boards)

    @property
    def motor_boards(self) -> BoardList[MotorBoard]:
        """
        :return: A ``BoardList`` of available ``MotorBoard``s.
        """
        return self._update_boards(self.known_motor_boards, MotorBoard, 'motor')

    def _configure_death(self):
        if self.mode == GameMode.COMPETITION:
            kill_after_delay(GAME_DURATION_SECONDS, GAME_EXIT_MESSAGE)

    @property
    def power_boards(self) -> BoardList[PowerBoard]:
        """
        :return: A ``BoardList`` of available ``PowerBoard``s.
        """
        return self._update_boards(
            self.known_power_boards,
            functools.partial(PowerBoard, on_start_signal=self._configure_death),
            'power',
        )

    @property
    def servo_boards(self) -> BoardList[ServoBoard]:
        """
        :return: A ``BoardList`` of available ``ServoBoard``s.
        """
        return self._update_boards(
            self.known_servo_boards,
            ServoBoard,
            'servo_assembly',
        )

    @property
    def cameras(self) -> BoardList[Camera]:
        """
        :return: A ``BoardList`` of available cameras.
        """
        return self._update_boards(self.known_cameras, Camera, 'camera')

    @property
    def _games(self) -> BoardList[GameState]:
        """
        :return: A ``BoardList`` of available ``GameStates``.
        """
        return self._update_boards(self.known_gamestates, GameState, 'game')

    @staticmethod
    def _single_index(name, list_of_boards: BoardList[TBoard]) -> TBoard:
        if list_of_boards:
            return list_of_boards[0]
        else:
            raise AttributeError("No {}s connected".format(name))

    @property
    def power_board(self) -> PowerBoard:
        """
        :return: The first ``PowerBoard``, if attached.

        Raises an ``AttributeError`` if there are no power boards attached.
        """
        return self._single_index("power board", self.power_boards)

    @property
    def motor_board(self) -> MotorBoard:
        """
        :return: The first ``MotorBoard``, if attached.

        Raises an ``AttributeError`` if there are no motor boards attached.
        """
        return self._single_index("motor board", self.motor_boards)

    @property
    def servo_board(self) -> ServoBoard:
        """
        :return: The first ``ServoBoard``, if attached.

        Raises an ``AttributeError`` if there are no servo boards attached.
        """
        return self._single_index("servo board", self.servo_boards)

    @property
    def camera(self) -> Camera:
        """
        :return: The first ``Camera``, if attached.

        Raises an ``AttributeError`` if there are no cameras attached.
        """
        return self._single_index("camera", self.cameras)

    @property
    def _game(self) -> GameState:
        """
        :return: The first ``GameStates``, if any.

        Raises an ``AttributeError`` if there are no game state configured.
        """
        return self._single_index("game states", self._games)

    @property
    def zone(self) -> Zone:
        """
        The zone the robot is in.

        This is changed by inserting a competition zone USB stick in it, the
        value defaults to 0 if there is no stick plugged in.

        :return: ID of the zone the robot started in (0-3)
        """
        return self._game.zone

    @property
    def mode(self) -> GameMode:
        """
        The ``GameMode`` the robot is in.

        :return: one of ``GameMode.COMPETITION`` or ``GameMode.DEVELOPMENT``.
        """
        return self._game.mode

    def close(self):
        """
        Cleanup robot instance.
        """

        for board_group in (
            self.known_power_boards,
            self.known_motor_boards,
            self.known_servo_boards,
            self.known_cameras,
            self.known_gamestates,
        ):
            for board in board_group:
                board.close()

            # Clear the group so that any further access doesn't accidentally
            # reanimate the boards (which isn't supported).
            del board_group[:]

    def __del__(self):
        self.close()
