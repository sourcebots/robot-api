import time
import unittest

from robot import COAST
from robot.robot import Robot
from tests.mock_robotd import MockRobotDFactoryMixin


class MotorBoardTest(MockRobotDFactoryMixin, unittest.TestCase):
    def setUp(self):
        mock = self.create_mock_robotd()
        mock.new_powerboard()
        time.sleep(0.2)
        self.mock = mock
        self.robot = Robot(robotd_path=mock.root_dir, wait_for_start_button=False)

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
            board.m0 = 1

        # Re-add it
        self.mock.new_motorboard('ABC')
        time.sleep(0.2)

        board.m0 = 1

    def test_two_clients(self):
        """ Checks you can interface a motor board multiple times"""
        # TODO make this test generic to the board, so it runs on all boards.
        self.mock.new_motorboard('ABC')
        # Set up robot 2!
        robot2 = Robot(robotd_path=self.mock.root_dir, wait_for_start_button=False)
        # Give it a tiny bit to init the boards
        time.sleep(0.2)
        self.robot.motor_boards[0].m0 = 1
        self.robot.motor_boards[0].m0 = -1
        robot2.motor_boards[0].m0 = 1
        robot2.motor_boards[0].m0 = -1

    def test_multiple_indexes(self):
        """ Checks you can index motor boards plenty of times"""
        self.mock.new_motorboard('ABC')
        # Give it a tiny bit to init the boards
        time.sleep(0.2)

        # Check all the motor boards are initialised and can be indexed
        for i in range(10):
            self.assertTrue(0 in self.robot.motor_boards)

    def test_set_edge_conditions(self):
        board = self.mock.new_motorboard()
        time.sleep(0.2)
        for motor in ['m0', 'm1']:
            self._try_power(motor, board, 1.0)
            self._try_power(motor, board, 1)
            self._try_power(motor, board, 0.002)
            self._try_power(motor, board, -1)
            # Invalid error
            with self.assertRaises(ValueError):
                self._try_power(motor, board, -1.01)
            # Brake and coast
            self._try_power(motor, board, COAST)
            # 0 should be BRAKE
            self._try_power_expect(motor, board, 0, 'brake')

    def _try_power(self, motor, board, value):
        self._try_power_expect(motor, board, value, value)

    def _try_power_expect(self, motor, board, value, expect):
        if motor == 'm0':
            self.robot.motor_boards[0].m0 = value
        elif motor == 'm1':
            self.robot.motor_boards[0].m1 = value
        else:
            raise ValueError()
        got_value = board.message_queue.get()
        # Test the motor board got what it expected
        self.assertEqual(got_value, {motor: expect})
        # Test the value can be read
        if motor == 'm0':
            self.assertEqual(self.robot.motor_boards[0].m0, value)
        elif motor == 'm1':
            self.assertEqual(self.robot.motor_boards[0].m1, value)
        else:
            raise ValueError()
