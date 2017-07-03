import socket
from pathlib import Path

from robot.motor import MotorBoard
from robot.power import PowerBoard


class Robot:
    """
    Robot API
    - Speaks to robotd over unix socket
    - Always grabs from sockets, avoids caching
    """

    ROBOTD_ADDRESS = "/var/robotd"

    def __init__(self, robotd_path=ROBOTD_ADDRESS):
        self.robotd_path = Path(robotd_path)
        # Try to power up the power board
        power_boards = self.power_boards
        if power_boards:
            self.power_board = power_boards[0]
            self.power_board.power_on()
        else:
            raise RuntimeError("Cannot find Power Board!")

    def get_boards(self, board_type, directory_name):
        boards = []
        boards_dir = self.robotd_path / directory_name
        for board_sock in boards_dir.glob('*'):
            boards.append(board_type(str(board_sock)))
        return boards

    @staticmethod
    def _motor_board_dict_gen(boards):
        return {i: x for i, x in enumerate(boards)}.update(
            {x.serial: x for x in enumerate(boards)}
        )

    @staticmethod
    def arrange_boards_by_serial(boards):
        # Convert lists of boards into a dictionary
        boards_dict = {}
        for i, board in enumerate(boards):
            boards_dict[i] = board
            boards_dict[board.serial] = board
        return boards_dict

    @property
    def motor_boards(self):
        boards = self.get_boards(MotorBoard, 'motor')
        boards_dict = self.arrange_boards_by_serial(boards)
        return boards_dict

    @property
    def power_boards(self):
        boards = self.get_boards(PowerBoard, 'power')
        boards_dict = self.arrange_boards_by_serial(boards)
        return boards_dict

    def see(self):
        pass

