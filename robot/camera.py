import socket
import time
from collections.abc import MutableSequence
from pathlib import Path

from robot.board import Board
from robot.markers import Marker


class Camera(Board):
    """
    A camera providing a view of the outside world expressed as ``Marker``s.
    """

    def __init__(self, socket_path):
        super().__init__(socket_path)
        self._serial = Path(socket_path).stem

    @staticmethod
    def _see_to_results(data):
        """
        Convert the data from ``robotd`` into a sorted of ``Marker``s.

        :param data: the data returned from ``robotd``.
        :return: A ``ResultList`` of ``Markers``, sorted by distance from the
                camera.
        """
        markers = []
        for token in data["markers"]:
            markers.append(Marker(token))
        # Sort by distance
        return ResultList(sorted(markers, key=lambda x: x.distance_metres))
        return ResultList(markers)

    @property
    def serial(self):
        """Serial number of the camera."""
        return self._serial

    def see(self):
        """
        Capture and process a new snapshot of the world the camera can see.

        Images are captured and processed on-demand in a "blocking" fashion, so
        this method may take a noticeable amount of time to complete its work.

        :return: A list of ``Marker`` objects which were identified.
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
    A ``list``-like class with nicer error messages.

    In particular, this class provides a slightly better error description when
    accessing index 0 and the list is empty.

    This is to mitigate a common beginners issue where a list is indexed
    without checking that the list has any items.
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

    def insert(self, index, value):  # noqa: D102
        self.data.insert(index, value)

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return self.data.__repr__()

    def __eq__(self, other):
        return self.data.__eq__(other)

    def __iter__(self):
        return self.data.__iter__()
