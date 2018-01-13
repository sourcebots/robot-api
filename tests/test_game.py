import time
import unittest

from robot import Robot
from robot.game import GameMode
from tests.mock_robotd import MockRobotD


class GameTest(unittest.TestCase):
    def setUp(self):
        mock = MockRobotD(root_dir="/tmp/robotd")
        mock.new_powerboard()
        time.sleep(0.2)
        self.mock = mock
        self.robot = Robot(robotd_path="/tmp/robotd")

    def test_default_state(self):
        self.mock.new_gamestate()
        time.sleep(0.2)
        self.assertEqual(self.robot.zone, 0)
        self.assertEqual(self.robot.mode, GameMode.DEVELOPMENT)

    def tearDown(self):
        self.mock.stop()
