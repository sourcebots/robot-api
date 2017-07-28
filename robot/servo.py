import json
from pathlib import Path

from robot.board import Board


class Servo:
    def __init__(self, board, servo_id):
        self.board = board
        self.servo_id = servo_id

    @property
    def position(self):
        return self.board._get_status(self.servo_id)

    @position.setter
    def position(self, position):
        self.board._update_servo(self.servo_id, position)


class ServoBoard(Board):
    def __init__(self, socket_path):
        super().__init__(socket_path)
        self._serial = Path(socket_path).stem

        servo_ids = range(0, 16)  # servos with a port 0-15

        self.servos = [Servo(self, x) for x in servo_ids]

    @property
    def ports(self):
        """
        List of `Servo` objects for the servo
        """
        return self.servos

    @property
    def serial(self):
        """
        Serial number for the board
        """
        return self._serial

    def _get_status(self, port):
        return self._send_recv_data({})[str(port)]

    def _update_servo(self, port, position):
        """
        Set the position of a servo
        :param port: port for the servo board
        :param position: position to set the servo to
        """
        if position > 1 or position < -1:
            raise ValueError("Value should be between -1 and 1")
        self._send_recv_data({port: position})
