import json
import socket
from pathlib import Path

from robot import COAST, BRAKE


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


class MotorBoard:
    def __init__(self, socket_path):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        self.sock.connect(socket_path)
        self._serial = Path(socket_path).stem
        # Get the status message, throw it away
        _ = self.sock.recv(2048)

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
    def string_to_voltage(voltage_string):
        """
        Converts a string to a Voltage value
        :param voltage_string:
        :return:
        """
        if voltage_string == 'free':
            return COAST
        elif voltage_string == 'brake':
            return BRAKE
        elif -1 <= float(voltage_string) <= 1:
            return float(voltage_string)
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
            return str(voltage)
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
        self.sock.send(json.dumps({motor_id: v_string}).encode('utf-8'))
        # Receive the response
        self.sock.recv(2048)

    def get_status(self, motor_id):
        # If you send it a {} it returns a status.
        self.sock.send('{}')
        status = json.loads(self.sock.recv(2048))
        return self.string_to_voltage(status[motor_id])
