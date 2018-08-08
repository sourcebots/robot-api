import time
import unittest
from unittest import mock

from robot.power import PowerBoard, PowerOutput
from robot.robot import Robot
from tests.mock_robotd import MockRobotDFactoryMixin


class PowerBoardTest(MockRobotDFactoryMixin, unittest.TestCase):
    def setUp(self):
        mock = self.create_mock_robotd()
        self.power_board = mock.new_powerboard()
        time.sleep(0.2)
        self.mock = mock
        self.robot = Robot(robotd_path=mock.root_dir, wait_for_start_button=False)

    def test_on_off(self):
        # power board switch on when booting
        msg = self.power_board.message_queue.get()
        self.assertIn('power', msg)
        self.assertEqual(msg['power'], True)

        self.power_board.clear_queue()
        self.robot.power_boards[0].power_off()
        msg = self.power_board.message_queue.get()
        self.assertEqual(msg['power'], False)

        self.robot.power_boards[0].power_on()
        msg = self.power_board.message_queue.get()
        self.assertEqual(msg['power'], True)

    def test_start_button_pressed(self):
        self.assertTrue(self.robot.power_board.start_button_pressed)

    def test_set_start_led(self):
        self.power_board.clear_queue()
        self.robot.power_board.set_start_led(True)
        msg = self.power_board.message_queue.get()
        self.assertEqual(msg['start-led'], True)

        self.robot.power_board.set_start_led(False)
        msg = self.power_board.message_queue.get()
        self.assertFalse(msg['start-led'])

    def test_wait_start(self):
        mock_callable = mock.Mock()
        board = PowerBoard(
            self.board_path(self.power_board),
            on_start_signal=mock_callable,
        )

        self.power_board.clear_queue()

        # this is the action we're testing
        board.wait_start()

        msg = self.power_board.message_queue.get()
        self.assertFalse(
            msg['start-led'],
            "Start LED should be off after wait_start returns",
        )

        # Check that our callable was called
        mock_callable.assert_called_once_with()

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

    def test_buzz_args(self):
        with self.assertRaises(ValueError):
            self.robot.power_board.buzz(1, note='c', frequency=100)

        with self.assertRaises(ValueError):
            self.robot.power_board.buzz(1)

        with self.assertRaises(TypeError):
            self.robot.power_board.buzz(1, 'c')

        with self.assertRaises(TypeError):
            self.robot.power_board.buzz(1, 'c', 100)

    def test_note_case(self):
        with self.assertRaises(KeyError):
            self.robot.power_board.buzz(1, note='J')

        with self.assertRaises(KeyError):
            self.robot.power_board.buzz(1, note='j')

        self.robot.power_board.buzz(1, note='c')
        self.robot.power_board.buzz(1, note='C')

    def test_buzz_message(self):
        self.power_board.clear_queue()
        self.robot.power_board.buzz(1, note='c')
        msg = self.power_board.message_queue.get()
        self.assertIn('buzz', msg)
        self.assertEqual(msg['buzz'], {
            'frequency': 261,
            'duration': 1000,
        })

        self.robot.power_board.buzz(4, frequency=200)
        msg = self.power_board.message_queue.get()
        self.assertIn('buzz', msg)
        self.assertEqual(msg['buzz'], {
            'frequency': 200,
            'duration': 4000,
        })

    def test_fractional_buzz_duration(self):
        self.power_board.clear_queue()
        self.robot.power_board.buzz(0.5, note='c')
        msg = self.power_board.message_queue.get()
        self.assertIn('buzz', msg)
        self.assertEqual(msg['buzz'], {
            'frequency': 261,
            'duration': 500,
        })
        self.assertIsInstance(msg['buzz']['duration'], int)

    def test_separate_power_on(self):
        self.power_board.clear_queue()
        self.robot.power_board.power_on_output(PowerOutput.H1)
        msg = self.power_board.message_queue.get()
        self.assertIn('power-output', msg)
        self.assertIn('power-level', msg)
        self.assertEqual(msg['power-output'], 1)
        self.assertEqual(msg['power-level'], True)

    def test_separate_power_off(self):
        self.power_board.clear_queue()
        self.robot.power_board.power_off_output(PowerOutput.H1)
        msg = self.power_board.message_queue.get()
        self.assertIn('power-output', msg)
        self.assertIn('power-level', msg)
        self.assertEqual(msg['power-output'], 1)
        self.assertEqual(msg['power-level'], False)
