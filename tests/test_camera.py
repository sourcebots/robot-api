import os
import time
import unittest

from robot.camera import ResultList
from robot.markers import CartCoord, PolarCoord, SphericalCoord
from robot.robot import Robot
from sb_vision.camera import FileCamera
from tests.mock_robotd import MockRobotD, MockRobotDFactoryMixin

IMAGE_ROOT = os.path.dirname(os.path.realpath(__file__)) + "/test_data/"
IMAGE_WITH_NO_MARKER = IMAGE_ROOT + 'photo_empty.jpg'
IMAGE_WITH_MARKER = IMAGE_ROOT + 'photo_1.jpg'

CAMERA_SEES_NO_MARKER = FileCamera(IMAGE_WITH_NO_MARKER, 'c270')
CAMERA_SEES_MARKER = FileCamera(IMAGE_WITH_MARKER, 'c270')


class CameraTest(MockRobotDFactoryMixin, unittest.TestCase):
    """
    Tests pertaining to the camera object
    """

    longMessage = True

    # TODO add test for Serial number
    def setUp(self):
        mock = self.create_mock_robotd()
        # Insert a power board to let the robot start up
        self.power_board = mock.new_powerboard()
        time.sleep(0.2)
        self.mock = mock
        self.robot = Robot(robotd_path=mock.root_dir)

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

        self.assertEqual({x.id for x in tokens}, {9}, "Saw wrong markers")

        self.assertEqual(
            9,
            tokens[0].id,
            "Failed to get first marker by index",
        )

        token, = tokens

        self.assertIsInstance(
            token.cartesian,
            CartCoord,
            "Invalid cartesian coordinates",
        )

        self.assertIsInstance(
            token.spherical,
            SphericalCoord,
            "Invalid spherical coordinates",
        )

        self.assertIsInstance(
            token.polar,
            PolarCoord,
            "Invalid polar coordinates",
        )

    def test_unique_error(self):
        self.camera = self.mock.new_camera(CAMERA_SEES_NO_MARKER)
        time.sleep(0.2)
        tokens = self.robot.cameras[0].see()
        with self.assertRaisesRegexp(IndexError, "Trying to index an empty list"):
            tokens[0]


class ResultListTest(unittest.TestCase):
    # Note: these tests deliberately ignore the implementation detail that
    # ``ResultList`` happens to be a subclass of ``list`` and deliberately
    # directly test the common operations which the class will experience --
    # indexing, iteration, length checking and boolishness.

    longMessage = True

    def test_empty(self):
        rl = ResultList([])

        self.assertFalse(rl, "Wrong bool conversion")
        self.assertEqual(0, len(rl), "Wrong length")
        self.assertEqual([], [x for x in rl], "Wrong result from iterating")

        with self.assertRaises(IndexError) as e_info:
            rl[0]

        self.assertEqual(
            "Trying to index an empty list",
            str(e_info.exception),
        )

        with self.assertRaises(IndexError) as e_info:
            rl[1]

        self.assertEqual(
            "Trying to index an empty list",
            str(e_info.exception),
        )

        with self.assertRaises(TypeError):
            rl["0"]

        with self.assertRaises(TypeError):
            rl["spam"]

    def test_one_item(self):
        expected = ["spam"]
        rl = ResultList(expected)

        self.assertTrue(rl, "Wrong bool converstion")
        self.assertEqual(1, len(rl), "Wrong length")
        self.assertEqual(
            expected,
            [x for x in rl],
            "Wrong result from iterating",
        )

        self.assertEqual(expected[0], rl[0], "Wrong value returned at index 0")

        with self.assertRaises(IndexError) as e_info:
            rl[1]

        self.assertEqual(
            "list index out of range",
            str(e_info.exception),
        )

        with self.assertRaises(TypeError):
            rl["0"]

        with self.assertRaises(TypeError):
            rl["spam"]

    def test_two_items(self):
        expected = ["spam", "ham"]
        rl = ResultList(expected)

        self.assertTrue(rl, "Wrong bool converstion")
        self.assertEqual(2, len(rl), "Wrong length")
        self.assertEqual(
            expected,
            [x for x in rl],
            "Wrong result from iterating",
        )

        self.assertEqual(expected[0], rl[0], "Wrong value returned at index 0")
        self.assertEqual(expected[1], rl[1], "Wrong value returned at index 1")

        with self.assertRaises(IndexError):
            rl[2]

        with self.assertRaises(IndexError):
            rl[5]

        with self.assertRaises(TypeError):
            rl["0"]

        with self.assertRaises(TypeError):
            rl["spam"]

    def test_many_items(self):
        expected = ["spam", "ham"] * 3
        rl = ResultList(expected)

        self.assertTrue(rl, "Wrong bool converstion")
        self.assertEqual(6, len(rl), "Wrong length")
        self.assertEqual(
            expected,
            [x for x in rl],
            "Wrong result from iterating",
        )

        self.assertEqual(expected[0], rl[0], "Wrong value returned at index 0")
        self.assertEqual(expected[1], rl[1], "Wrong value returned at index 1")
        self.assertEqual(expected[2], rl[2], "Wrong value returned at index 2")
        self.assertEqual(expected[3], rl[3], "Wrong value returned at index 3")
        self.assertEqual(expected[4], rl[4], "Wrong value returned at index 4")
        self.assertEqual(expected[5], rl[5], "Wrong value returned at index 5")

        with self.assertRaises(IndexError):
            rl[6]

        with self.assertRaises(TypeError):
            rl["0"]

        with self.assertRaises(TypeError):
            rl["spam"]
