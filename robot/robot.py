from pathlib import Path
from typing import Set  # noqa: F401

from robot.board import BoardList
from robot.camera import Camera
from robot.game import GameState
from robot.motor import MotorBoard
from robot.power import PowerBoard
from robot.servo import ServoBoard


class Robot:
    """
    Core class of the Robot API.

    This class provides access to the various boards which comprise the API.

    Internally it:
    - Speaks to robotd over unix socket
    - Always grabs from sockets, avoids caching
    """

    ROBOTD_ADDRESS = "/var/robotd"

    def __init__(self, robotd_path=ROBOTD_ADDRESS):
        self.robotd_path = Path(robotd_path)
        self.known_power_boards = []
        self.known_motor_boards = []
        self.known_servo_boards = []
        self.known_cameras = []
        self.known_gamestates = []
        print("Initializing Hardware...")
        self.all_known_boards = [
            self.known_power_boards,
            self.known_motor_boards,
            self.known_servo_boards,
            self.known_cameras,
            self.known_gamestates,
        ]

        self._display_boards()
        self._wait_for_power_board()

        print('Waiting for start button.')
        self.power_board.wait_start()

        self.power_board.power_on()
        print("Starting user code.")

    def _display_boards(self):
        print("Found the following hardware devices:")
        for board_list in self.all_known_boards:
            for board in board_list:
                print(board)

    def _wait_for_power_board(self):
        power_boards = self.power_boards
        if not power_boards:
            raise RuntimeError('Cannot find Power Board!')

    def _update_boards(self, known_boards, board_type, directory_name):
        """
        Update the number of boards against the known boards.

        :param known_boards:
        :param board_type:
        :param directory_name:
        :return:
        """
        known_paths = {x.socket_path for x in known_boards}  # type: Set[Path]
        boards_dir = self.robotd_path / directory_name  # type: Path
        new_paths = set(boards_dir.glob('*'))  # type: Set[Path]
        boards = known_boards[:]
        # Add all boards that weren't previously there
        for board_path in new_paths - known_paths:
            print("New board found:", board_path)

            try:
                new_board = board_type(board_path)
                boards.append(new_board)
            except (FileNotFoundError, ConnectionRefusedError) as e:
                print("Could not connect to the board:", board_path, e)

        return sorted(boards, key=lambda b: b.serial)

    @staticmethod
    def _dictify_boards(boards):
        # Convert lists of boards into a dictionary
        return BoardList({board.serial: board for board in boards})

    # TODO: Parameterise the functions below so we only need one
    @property
    def motor_boards(self):
        """
        :return: A ``BoardList`` of available ``MotorBoard``s.
        """
        boards = self._update_boards(self.known_motor_boards, MotorBoard, 'motor')
        self.known_motor_boards = boards
        return self._dictify_boards(boards)

    @property
    def power_boards(self):
        """
        :return: A ``BoardList`` of available ``PowerBoard``s.
        """
        boards = self._update_boards(self.known_power_boards, PowerBoard, 'power')
        self.known_power_boards = boards
        return self._dictify_boards(boards)

    @property
    def servo_boards(self):
        """
        :return: A ``BoardList`` of available ``ServoBoard``s.
        """
        boards = self._update_boards(
            self.known_servo_boards,
            ServoBoard,
            'servo_assembly',
        )
        self.known_servo_boards = boards
        return self._dictify_boards(boards)

    @property
    def cameras(self):
        """
        :return: A ``BoardList`` of available cameras.
        """
        boards = self._update_boards(self.known_cameras, Camera, 'camera')
        self.known_cameras = boards
        return self._dictify_boards(boards)

    @property
    def _games(self):
        """
        :return: A ``BoardList`` of available ``GameStates``.
        """
        boards = self._update_boards(self.known_gamestates, GameState, 'game')
        self.known_gamestates = boards
        return self._dictify_boards(boards)

    @staticmethod
    def _single_index(name, list_of_boards):
        if list_of_boards:
            return list_of_boards[0]
        else:
            raise AttributeError("No {}s connected".format(name))

    @property
    def power_board(self):
        """
        :return: The first ``PowerBoard``, if attached.

        Raises an ``AttributeError`` if there are no power boards attached.
        """
        return self._single_index("power board", self.power_boards)

    @property
    def motor_board(self):
        """
        :return: The first ``MotorBoard``, if attached.

        Raises an ``AttributeError`` if there are no motor boards attached.
        """
        return self._single_index("motor board", self.motor_boards)

    @property
    def servo_board(self):
        """
        :return: The first ``ServoBoard``, if attached.

        Raises an ``AttributeError`` if there are no servo boards attached.
        """
        return self._single_index("servo board", self.servo_boards)

    @property
    def camera(self):
        """
        :return: The first ``Camera``, if attached.

        Raises an ``AttributeError`` if there are no cameras attached.
        """
        return self._single_index("camera", self.cameras)

    @property
    def _game(self):
        """
        :return: The first ``GameStates``, if any.

        Raises an ``AttributeError`` if there are no game state configured.
        """
        return self._single_index("game states", self._games)

    @property
    def zone(self):
        """
        The zone the robot is in.

        This is changed by inserting a competition zone USB stick in it, the
        value defaults to 0 if there is no stick plugged in.

        :return: ID of the zone the robot started in (0-3)
        """
        return self._game.zone

    @property
    def mode(self):
        """
        The ``GameMode`` the robot is in.

        :return: one of ``GameMode.COMPETITION`` or ``GameMode.DEVELOPMENT``.
        """
        return self._game.mode

    def close(self):
        """
        Cleanup robot instance.
        """

        for board_group in self.all_known_boards:
            for board in board_group:
                board.close()

            # Clear the group so that any further access doesn't accidentally
            # reanimate the boards (which isn't supported).
            del board_group[:]

    def __del__(self):
        self.close()
