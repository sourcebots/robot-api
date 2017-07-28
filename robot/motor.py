import json
from pathlib import Path

from robot.board import Board

BRAKE = 0  # 0 so setting the motors to 0 has exactly the same affect as setting the motors to BRAKE
COAST = "coast"


class Motor:
    def __init__(self, motor_board, motor_id):
        self.motor_board = motor_board
        self.motor_id = motor_id

    @property
    def voltage(self):
        return self.motor_board._get_status(self.motor_id)

    @voltage.setter
    def voltage(self, voltage):
        self.motor_board._update_motor(self.motor_id, voltage)


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
    def _string_to_voltage(voltage):
        """
        Converts a string to a Voltage value
        :param voltage:
        :return:
        """
        if voltage == 'coast':
            return COAST
        elif voltage == 'brake':
            return BRAKE
        elif -1 <= voltage <= 1:
            return voltage
        else:
            raise ValueError('Incorrect voltage value, valid values: between -1 and 1, "free", or "brake"')

    @staticmethod
    def _voltage_to_string(voltage):
        """
        Inverse of #MotorBoard.string_to_voltage
        Converts more human readable info to that robotd can read
        """
        if voltage is COAST:
            return 'coast'
        # Explicit or implicit stopping
        elif voltage is BRAKE or voltage == 0:
            return 'brake'
        elif -1 <= voltage <= 1:
            return voltage
        else:
            raise ValueError('Incorrect voltage value, valid values: between -1 and 1, robot.COAST, or robot.BRAKE')

    @property
    def m0(self):
        """
        :return: `Motor` object for motor connected to the `m0` slot
        """
        return self._m0

    @property
    def m1(self):
        """
        :return: `Motor` object for motor connected to the `m1` slot
        """
        return self._m1

    @property
    def serial(self):
        """
        Serial number for the board
        """
        return self._serial

    def _get_status(self, motor_id):
        return self._string_to_voltage(
            self._send_recv_data({})[motor_id]
        )

    def _update_motor(self, motor_id, voltage):
        """
        Set the value of a motor
        :param motor_id: id of the motor, either 'm0' or 'm1'
        :param voltage: Voltage to set the motor to
        """
        v_string = self._voltage_to_string(voltage)
        self._send_recv_data({motor_id: v_string})
