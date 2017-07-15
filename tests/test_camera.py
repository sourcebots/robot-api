import unittest

import time

from robot.robot import Robot
from robot.tests.mock_robotd import MockRobotD
from robotd.vision.camera import FileCamera


class CameraTest(unittest.TestCase):
    """
    Tests pertaining to the camera object
    """

    def setUp(self):
        mock = MockRobotD(root_dir="/tmp/")
        # Insert a power board to let the robot start up
        self.power_board = mock.new_powerboard()
        time.sleep(0.2)
        self.mock = mock
        self.robot = Robot(robotd_path="/tmp/robotd")

    def test_cant_see_anything(self):
        self.camera = self.mock.new_camera()
        time.sleep(0.2)
        tokens = self.robot.cameras[0].see()
        self.assertEqual(tokens, [])

    def test_can_see_something(self):
        self.camera = self.mock.new_camera(camera=FileCamera('tagsampler.png', 720))
        time.sleep(0.2)
        camera = self.robot.cameras[0]
        tokens = camera.see()
        print([t for t in tokens])

    def tearDown(self):
        self.mock.stop()
