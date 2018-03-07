import math
import warnings
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

_SphericalCoord = NamedTuple('SphericalCoord', (
    ('rot_x_radians', Radians),
    ('rot_y_radians', Radians),
    ('distance_metres', Metres),
))


class SphericalCoord(_SphericalCoord):
    """
    Represents a point expressed in polar co-ordinates.

    This co-ordinate space describes a point as angles about the Cartesian x
    and y axes and a distance from the observer.

    Note: this co-ordinate space is different to the usual representation of a
    spherical space which measures its angles relative to Cartesian planes
    rather than about Cartesian axes.
    """

    @property
    def rot_x_degrees(self) -> Degrees:
        """Rotation about the x-axis in degrees."""
        return Degrees(math.degrees(self.rot_x_radians))

    @property
    def rot_y_degrees(self) -> Degrees:
        """Rotation about the y-axis in degrees."""
        return Degrees(math.degrees(self.rot_y_radians))


class PolarCoord:
    """
    Deprecated: represents a point expressed in legacy "polar" co-ordinates.

    This coordinate space uses angles between the given axis and a line between
    the point and the camera.

    Use of this co-ordinate space is discouraged.
    """

    def __init__(self, rot, dist_m):
        self._rot_x_rad = rot[0]
        self._rot_y_rad = rot[1]
        self._distance_metres = dist_m

    # TODO add tests for all these
    @property
    def rot_x_rad(self) -> Radians:
        """Deprecated. Use Spherical Coordinates instead."""
        return self._rot_x_rad

    @property
    def rot_y_rad(self) -> Radians:
        """Deprecated. Use Spherical Coordinates instead."""
        return self._rot_y_rad

    @property
    def rot_x_deg(self) -> Degrees:
        """Deprecated. Use Spherical Coordinates instead."""
        return Degrees(math.degrees(self._rot_x_rad))

    @property
    def rot_y_deg(self) -> Degrees:
        """Deprecated. Use Spherical Coordinates instead."""
        return Degrees(math.degrees(self._rot_y_rad))

    @property
    def distance_metres(self) -> Metres:
        """Deprecated. Use Spherical Coordinates instead."""
        return self._distance_metres


class Marker:
    """A marker captured from a webcam image."""

    def __init__(self, data):
        self._raw_data = data

    @property
    def id(self) -> int:
        """ID of the marker seen."""
        return self._raw_data['id']

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
        return self.spherical.distance_metres

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
        Deprecated: the position of the marker in legacy "polar" co-ordinates.

        This co-ordinate space uses angles between the given axis and a line
        between the point and the camera.
        """
        warnings.warn(
            "Use of the 'polar' property is deprecated as the values returned "
            "aren't from any known polar co-ordinate system. You should use the "
            "'spherical' property instead.",
            DeprecationWarning,
        )
        polar = self._raw_data['legacy_polar']
        return PolarCoord((polar[0], polar[1]), polar[2])

    @property
    def cartesian(self) -> CartCoord:
        """
        The position of the marker in Cartesian co-ordinates.

        The camera's position is the origin of the co-ordinate space.
        """
        return CartCoord(*self._raw_data['cartesian'])

    @property
    def spherical(self) -> SphericalCoord:
        """
        The position of the marker in Spherical co-ordinates.

        This co-ordinate space describes a point as angles about the Cartesian
        x and y axes and a distance from the camera. Note: this co-ordinate
        space is different to the usual representation of a spherical space.
        """
        return SphericalCoord(*self._raw_data['spherical'])

    def __repr__(self):
        return "<robot.markers.{} >".format(str(self))

    def __str__(self):
        bearing = self.spherical.rot_y_degrees
        return "Marker {}: {:.0f}° {}, {:.2f}m away".format(
            self.id,
            abs(bearing),
            "right" if bearing > 0 else "left",
            self.distance_metres,
        )
