import json
import threading
from pathlib import Path
from collections.abc import MutableSequence

import math

from robot.board import Board
from robot.game_specific import WALL, TOKEN


class CartCoord:
    """
    Represents a cartesian co-ordinate point
    """

    def __init__(self, x, y, z):
        self._x = x
        self._y = y
        self._z = z

    @property
    def x(self):
        """ X co-ordinate of the cartesian position"""
        return self._x

    @property
    def y(self):
        """ Y co-ordinate of the cartesian position"""
        return self._y

    @property
    def z(self):
        """ Z co-ordinate of the cartesian position"""
        return self._z


class PolarCoord:
    """
    Represents a polar co-ordinate point
    """

    def __init__(self, rot, dist_m):
        self._rot_x_rad = rot[0]
        self._rot_y_rad = rot[1]
        self._rot_z_rad = rot[2]
        self._distance_metres = dist_m

    # TODO add tests for all these
    @property
    def rot_x_rad(self):
        """
        Rotation of marker relative to camera in the #TODO axis
        (axis is in the location of the camera)
        """
        return self._rot_x_rad

    @property
    def rot_y_rad(self):
        """
        Rotation of marker relative to camera in the #TODO axis
        (axis is in the location of the camera)
        """
        return self._rot_y_rad

    @property
    def rot_z_rad(self):
        """
        Rotation of marker relative to camera in the #TODO axis
        (axis is in the location of the camera)
        """
        return self._rot_z_rad

    @property
    def rot_x_deg(self):
        """
        Rotation of marker relative to camera in the #TODO axis.
        (axis is in the location of the camera)
        """
        # TODO describe which axis this is
        return math.degrees(self._rot_x_rad)

    @property
    def rot_y_deg(self):
        """
        Rotation of marker relative to camera in the #TODO axis.
        (axis is in the location of the camera)
        """
        # TODO describe which axis this is
        return math.degrees(self._rot_y_rad)

    @property
    def rot_z_deg(self):
        """
        Rotation of marker relative to camera in the #TODO axis.
        (axis is in the location of the camera)
        """
        # TODO describe which axis this is
        return math.degrees(self._rot_z_rad)

    @property
    def distance_metres(self):
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

        # Go through all the data, add an _ at the start.
        data = {"_" + k: v for k, v in data.items()}

        self.__dict__.update(data)

    @property
    def id(self):
        """
            ID of the marker seen
        """
        return self._id

    @property
    def size(self):
        """
            Marker size in metres
        """
        return tuple(self._size)

    # Disabled because it's always 0.0
    # TODO fix the certainty being 0
    # @property
    # def certainty(self):
    #     return self._certainty

    @property
    def pixel_corners(self):
        """
            Pixel co-ordinates of the of the corners of the marker
        """
        # TODO define what the order of these corners are
        return [tuple(x) for x in self._pixel_corners]

    @property
    def pixel_centre(self):
        """
            Pixel co-ordinates of the centre of the marker
        """
        return tuple(self._pixel_centre)

    @property
    def distance_metres(self):
        """
        Distance of the marker from the camera in metres
        """
        return self.polar.distance_metres

    # Helper functions, Might need to vary these per-game

    def is_wall_marker(self):
        """ If the marker is a wall marker """
        return self.id in WALL

    def is_token_marker(self):
        """ If the marker is a token marker """
        return self.id in TOKEN

    @property
    def polar(self):
        """ Position of the marker in the polar co-ordinates system, Axis is at the camera's position """
        return PolarCoord(self._polar[0], self._polar[1])

    @property
    def cartesian(self):
        return CartCoord()


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
        self._running = threading.Event()
        self._latest_lock = threading.Lock()
        self._start_listening()

    def _start_listening(self):
        """
        Start listening thread
        """
        thread = threading.Thread(target=self._cam_listener_worker)
        self._running.set()
        thread.start()
        self.sock_thread = thread

    def _clean_up(self):
        pass

    def _stop_poll(self):
        """
        Stop polling the camera
        """
        self._running.clear()
        self.sock_thread.join()

    def _cam_listener_worker(self):
        """
        Worker thread for listening to the camera socket

        Works until `self._running` is set.
        """
        while self._running.is_set():
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
