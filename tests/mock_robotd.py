import time
from multiprocessing import Queue

import robot

from robotd.devices import Camera as RobotDCamera
from robotd.devices import GameState as RobotDGameState
from robotd.devices_base import Board
from robotd.master import BoardRunner


class MockBoardMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_queue = Queue()

    def clear_queue(self):
        while not self.message_queue.empty():
            self.message_queue.get()

    @classmethod
    def name(cls, node):
        """Board name - actually fetched over serial."""
        return node['name']

    def status(self):
        return self._status

    def command(self, cmd):
        print("{} Command: {}".format(self._name, cmd))
        self._status.update(cmd)
        self.message_queue.put(cmd)


class MockRobotD:
    DEFAULT_ROOT_DIR = "/var/"

    def __init__(self, root_dir=DEFAULT_ROOT_DIR):
        self.root_dir = root_dir
        self.runners = []
        self.board_to_runner = {}

    def new_board(self, board_class, name, *args):
        # Enter a blank node
        board = board_class(name, {'name': name}, *args)
        runner = BoardRunner(board, self.root_dir)
        self.board_to_runner[board] = runner
        self.runners.append(runner)
        runner.start()
        return board

    def new_powerboard(self, name=None):
        if not name:
            name = "MOCK{}".format(len(self.runners))
        return self.new_board(MockPowerBoard, name)

    def new_motorboard(self, name=None):
        if not name:
            name = "MOCK{}".format(len(self.runners))
        return self.new_board(MockMotorBoard, name)

    def new_servoboard(self, name=None):
        if not name:
            name = "MOCK{}".format(len(self.runners))
        return self.new_board(MockServoAssembly, name)

    def new_camera(self, camera, name=None):
        if not name:
            name = "MOCK{}".format(len(self.runners))
        return self.new_board(MockCamera, name, camera)

    def new_gamestate(self, name="serial"):
        return self.new_board(MockGameState, name)

    def remove_board(self, board):
        runner = self.board_to_runner[board]
        runner.terminate()
        runner.join()
        runner.cleanup()

    def stop(self):
        for runner in self.runners:
            runner.terminate()
            runner.join()
            runner.cleanup()


class MockMotorBoard(MockBoardMixin, Board):
    """
    Mock class for simulating a motor board
    """
    board_type_id = 'motor'

    def __init__(self, name, node):
        super().__init__(node)
        self._name = name
        self._status = {'m0': robot.BRAKE, 'm1': robot.COAST}


class MockServoAssembly(MockBoardMixin, Board):
    """
    Mock class for simulating a servo board
    """
    board_type_id = 'servo_assembly'

    def __init__(self, name, node):
        super().__init__(node)
        self._name = name
        self._status = {
            'servos': {x: None for x in range(16)},
            'pins': {x: 'input' for x in range(2, 13)},
        }
        self.message_queue = Queue()


class MockPowerBoard(MockBoardMixin, Board):
    """
    Mock class for simulating a power board with a button
    """
    board_type_id = 'power'

    def __init__(self, name, node):
        super().__init__(node)
        self._name = name
        self.message_queue = Queue()
        self._status = {'start-button': True}


class MockCamera(RobotDCamera):
    board_type_id = 'camera'

    def __init__(self, name, node, camera):
        node['DEVNAME'] = name
        self.serial = name
        # Create a camera with a file camera instead of a real camera
        super().__init__(node, camera)


class MockGameState(RobotDGameState):
    board_type_id = 'game'

    def __init__(self, name, node):
        super().__init__()
        self._serial = name


def main():
    mock = MockRobotD(root_dir='/tmp/robotd')

    mock.new_powerboard()
    time.sleep(0.2)

    mock.new_motorboard()
    time.sleep(0.2)

    from robot.robot import Robot
    robot = Robot(robotd_path='/tmp/robotd')
    robot.power_board.power_off()
    m0 = robot.motor_boards[0].m0
    m0.voltage = 1


if __name__ == "__main__":
    main()
