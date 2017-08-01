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
        markers = []
        for token in data["markers"]:
            markers.append(Marker(token))
        # Sort by distance
        return ResultList(markers)

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


class ResultList(MutableSequence):
    """
    This class pretends to be a list, except it returns
    a much more useful error description if the user indexes an empty array.

    This is to mitigate a common beginners issue where an array is indexed
    without checking that the array has any items
    """

    def __delitem__(self, index):
        del self.data[index]

    def __init__(self, data):
        self.data = data

    def __getitem__(self, item):
        try:
            self.data[item]
        except IndexError as e:
            if len(self.data) == 0:
                raise IndexError("Trying to index an empty list")
            else:
                raise e

    def __setitem__(self, key, value):
        self.data[key] = value

    def insert(self, index, value):
        self.data.insert(index, value)

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return self.data.__repr__()

    def __eq__(self, other):
        return self.data.__eq__(other)

    def __iter__(self):
        return self.data.__iter__()
