import os
import unittest

import time

from robotd.game_specific import MARKER_SIZES as MARKER_SIZES_ROBOTD
from robot.robot import Robot
from tests.mock_robotd import MockRobotD
from sb_vision.camera import FileCamera

IMAGE_ROOT = os.path.dirname(os.path.realpath(__file__)) + "/test_data/"
IMAGE_WITH_NO_MARKER = IMAGE_ROOT + 'photo_empty.jpg'
IMAGE_WITH_MARKER = IMAGE_ROOT + 'photo_1.jpg'

CAMERA_SEES_NO_MARKER = FileCamera(IMAGE_WITH_NO_MARKER, 'c270')
CAMERA_SEES_MARKER = FileCamera(IMAGE_WITH_MARKER, 'c270')


class CameraTest(unittest.TestCase):
    """
    Tests pertaining to the camera object
    """

    # TODO add test for Serial number
    def setUp(self):
        mock = MockRobotD(root_dir="/tmp/robotd")
        # Insert a power board to let the robot start up
        self.power_board = mock.new_powerboard()
        time.sleep(0.2)
        self.mock = mock
        self.robot = Robot(robotd_path="/tmp/robotd")

    def tearDown(self):
        self.mock.stop()
