import math
from collections import namedtuple
from robot.game_specific import WALL, TOKEN
from typing import Tuple


CartCoord = namedtuple("CardCoord", ["x", "y", "z"])


class PolarCoord:
    """
    Represents a polar co-ordinate point
    """

    def __init__(self, rot, dist_m):
        self._rot_x_rad = rot[0]
        self._rot_y_rad = rot[1]
        self._distance_metres = dist_m

    # TODO add tests for all these
    @property
    def rot_x_rad(self) -> float:
        """
        Rotation of marker relative to camera in the #TODO axis
        (axis is in the location of the camera)
        """
        return self._rot_x_rad

    @property
    def rot_y_rad(self) -> float:
        """
        Rotation of marker relative to camera in the #TODO axis
        (axis is in the location of the camera)
        """
        return self._rot_y_rad


    @property
    def rot_x_deg(self) -> float:
        """
        Rotation of marker relative to camera in the #TODO axis.
        (axis is in the location of the camera)
        """
        # TODO describe which axis this is
        return math.degrees(self._rot_x_rad)

    @property
    def rot_y_deg(self) -> float:
        """
        Rotation of marker relative to camera in the #TODO axis.
        (axis is in the location of the camera)
        """
        # TODO describe which axis this is
        return math.degrees(self._rot_y_rad)

    @property
    def distance_metres(self) -> float:
        """
        Distance of marker from camera in Metres
        """
        # TODO describe which axis this is
        return self._distance_metres


class Marker:
    """
    Class that represents a marker captured from a webcam image
    """

    def __init__(self, data):
        self._raw_data = data

    @property
    def id(self) -> int:
        """ID of the marker seen"""
        return self._raw_data['id']

    @property
    def size(self) -> Tuple:
        """Marker size in metres"""
        return tuple(self._raw_data['size'])

    # Disabled because it's always 0.0
    # TODO fix the certainty being 0
    # @property
    # def certainty(self):
    #     return self._certainty

    @property
    def pixel_corners(self):
        """Pixel co-ordinates of the of the corners of the marker"""
        # TODO define what the order of these corners are
        return [tuple(x) for x in self._raw_data['pixel_corners']]

    @property
    def pixel_centre(self):
        """Pixel co-ordinates of the centre of the marker"""
        return tuple(self._raw_data['pixel_centre'])

    # Helper functions, Might need to vary these per-game

    def is_wall_marker(self) -> bool:
        """ If the marker is a wall marker """
        return self.id in WALL

    def is_token_marker(self) -> bool:
        """ If the marker is a token marker """
        return self.id in TOKEN

    @property
    def cartesian(self):
        raise NotImplementedError("This is not implemented.")
