import json
import threading
from pathlib import Path

from robot.board import Board


class Marker:
    def __init__(self, data):
        self._raw_data = data
        self.__dict__.update(data)


class Camera(Board):
    def __init__(self, socket_path):
        self._latest = None
        self._got_image = threading.Event()
        super().__init__(socket_path)
        self._serial = Path(socket_path)
        self._running = threading.Event()
        self._latest_lock = threading.Lock()
        self.sock_thread = self.listen()

    def _init_response(self, data):
        pass

    def listen(self):
        thread = threading.Thread(target=self.cam_listener_worker)
        self._running.set()
        thread.start()
        return thread

    def clean_up(self):
        pass

    def stop_poll(self):
        self._running.clear()
        self.sock_thread.join()

    def cam_listener_worker(self):
        print("Thread started")
        while self._running.is_set():
            data = self._recv()
            if data:
                self._got_image.set()
                # print("Received", data)
                with self._latest_lock:
                    self._latest = data
        print("Thread finished")

    @staticmethod
    def see_to_results(data):
        tokens = []
        data = json.loads(data)
        for token in data["tokens"]:
            tokens.append(Marker(token))
        # Sort by distance
        return sorted(tokens, key=lambda x: x.distance)

    @property
    def serial(self):
        """
        Serial number for the board
        """
        return self._serial

    def see(self):
        self._got_image.wait()
        with self._latest_lock:
            return self.see_to_results(self._latest)
