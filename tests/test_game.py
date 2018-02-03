import time
import unittest

from robot import Robot
from robot.game import GameMode
from tests.mock_robotd import MockRobotD, create_root_dir, remove_root_dir


class GameTest(unittest.TestCase):
    def setUp(self):
        self.root_dir = create_root_dir()
        mock = MockRobotD(root_dir=self.root_dir)
        mock.new_powerboard()
        time.sleep(0.2)
        self.mock = mock
        self.robot = Robot(robotd_path=self.root_dir)

    def test_default_state(self):
        self.mock.new_gamestate()
        time.sleep(0.2)
        self.assertEqual(self.robot.zone, 0)
        self.assertEqual(self.robot.mode, GameMode.DEVELOPMENT)

    def tearDown(self):
        self.mock.stop()
        remove_root_dir(self.root_dir)
