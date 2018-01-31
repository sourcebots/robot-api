import socket
import time

from robot.board import Board
from robot.markers import Marker


class Camera(Board):
    """
    A camera providing a view of the outside world expressed as ``Marker``s.
    """

    @staticmethod
    def _see_to_results(data):
        """
        Convert the data from ``robotd`` into a sorted of ``Marker``s.

        :param data: the data returned from ``robotd``.
        :return: A ``ResultList`` of ``Markers``, sorted by distance from the
                camera.
        """
        return ResultList(sorted(
            (Marker(x) for x in data["markers"]),
            key=lambda x: x.distance_metres,
        ))

    def see(self):
        """
        Capture and process a new snapshot of the world the camera can see.

        Images are captured and processed on-demand in a "blocking" fashion, so
        this method may take a noticeable amount of time to complete its work.

        :return: A list of ``Marker`` objects which were identified.
        """
        abort_after = time.time() + 10

        self._send({'see': True})

        while True:
            try:
                return self._see_to_results(self._receive(should_retry=True))
            except socket.timeout:
                if time.time() > abort_after:
                    raise


class ResultList(list):
    """
    A ``list`` class with nicer error messages.

    In particular, this class provides a slightly better error description when
    accessing indexes and the list is empty.

    This is to mitigate a common beginners issue where a list is indexed
    without checking that the list has any items.
    """

    def __getitem__(self, *args, **kwargs):
        try:
            return super().__getitem__(*args, **kwargs)
        except IndexError as e:
            if not self:
                raise IndexError("Trying to index an empty list") from None
            else:
                raise
