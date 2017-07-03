import unittest

import time

from robot.robot import Robot
from robot.tests.mock_robotd import MockRobotD


class MotorBoardTest(unittest.TestCase):
    def setUp(self):
        mock = MockRobotD(root_dir="/tmp/")
        self.mock = mock
        self.robot = Robot(robotd_path="/tmp/robotd")

    def test_insert_motorboards(self):
        self.mock.new_motorboard('ABC')
        self.mock.new_motorboard('DEF')
        # Give it a tiny bit to init the boards
        time.sleep(0.4)

        boards = self.robot.motor_boards

        # Check all the motor boards are initialised and can be indexed
        self.assertTrue(0 in boards)
        self.assertTrue(1 in boards)
        self.assertTrue('ABC' in boards)
        self.assertTrue('DEF' in boards)

    def tearDown(self):
        self.mock.stop()

