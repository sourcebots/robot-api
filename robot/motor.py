import json
from pathlib import Path

from robot.board import Board


BRAKE = 0  # 0 so setting the motors to 0 has exactly the same affect as setting the motors to BRAKE
COAST = "coast"

class MotorBoard(Board):

    def __init__(self, socket_path):
        super().__init__(socket_path)
        self._serial = Path(socket_path).stem

    @staticmethod
    def _string_to_power(voltage):
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
            raise ValueError('Incorrect voltage value, valid values: between -1 and 1, "coast", or "brake"')

    @staticmethod
    def _power_to_string(voltage):
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
        :return: The current value of the motor
        """
        return self._get_status("m0")

    @m0.setter
    def m0(self, power):
        self._update_motor("m0", power)


    @property
    def m1(self):
        """
        :return: The current value of the motor
        """
        return self._get_status("m1")

    @m1.setter
    def m1(self, power):
        self._update_motor("m1", power)

    @property
    def serial(self):
        """Serial number for the board"""
        return self._serial

    def _get_status(self, motor_id):
        return self._string_to_power(
            self.send_and_receive({})[motor_id]
        )

    def _update_motor(self, motor_id, voltage):
        """
        Set the value of a motor
        :param motor_id: id of the motor, either 'm0' or 'm1'
        :param voltage: Voltage to set the motor to
        """
        v_string = self._power_to_string(voltage)
        self.send_and_receive({motor_id: v_string})
