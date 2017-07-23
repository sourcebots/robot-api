import json
import threading
from collections.abc import MutableSequence
from pathlib import Path

from robot.board import Board
from robot.markers import Marker


class Camera(Board):
    """
    Object representing an Apriltag camera in robotd

    Polls the robot daemon for new images
    """

    def __init__(self, socket_path):
        self._latest = None
        self._got_image = threading.Event()
        super().__init__(socket_path)
        self._serial = Path(socket_path).stem
        self._stop = threading.Event()
        self._latest_lock = threading.Lock()
        self._start_listening()

    def _start_listening(self):
        """
        Start listening thread
        """
        thread = threading.Thread(target=self._cam_listener_worker)
        self._stop.clear()
        thread.start()
        self.sock_thread = thread

    def _clean_up(self):
        pass

    def _stop_poll(self):
        """
        Stop polling the camera
        """
        self._stop.set()
        self.sock_thread.join()

    def _cam_listener_worker(self):
        """
        Worker thread for listening to the camera socket

        Works until `self._running` is set.
        """
        while not self._stop.is_set():
            data = self._recv()
            if data:
                self._got_image.set()
                with self._latest_lock:
                    self._latest = data

    @staticmethod
    def _see_to_results(data):
        """
        Converts the string output that comes from the camera in robotd to a list of #Marker objects
        :param data: json string data to convert
        :return: #ResultList object (that imitates a list) of markers
        """
        markers = []
        data = json.loads(data)
        for token in data["tokens"]:
            markers.append(Marker(token))
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
        self._got_image.wait()
        with self._latest_lock:
            return self._see_to_results(self._latest)


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
