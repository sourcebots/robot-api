import unittest

import time

from robot.robot import Robot
from robot import COAST, BRAKE
from tests.mock_robotd import MockRobotD


class ServoBoardTest(unittest.TestCase):
    def setUp(self):
        mock = MockRobotD(root_dir="/tmp/robotd")
        mock.new_powerboard()
        time.sleep(0.2)
        self.mock = mock
        self.robot = Robot(robotd_path="/tmp/robotd")

    def test_insert_servoboards(self):
        self.mock.new_servoboard('ABC')
        self.mock.new_servoboard('DEF')
        # Give it a tiny bit to init the boards
        time.sleep(0.4)

        boards = self.robot.servo_boards

        # Check all the motor boards are initialised and can be indexed
        self.assertTrue(0 in boards)
        self.assertTrue(1 in boards)
        self.assertTrue('ABC' in boards)
        self.assertTrue('DEF' in boards)

    def test_remove_servoboard_recovery(self):
        mock_servo = self.mock.new_servoboard('ABC')
        # Give it a tiny bit to init the boards
        time.sleep(0.4)

        boards = self.robot.servo_boards

        # Get the board
        board = boards[0]
        self.mock.remove_board(mock_servo)
        with self.assertRaises(ConnectionError):
            board.ports[0].position = 1

        # Re-add it
        self.mock.new_servoboard('ABC')
        time.sleep(0.2)

        board.ports[0].position = 1

    def test_multiple_indexes(self):
        """ Checks you can index servo boards plenty of times"""
        self.mock.new_servoboard('ABC')
        # Give it a tiny bit to init the boards
        time.sleep(0.2)

        # Check all the motor boards are initialised and can be indexed
        for i in range(10):
            self.assertTrue(0 in self.robot.servo_boards)

    def test_set_edge_conditions(self):
        board = self.mock.new_servoboard()
        time.sleep(0.2)
        for servo in range(16):
            for pos in [1.0, 1, 0.002, -1]:
                self._try_position(servo, board, pos)
            # Invalid error
            with self.assertRaises(ValueError):
                self._try_position(servo, board, -1.01)

    def _try_position(self, motor, board, value):
        self._try_position_expect(motor, board, value, value)

    def _try_position_expect(self, servo, board, value, expect):
        self.robot.servo_boards[0].ports[servo].position = value
        got_value = board.message_queue.get()
        # Test the motor board got what it expected
        self.assertEqual(got_value, {str(servo): expect})
        # Test the value can be read
        self.assertEqual(self.robot.servo_boards[0].ports[servo].position, value)

    def tearDown(self):
        self.mock.stop()
