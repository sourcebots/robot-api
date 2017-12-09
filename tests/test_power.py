import unittest

import time

from robot.robot import Robot
from tests.mock_robotd import MockRobotD


class PowerBoardTest(unittest.TestCase):
    def setUp(self):
        mock = MockRobotD(root_dir="/tmp/robotd")
        self.power_board = mock.new_powerboard()
        time.sleep(0.2)
        self.mock = mock
        self.robot = Robot(robotd_path="/tmp/robotd")

    def test_on_off(self):
        # power board switch on when booting
        msg = self.power_board.message_queue.get()
        self.assertIn('power', msg)
        self.assertEqual(msg['power'], True)

        # Catch the start led turning on
        msg = self.power_board.message_queue.get()
        self.assertIn('start-led', msg)
        self.assertEqual(msg['start-led'], True)

        # Catch the start led turning off
        msg = self.power_board.message_queue.get()
        self.assertIn('start-led', msg)
        self.assertEqual(msg['start-led'], False)

        self.robot.power_boards[0].power_off()
        msg = self.power_board.message_queue.get()
        self.assertEqual(msg['power'], False)

        self.robot.power_boards[0].power_on()
        msg = self.power_board.message_queue.get()
        self.assertEqual(msg['power'], True)

    def test_insert_power(self):
        # TODO: Make this generic for all boards, instead of duplicated logic
        self.mock.new_powerboard('ABC')
        self.mock.new_powerboard('DEF')
        # Give it a tiny bit to init the boards
        time.sleep(0.4)

        boards = self.robot.power_boards

        # Check all the motor boards are initialised and can be indexed
        self.assertTrue(0 in boards)
        self.assertTrue(1 in boards)
        self.assertTrue(2 in boards)
        self.assertTrue('ABC' in boards)
        self.assertTrue('DEF' in boards)

    def test_remove_board(self):
        # TODO: Make this generic for all boards
        # Add and remove a board
        pb = self.mock.new_powerboard('ABC')
        self.mock.remove_board(pb)
        # check the new board has gone
        self.assertTrue('ABC' not in self.robot.power_boards)

    def tearDown(self):
        self.mock.stop()
