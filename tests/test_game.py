import time
import unittest
from threading import Thread, Event

from robot import corner_script
from robot import Robot
from robot.game import GameMode
from tests.mock_robotd import MockRobotD


class GameTest(unittest.TestCase):
    def setUp(self):
        mock = MockRobotD(root_dir="/tmp/")
        mock.new_powerboard()
        time.sleep(0.2)
        self.mock = mock
        self.robot = Robot(robotd_path="/tmp/robotd")
        self.stop_event = Event()
        self.thread = None

    def test_default_state(self):
        self.mock.new_gamestate()
        time.sleep(0.2)
        self.assertEqual(self.robot.games[0].corner, 0)
        self.assertEqual(self.robot.games[0].mode, GameMode.DEVELOPMENT)

    def test_game_state(self):
        self.mock.new_gamestate()
        corner = 2
        self.thread = Thread(target=corner_script.poll, args=("/tmp/robotd/", corner, self.stop_event))
        time.sleep(0.2)
        # Check before
        self.assertEqual(self.robot.games[0].corner, 0)
        self.assertEqual(self.robot.games[0].mode, GameMode.DEVELOPMENT)
        self.thread.start()
        time.sleep(0.1)
        # Check after
        self.assertEqual(self.robot.games[0].corner, corner)
        self.assertEqual(self.robot.games[0].mode, GameMode.COMPETITION)

    def tearDown(self):
        self.mock.stop()
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join()

