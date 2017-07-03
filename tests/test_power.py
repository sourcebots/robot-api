import unittest

import time

from robot.robot import Robot
from robot.tests.mock_robotd import MockRobotD


class PowerBoardTest(unittest.TestCase):
    def setUp(self):
        mock = MockRobotD(root_dir="/tmp/")
        mock.new_powerboard()
        time.sleep(0.1)
        self.mock = mock
        self.robot = Robot(robotd_path="/tmp/robotd")

    def test_insert_motorboards(self):
        # Give it a tiny bit to init the boards
        time.sleep(0.4)

        boards = self.robot.power_boards

        # Check all the motor boards are initialised and can be indexed
        self.assertTrue(0 in boards)

    def tearDown(self):
        self.mock.stop()

