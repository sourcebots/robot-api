import math
from collections import namedtuple
from robot.game_specific import TOKEN, WALL

CartCoord = namedtuple("CardCoord", ["x", "y", "z"])

class PolarCoord:
    """
    Represents a point expressed in polar co-ordinates.

    Strictly the space are spherical co-ordinates.
    """

    def __init__(self, rot, dist_m):
        self._rot_x_rad = rot[0]
        self._rot_y_rad = rot[1]
        self._distance_metres = dist_m

    # TODO add tests for all these
    @property
    def rot_x_rad(self) -> float:
        """
        Rotation of marker relative to camera in the #TODO axis.
        """
        return self._rot_x_rad

    @property
    def rot_y_rad(self) -> float:
        """
        Rotation of marker relative to camera in the #TODO axis.
        """
        return self._rot_y_rad

    @property
    def rot_x_deg(self) -> float:
        """
        Rotation of marker relative to camera in the #TODO axis.
        """
        # TODO describe which axis this is
        return math.degrees(self._rot_x_rad)

    @property
    def rot_y_deg(self) -> float:
        """
        Rotation of marker relative to camera in the #TODO axis.
        """
        # TODO describe which axis this is
        return math.degrees(self._rot_y_rad)

    @property
    def distance_metres(self) -> float:
        """Distance of marker from camera in metres."""
        # TODO describe which axis this is
        return self._distance_metres


class Marker:
    """A marker captured from a webcam image."""

    def __init__(self, data):
        self._raw_data = data

    def id(self) -> int:
        """ID of the marker seen."""
        return self._id

    @property
    def size(self) -> Tuple:
        """Marker size in metres."""
        return tuple(self._size)

    # Disabled because it's always 0.0
    # TODO fix the certainty being 0
    # @property
    # def certainty(self):
    #     return self._certainty

    @property
    def pixel_corners(self):
        """Pixel co-ordinates of the of the corners of the marker."""
        # TODO define what the order of these corners are
        return [tuple(x) for x in self._raw_data['pixel_corners']]

    @property
    def pixel_centre(self):
        """Pixel co-ordinates of the centre of the marker."""
        return tuple(self._pixel_centre)

    @property
    def distance_metres(self):
        """Distance of the marker from the camera in metres."""
        return self.polar.distance_metres

    # Helper functions, Might need to vary these per-game
    def is_wall_marker(self) -> bool:
        """If the marker is a wall marker."""
        return self.id in WALL

    def is_token_marker(self) -> bool:
        """If the marker is a token marker."""
        return self.id in TOKEN

    @property
    def polar(self):
        """
        The position of the marker in the polar co-ordinates.

        Strictly these are spherical co-ordinates. The camera's position is the
        origin of the co-ordinate space.
        """
        return PolarCoord((self._polar[0], self._polar[1]), self._polar[2])

    @property
    def cartesian(self):
        """
        The position of the marker in Cartesian co-ordinates.

        The camera's position is the origin of the co-ordinate space.
        """
        raise NotImplementedError("This is not implemented.")
