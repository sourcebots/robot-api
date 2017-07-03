import socket
from pathlib import Path

from robot.motor import MotorBoard


class Robot:
    """
    Robot API
    - Speaks to robotd over unix socket
    - Always grabs from sockets, avoids caching
    """

    ROBOTD_ADDRESS = "/var/robotd"

    def __init__(self, robotd_path=ROBOTD_ADDRESS):
        self.robotd_path = Path(robotd_path)

    def _motor_board_dict_gen(self, boards):
        return {i: x for i, x in enumerate(boards)}.update(
            {x.serial: x for x in enumerate(boards)}
        )

    @property
    def motor_boards(self):
        boards = []
        motors_dir = self.robotd_path / "motor"
        for motor_sock in motors_dir.glob('*'):
            boards.append(MotorBoard(str(motor_sock)))

        # Convert array of boards into a dictionary
        boards_dict = {}
        for i, board in enumerate(boards):
            boards_dict[i] = board
            boards_dict[board.serial] = board
        return boards_dict

    def see(self):
        pass


class ServoBoard:
    def __init__(self):
        pass
