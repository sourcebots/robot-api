from pathlib import Path

from robot.camera import Camera
from robot.motor import MotorBoard
from robot.power import PowerBoard
from robot.servo import ServoBoard
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
        # Try to turn on the outputs of the power board
        power_boards = self.power_boards
        if power_boards:
            self.power_board = power_boards[0]
            self.power_board.power_on()
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
        new_boards = {str(x) for x in boards_dir.glob('*')}
        boards = known_boards[:]
        # Add all boards that weren't previously there
        for board in new_boards - known_paths:
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
        :return: list of available Cameras, can be indexed by serial or by number
        """
        boards = self._update_boards(self.known_cameras, Camera, 'camera')
        self.known_cameras = boards
        return self._dictify_boards(boards)

    def __del__(self):
        # stop the polling threads
        for camera in self.known_cameras:
            camera._stop_poll()
