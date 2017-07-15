import unittest

import time

from robot.robot import Robot
from robot import COAST, BRAKE
from robot.tests.mock_robotd import MockRobotD


class MotorBoardTest(unittest.TestCase):
    def setUp(self):
        mock = MockRobotD(root_dir="/tmp/")
        mock.new_powerboard()
        time.sleep(0.2)
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

    def test_remove_motorboard_recovery(self):
        mock_motor = self.mock.new_motorboard('ABC')
        # Give it a tiny bit to init the boards
        time.sleep(0.4)

        boards = self.robot.motor_boards

        # Get the board
        board = boards[0]
        self.mock.remove_board(mock_motor)
        with self.assertRaises(ConnectionError):
            board.m0.voltage = 1

        # Re-add it
        self.mock.new_motorboard('ABC')
        time.sleep(0.2)

        board.m0.voltage = 1

    def test_multiple_indexes(self):
        """ Checks you can index motor boards plenty of times"""
        self.mock.new_motorboard('ABC')
        # Give it a tiny bit to init the boards
        time.sleep(0.2)

        # Check all the motor boards are initialised and can be indexed
        for i in range(10):
            self.assertTrue(0 in self.robot.motor_boards)
            print("connection", i)

    def _try_voltage(self, motor, board, value):
        self._try_voltage_expect(motor, board, value, value)

    def _try_voltage_expect(self, motor, board, value, expect):
        if motor == 'm0':
            self.robot.motor_boards[0].m0.voltage = value
        elif motor == 'm1':
            self.robot.motor_boards[0].m1.voltage = value
        got_value = board.message_queue.get()
        self.assertEqual(got_value, {motor: expect})

    def test_set_edge_conditions(self):
        board = self.mock.new_motorboard()
        time.sleep(0.2)
        for motor in ['m0', 'm1']:
            self._try_voltage(motor, board, 1.0)
            self._try_voltage(motor, board, 1)
            self._try_voltage(motor, board, 0.002)
            self._try_voltage(motor, board, -1)
            # Invalid error
            with self.assertRaises(ValueError):
                self._try_voltage(motor, board, -1.01)
            # Brake and coast
            self._try_voltage(motor, board, COAST)
            self._try_voltage(motor, board, BRAKE)
            # 0 should be BRAKE
            self._try_voltage_expect(motor, board, 0, BRAKE)

    def tearDown(self):
        self.mock.stop()
