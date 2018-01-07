import os
import time
import unittest

from robot.robot import Robot
from sb_vision.camera import FileCamera
from tests.mock_robotd import MockRobotD

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

    def test_insert_cameras(self):
        self.mock.new_camera(CAMERA_SEES_NO_MARKER, 'ABC')
        self.mock.new_camera(CAMERA_SEES_NO_MARKER, 'DEF')
        # Give it a tiny bit to init the boards
        time.sleep(0.4)

        boards = self.robot.cameras

        # Check all the motor boards are initialised and can be indexed
        self.assertTrue(0 in boards)
        self.assertTrue(1 in boards)
        self.assertTrue('ABC' in boards)
        self.assertTrue('DEF' in boards)

    def test_cant_see_anything(self):
        self.camera = self.mock.new_camera(CAMERA_SEES_NO_MARKER)
        time.sleep(0.2)
        tokens = self.robot.cameras[0].see()
        self.assertEqual(tokens, [])

    def test_can_see_something(self):
        self.camera = self.mock.new_camera(CAMERA_SEES_MARKER)
        time.sleep(0.2)
        camera = self.robot.cameras[0]
        tokens = camera.see()

        # Check the correct markers are spotted
        self.assertEqual({x.id for x in tokens}, {9})

    def test_unique_error(self):
        self.camera = self.mock.new_camera(CAMERA_SEES_NO_MARKER)
        time.sleep(0.2)
        tokens = self.robot.cameras[0].see()
        with self.assertRaisesRegexp(IndexError, "Trying to index an empty list"):
            tokens[0]

    def tearDown(self):
        self.mock.stop()
