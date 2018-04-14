import time
import unittest
from unittest import mock

from robot import game_specific
from robot.board import Board
from robot.robot import Robot
from tests.mock_robotd import MockRobotDFactoryMixin


class RobotTest(MockRobotDFactoryMixin, unittest.TestCase):
    def mock_kill_after_delay(self):
        return mock.patch('robot.robot.kill_after_delay')

    def set_competition_mode(self):
        board = Board(self.board_path(self.game_state))
        board._send_and_receive({'mode': 'competition'})

    def setUp(self):
        mock = self.create_mock_robotd()
        self.power_board = mock.new_powerboard()
        self.game_state = mock.new_gamestate()
        time.sleep(0.2)
        self.mock = mock

    def test_explicit_wait_start_development_mode(self):
        robot = Robot(
            robotd_path=self.mock.root_dir,
            wait_for_start_button=False,
        )

        with self.mock_kill_after_delay() as mock_kill_after_delay:
            robot.power_board.wait_start()

            # default is development mode, which doesn't have a timeout
            mock_kill_after_delay.assert_not_called()

    def test_explicit_wait_start_competition_mode(self):
        robot = Robot(
            robotd_path=self.mock.root_dir,
            wait_for_start_button=False,
        )

        self.set_competition_mode()

        with self.mock_kill_after_delay() as mock_kill_after_delay:
            robot.power_board.wait_start()

            mock_kill_after_delay.assert_called_once_with(
                game_specific.GAME_DURATION_SECONDS,
            )

    def test_implicit_wait_start_development_mode(self):
        with self.mock_kill_after_delay() as mock_kill_after_delay:
            Robot(robotd_path=self.mock.root_dir)

            # default is development mode, which doesn't have a timeout
            mock_kill_after_delay.assert_not_called()

    def test_implicit_wait_start_competition_mode(self):
        self.set_competition_mode()

        with self.mock_kill_after_delay() as mock_kill_after_delay:
            Robot(robotd_path=self.mock.root_dir)

            mock_kill_after_delay.assert_called_once_with(
                game_specific.GAME_DURATION_SECONDS,
            )
