import math
from typing import List, NamedTuple, NewType, Tuple

from robot.game_specific import TOKEN, WALL

Metres = NewType('Metres', float)
Degrees = NewType('Degrees', float)
Radians = NewType('Radians', float)
Pixel = NewType('Pixel', float)
PixelCoordinates = NewType('PixelCoordinates', Tuple[Pixel, Pixel])

CartCoord = NamedTuple('CartCoord', (
    ('x', Metres),
    ('y', Metres),
    ('z', Metres),
))


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
    def rot_x_rad(self) -> Radians:
        """
        Rotation of marker relative to camera in the #TODO axis.
        """
        return self._rot_x_rad

    @property
    def rot_y_rad(self) -> Radians:
        """
        Rotation of marker relative to camera in the #TODO axis.
        """
        return self._rot_y_rad

    @property
    def rot_x_deg(self) -> Degrees:
        """
        Rotation of marker relative to camera in the #TODO axis.
        """
        # TODO describe which axis this is
        return Degrees(math.degrees(self._rot_x_rad))

    @property
    def rot_y_deg(self) -> Degrees:
        """
        Rotation of marker relative to camera in the #TODO axis.
        """
        # TODO describe which axis this is
        return Degrees(math.degrees(self._rot_y_rad))

    @property
    def distance_metres(self) -> Metres:
        """Distance of marker from camera in metres."""
        # TODO describe which axis this is
        return self._distance_metres


class Marker:
    """A marker captured from a webcam image."""

    def __init__(self, data):
        self._raw_data = data

    @property
    def id(self) -> int:
        """ID of the marker seen."""
        return self._raw_data['id']

    @property
    def size(self) -> Tuple[Metres, Metres]:
        """Marker size in metres."""
        return self._raw_data['size']

    # Disabled because it's always 0.0
    # TODO fix the certainty being 0
    # @property
    # def certainty(self):
    #     return self._certainty

    @property
    def pixel_corners(self) -> List[PixelCoordinates]:
        """Pixel co-ordinates of the of the corners of the marker."""
        # TODO define what the order of these corners are
        return [PixelCoordinates((x[0], x[1])) for x in self._raw_data['pixel_corners']]

    @property
    def pixel_centre(self) -> PixelCoordinates:
        """Pixel co-ordinates of the centre of the marker."""
        pixel_center = self._raw_data['pixel_centre']
        return PixelCoordinates((pixel_center[0], pixel_center[1]))

    @property
    def distance_metres(self) -> Metres:
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
    def polar(self) -> PolarCoord:
        """
        The position of the marker in the polar co-ordinates.

        Strictly these are spherical co-ordinates. The camera's position is the
        origin of the co-ordinate space.
        """
        polar = self._raw_data['polar']
        return PolarCoord((polar[0], polar[1]), polar[2])

    @property
    def cartesian(self) -> CartCoord:
        """
        The position of the marker in Cartesian co-ordinates.

        The camera's position is the origin of the co-ordinate space.
        """
        return CartCoord(*self._raw_data['cartesian'])
