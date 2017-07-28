from pathlib import Path

from robot.camera import Camera
from robot.motor import MotorBoard
from robot.power import PowerBoard
from robot.servo import ServoBoard
from robot.game import GameState
from robot.board import BoardList


class Robot:
    """
    Robot API
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
        # Try to turn on the outputs of the power board
        power_boards = self.power_boards
        if power_boards:
            self.power_boards[0].power_on()
        else:
            raise RuntimeError("Cannot find Power Board!")

    def _update_boards(self, known_boards, board_type, directory_name):
        """
        Update the number of boards against the known boards
        :param known_boards:
        :param board_type:
        :param directory_name:
        :return:
        """
        known_paths = {x.sock_path for x in known_boards}
        boards_dir = self.robotd_path / directory_name
        new_paths = {str(x) for x in boards_dir.glob('*')}
        boards = known_boards[:]
        # Add all boards that weren't previously there
        for board in new_paths - known_paths:
            boards.append(board_type(board))

        return sorted(boards, key=lambda b: b.serial)

    @staticmethod
    def _dictify_boards(boards):
        # Convert lists of boards into a dictionary
        return BoardList({board.serial for board in boards})

    # TODO: Parameterise the functions below so we only need one
    @property
    def motor_boards(self):
        """
        :return: list of available Motor boards, can be indexed by serial or by number
        """
        boards = self._update_boards(self.known_motor_boards, MotorBoard, 'motor')
        self.known_motor_boards = boards
        return self._dictify_boards(boards)

    @property
    def power_boards(self):
        """
        :return: list of available Power boards, can be indexed by serial or by number
        """
        boards = self._update_boards(self.known_power_boards, PowerBoard, 'power')
        self.known_power_boards = boards
        return self._dictify_boards(boards)

    @property
    def servo_boards(self):
        """
        :return: list of available Servo boards, can be indexed by serial or by number
        """
        boards = self._update_boards(self.known_servo_boards, ServoBoard, 'servo')
        self.known_servo_boards = boards
        return self._dictify_boards(boards)

    @property
    def cameras(self):
        """
        :return: list of available cameras, can be indexed by serial or by number
        """
        boards = self._update_boards(self.known_cameras, Camera, 'camera')
        self.known_cameras = boards
        return self._dictify_boards(boards)

    @property
    def _games(self):
        """
        :return: list of available GameStates, can be indexed by serial or by number
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
        return self._single_index("power board", self.power_boards)

    @property
    def motor_board(self):
        return self._single_index("motor board", self.motor_boards)

    @property
    def servo_board(self):
        return self._single_index("servo board", self.servo_boards)

    @property
    def camera(self):
        """
        Get the object representing the camera information
        """
        return self._single_index("camera", self.cameras)

    @property
    def _game(self):
        """
        Get the object representing the game information

        This is a private method, users should use self.zone to access the same information stored here.
        """
        return self._single_index("game states", self._games)

    @property
    def zone(self):
        """
        Get the zone the robot is in. This is changed by inserting a competition zone USB stick in it,
        the value defaults to 0 if there is no stick plugged in.

        :return: ID of the zone the robot started in (0-3)
        """
        return self._game.zone

    @property
    def mode(self):
        """
        Get which mode the robot is in,
        :return: either GameMode.COMPETITION or GameMode.DEVELOPMENT, if the robot is in
        competition or development mode respectively.
        """
        return self._game.mode

    def __del__(self):
        # stop the polling threads
        for camera in self.known_cameras:
            camera._stop_poll()
