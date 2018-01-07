import time
import unittest

from robot import PinMode
from robot.robot import Robot
from tests.mock_robotd import MockRobotD


class GPIOTest(unittest.TestCase):
    def setUp(self):
        mock = MockRobotD(root_dir="/tmp/robotd")
        mock.new_powerboard()
        time.sleep(0.2)
        self.mock = mock
        self.robot = Robot(robotd_path="/tmp/robotd")

    def test_set_edge_conditions(self):
        board = self.mock.new_servoboard()
        time.sleep(0.2)
        for gpio in range(2,13):
            for mode in [PinMode.INPUT, PinMode.INPUT_PULLUP, PinMode.OUTPUT_HIGH, PinMode.OUTPUT_LOW]:
                self._try_mode(gpio, board, mode)
            # Invalid error
            with self.assertRaises(ValueError):
                self._try_mode(gpio, board, "Hi")

    def _try_mode(self, motor, board, value):
        self._try_mode_expect(motor, board, value, value)

    def _try_mode_expect(self, gpio, board, value, expect):
        self.robot.servo_boards[0].gpios[gpio].mode = value
        got_value = board.message_queue.get()
        # Test the motor board got what it expected
        self.assertEqual(got_value, {'pins': {str(gpio): expect.value}})
        # Test the value can be read
        self.assertEqual(self.robot.servo_boards[0].gpios[gpio].mode, value)

    def tearDown(self):
        self.mock.stop()
