import os
import unittest

import time

from robotd.game_specific import MARKER_SIZES as MARKER_SIZES_ROBOTD
from robot.robot import Robot
from tests.mock_robotd import MockRobotD
from robotd.vision.camera import FileCamera


class CameraTest(unittest.TestCase):
    """
    Tests pertaining to the camera object
    """
    # TODO add test for Serial number
    def setUp(self):
        mock = MockRobotD(root_dir="/tmp/")
        # Insert a power board to let the robot start up
        self.power_board = mock.new_powerboard()
        time.sleep(0.2)
        self.mock = mock
        self.robot = Robot(robotd_path="/tmp/robotd")
        self.image_root = os.path.dirname(os.path.realpath(__file__))

    def test_insert_cameras(self):
        self.mock.new_camera('ABC')
        self.mock.new_camera('DEF')
        # Give it a tiny bit to init the boards
        time.sleep(0.4)

        boards = self.robot.cameras

        # Check all the motor boards are initialised and can be indexed
        self.assertTrue(0 in boards)
        self.assertTrue(1 in boards)
        self.assertTrue('ABC' in boards)
        self.assertTrue('DEF' in boards)

    def test_cant_see_anything(self):
        self.camera = self.mock.new_camera()
        time.sleep(0.2)
        tokens = self.robot.cameras[0].see()
        self.assertEqual(tokens, [])

    def test_can_see_something(self):
        self.camera = self.mock.new_camera(camera=FileCamera(self.image_root + '/tagsampler.png', 720))
        time.sleep(0.2)
        camera = self.robot.cameras[0]
        tokens = camera.see()

        # Check the correct markers are spotted
        self.assertEqual({x.id for x in tokens}, {0, 1, 24, 25})

    def test_marker_sizes(self):
        # Change the marker sizes value in both robotd and robot-api
        written_sizes = {0: (0.9, 0.9), 1: (0.9, 0.9), 24: (0.2, 0.2), 25: (0.2, 0.2)}
        MARKER_SIZES_ROBOTD.update(written_sizes)
        self.camera = self.mock.new_camera(camera=FileCamera(self.image_root + '/tagsampler.png', 720))
        time.sleep(0.2)
        camera = self.robot.cameras[0]
        tokens = camera.see()

        # Check the correct sizes are read
        read_sizes = {x.id:x.size for x in tokens}
        self.assertEqual(written_sizes, read_sizes)

    def test_unique_error(self):
        self.camera = self.mock.new_camera()
        time.sleep(0.2)
        tokens = self.robot.cameras[0].see()
        with self.assertRaises(IndexError):
            _ = tokens[0]
        try:
            _ = tokens[0]
        except IndexError as e:
            self.assertEqual(str(e), "Trying to index an empty list")

    def tearDown(self):
        self.mock.stop()
