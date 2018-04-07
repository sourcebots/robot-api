import time
import unittest
from pathlib import Path

from robot.power import PowerBoard
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
        board_name = self.power_board.name(self.power_board.node)
        board_path = Path(self.mock.root_dir) / 'power' / board_name

        mock_callable = unittest.mock()
        board = PowerBoard(board_path, on_start_signal=mock_callable)

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

    def tearDown(self):
        self.mock.stop()
