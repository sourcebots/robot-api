import unittest

import time

from robot.robot import Robot
from robot.tests.mock_robotd import MockRobotD


class PowerBoardTest(unittest.TestCase):
    def setUp(self):
        mock = MockRobotD(root_dir="/tmp/")
        self.power_board = mock.new_powerboard()
        time.sleep(0.2)
        self.mock = mock
        self.robot = Robot(robotd_path="/tmp/robotd")

    def test_on_off(self):
        # Got to clear the first message
        _ = self.power_board.message_queue.get()

        self.robot.power_boards[0].power_off()
        msg = self.power_board.message_queue.get()
        self.assertEqual(msg, {'power': False})

        self.robot.power_boards[0].power_on()
        msg = self.power_board.message_queue.get()
        self.assertEqual(msg, {'power': True})

    def tearDown(self):
        self.mock.stop()
