from typing import Union

from robot.board import Board

Power = Union[float, str]
_VoltageString = Union[float, str]


# BRAKE is set to 0 so setting the motors to 0 has exactly the same affect as
# setting the motors to BRAKE
BRAKE = 0
COAST = "coast"


class MotorBoard(Board):
    """A motor board with two motor outputs."""

    @staticmethod
    def _string_to_power(voltage: _VoltageString) -> Power:
        """
        Converts a string to a Voltage value.

        :param voltage:
        :return:
        """
        if isinstance(voltage, str):
            if voltage == 'coast':
                return COAST
            elif voltage == 'brake':
                return BRAKE

        if isinstance(voltage, float):
            if -1 <= voltage <= 1:
                return voltage

        raise ValueError(
            "Incorrect voltage value, valid values: between -1 and 1, "
            "'coast', or 'brake'",
        )

    @staticmethod
    def _power_to_string(voltage: Power) -> _VoltageString:
        """
        Converts a voltage value to the equivalent API value.

        This is the reverse of inverse of ``MotorBoard.string_to_voltage``.
        """
        if isinstance(voltage, str):
            if voltage is COAST:
                return 'coast'

        if isinstance(voltage, float):
            # Explicit or implicit stopping
            if voltage is BRAKE or voltage == 0:
                return 'brake'
            elif -1 <= voltage <= 1:
                return voltage

        raise ValueError(
            "Incorrect voltage value, valid values: between -1 and 1, "
            "robot.COAST, or robot.BRAKE",
        )

    @property
    def m0(self) -> Power:
        """
        :return: The value of motor output 0.
        """
        return self._get_status("m0")

    @m0.setter
    def m0(self, power: Power) -> None:
        self._update_motor("m0", power)

    @property
    def m1(self) -> Power:
        """
        :return: The value of motor output 1.
        """
        return self._get_status("m1")

    @m1.setter
    def m1(self, power: Power) -> None:
        self._update_motor("m1", power)

    def _get_status(self, motor_id: str) -> Power:
        return self._string_to_power(
            self._send_and_receive({})[motor_id],
        )

    def _update_motor(self, motor_id: str, voltage: Power) -> None:
        """
        Set the value of a motor output.

        :param motor_id: id of the motor, either 'm0' or 'm1'
        :param voltage: Voltage to set the motor to
        """
        v_string = self._power_to_string(voltage)
        self._send_and_receive({motor_id: v_string})
