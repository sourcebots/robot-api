import time

import robot
from robotd.devices_base import Board
from robotd.master import BoardRunner


class MockRobotD:
    DEFAULT_ROOT_DIR = "/var/"

    def __init__(self, root_dir=DEFAULT_ROOT_DIR):
        self.root_dir = root_dir
        self.motor_boards = []
        self.runners = []

    def new_motorboard(self, name=None):
        if not name:
            name = "MOCK{}".format(len(self.motor_boards))
        self.motor_boards.append(name)
        # Enter a blank node
        runner = BoardRunner(MockMotorBoard(name, {'name': name}), self.root_dir)
        runner.start()
        self.runners.append(runner)

    def stop(self):
        for runner in self.runners:
            runner.terminate()
            runner.join()
            runner.cleanup_socket()


class MockMotorBoard(Board):
    """
    Mock class for simulating a motor board
    """
    board_type_id = 'motor'

    def __init__(self, name, node):
        super().__init__(node)
        self._name = name
        self.left = robot.BRAKE
        self.right = robot.BRAKE

    @classmethod
    def name(cls, node):
        """Board name - actually fetched over serial."""
        return node['name']

    def command(self, cmd):
        print("{} Command: {}".format(self._name, cmd))


def main():
    mock = MockRobotD(root_dir="/tmp/")
    mock.new_motorboard()
    # Give it a tiny bit to init the boards
    time.sleep(0.1)
    from robot.robot import Robot
    robot = Robot(robotd_path="/tmp/robotd")
    m0 = robot.motor_boards[0].m0
    m0.voltage = 1


if __name__ == "__main__":
    main()
