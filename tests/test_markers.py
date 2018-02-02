import math
import unittest

from robot.markers import Metres, Radians, SphericalCoord


class SphericalCoordTest(unittest.TestCase):
    def test_conversion_to_degrees(self):
        coords = SphericalCoord(
            rot_x_radians=Radians(math.pi / 2),
            rot_y_radians=Radians(-math.pi / 4),
            dist=Metres(1),
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
