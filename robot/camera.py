from collections.abc import MutableSequence
from pathlib import Path
import socket
import time

from robot.board import Board
from robot.markers import Marker


class Camera(Board):
    """
    Object representing an Apriltag camera in robotd

    Polls the robot daemon for new images
    """

    def __init__(self, socket_path):
        super().__init__(socket_path)
        self._serial = Path(socket_path).stem

    @staticmethod
    def _see_to_results(data):
        """
        Converts the string output that comes from the camera in robotd to a list of #Marker objects
        :param data: json string data to convert
        :return: #ResultList object (that imitates a list) of markers
        """
        markers = [Marker(x) for x in data["markers"]]

        # Sort by distance
        return ResultList(sorted(markers, key=lambda x: x.distance_metres))

    @property
    def serial(self):
        """
        Serial number for the board
        """
        return self._serial

    def see(self):
        """
        Look for markers
        :return: List of #Marker objects
        """
        abort_after = time.time() + 10

        self.send({'see': True})

        while True:
            try:
                return self._see_to_results(self.receive(should_retry=True))
            except socket.timeout:
                if time.time() > abort_after:
                    raise


class ResultList(list):
    """
    This class returns a more beginner-friendly error messages if the user
    indexes into it, but it is empty.

    This is to mitigate a common beginners issue where an array is indexed
    without checking that the array has any items.
    """

    def __getitem__(self, *args, **kwargs):
        try:
            return super().__getitem__(*args, **kwargs)
        except IndexError as e:
            if not self:
                raise IndexError("Trying to index an empty list")
            else:
                raise
