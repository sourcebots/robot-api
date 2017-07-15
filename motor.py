import json
import socket
from pathlib import Path

from robot import COAST, BRAKE
from robot.board import Board


class Motor:
    def __init__(self, motor_board, motor_id):
        self.motor_board = motor_board
        self.motor_id = motor_id

    @property
    def voltage(self):
        return self.motor_board.get_status(self.motor_id)

    @voltage.setter
    def voltage(self, voltage):
        self.motor_board.update_motor(self.motor_id, voltage)


class MotorBoard(Board):
    def __init__(self, socket_path):
        super().__init__(socket_path)
        self._serial = Path(socket_path).stem

        m0_id = "m0"
        m1_id = "m1"

        self._m0 = Motor(self, m0_id)
        self._m1 = Motor(self, m1_id)

        # Set 'm0' and 'm1' to the motors
        self.motor_index = {
            m0_id: self._m0,
            m1_id: self._m1
        }



    @staticmethod
    def string_to_voltage(voltage):
        """
        Converts a string to a Voltage value
        :param voltage:
        :return:
        """
        if voltage == 'free':
            return COAST
        elif voltage == 'brake':
            return BRAKE
        elif -1 <= voltage <= 1:
            return voltage
        else:
            raise ValueError('Incorrect voltage value, valid values: between -1 and 1, "free", or "brake"')

    @staticmethod
    def voltage_to_string(voltage):
        """
        Inverse of #MotorBoard.string_to_voltage
        """
        if voltage is COAST:
            return 'free'
        # Explicit or implicit stopping
        elif voltage is BRAKE or voltage == 0:
            return 'brake'
        elif -1 <= voltage <= 1:
            return voltage
        else:
            raise ValueError('Incorrect voltage value, valid values: between -1 and 1, robot.COAST, or robot.BRAKE')

    @property
    def m0(self):
        return self._m0

    @property
    def m1(self):
        return self._m1

    @property
    def serial(self):
        """
        Serial number for the board
        """
        return self._serial

    def update_motor(self, motor_id, voltage):
        v_string = self.voltage_to_string(voltage)
        self._send(json.dumps({motor_id: v_string}).encode('utf-8'))

