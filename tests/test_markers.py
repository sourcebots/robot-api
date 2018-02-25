import math
import unittest

from robot.markers import Metres, Radians, SphericalCoord, Marker


class SphericalCoordTest(unittest.TestCase):
    def test_conversion_to_degrees(self):
        coords = SphericalCoord(
            rot_x_radians=Radians(math.pi / 2),
            rot_y_radians=Radians(-math.pi / 4),
            distance_metres=Metres(1),
        )

        self.assertEqual(
            90,
            coords.rot_x_degrees,
            "Wrong x rotation",
        )

        self.assertEqual(
            -45,
            coords.rot_y_degrees,
            "Wrong y rotation",
        )


class MarkerTest(unittest.TestCase):
    def test_str_left(self):
        data = {
            'id': 13,
            'spherical': [
                0,  # rot_x
                -0.21467549799530256,  # rot_y, -12.3 degrees
                0.12,  # distance
            ],
        }
        self.assertEqual(
            str(Marker(data)),
            "<Marker 13: 12° left, 0.12m away>",
        )

    def test_str_right(self):
        data = {
            'id': 13,
            'spherical': [
                0,  # rot_x
                0.21467549799530256,  # rot_y, 12.3 degrees
                0.12,  # distance
            ],
        }
        self.assertEqual(
            str(Marker(data)),
            "<Marker 13: 12° right, 0.12m away>",
        )
