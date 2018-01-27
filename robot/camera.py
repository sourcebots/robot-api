from pathlib import Path
from robot.board import Board
from robot.markers import Marker
import time
from typing import List, overload
import socket


class ResultList(List[Marker]):
    """
    A ``list`` class with nicer error messages.

    In particular, this class provides a slightly better error description when
    accessing indexes and the list is empty.

    This is to mitigate a common beginners issue where a list is indexed
    without checking that the list has any items.
    """

    @overload
    def __getitem__(self, index: int) -> Marker:
        ...

    @overload  # noqa: F811 (deliberately method replacement)
    def __getitem__(self, index: slice) -> List[Marker]:
        ...

    def __getitem__(self, index):  # noqa: F811 (deliberately method replacement)
        try:
            return super().__getitem__(index)
        except IndexError as e:
            if not self:
                raise IndexError("Trying to index an empty list") from None
            else:
                raise e


class Camera(Board):
    """
    A camera providing a view of the outside world expressed as ``Marker``s.
    """

    def __init__(self, socket_path):
        super().__init__(socket_path)
        self._serial = Path(socket_path).stem

    @staticmethod
    def _see_to_results(data) -> ResultList:
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

    @property
    def serial(self):
        """Serial number of the camera."""
        return self._serial

    def see(self) -> ResultList:
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
