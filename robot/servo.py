import json
from pathlib import Path

from enum import Enum

from robot.board import Board


class PinMode(Enum):
    INPUT = 'hi-z'
    INPUT_PULLUP = 'pullup'
    OUTPUT_HIGH = 'high'
    OUTPUT_LOW = 'low'


class PinValue(Enum):
    HIGH = 'high'
    LOW = 'low'


class Servo:
    def __init__(self, servo_id, set_pos, get_pos):
        self.servo_id = servo_id
        self._set_pos = set_pos
        self._get_pos = get_pos

    @property
    def position(self):
        return self._get_pos()

    @position.setter
    def position(self, position):
        if position > 1 or position < -1:
            raise ValueError("servo position must be between -1 and 1")
        self._set_pos(position)


class Gpio:
    def __init__(self, pin_id, pin_read, pin_mode_get, pin_mode_set):
        self._pin_id = pin_id
        self._pin_read = pin_read
        self._pin_mode_get = pin_mode_get
        self._pin_mode_set = pin_mode_set

    @property
    def mode(self):
        return PinMode[self._pin_mode_get()]

    @mode.setter
    def mode(self, mode: PinMode):
        """
        The mode the pin should be in
        :param mode: PinMode.INPUT, PinMode.INPUT_PULLUP, or PinMode.OUTPUT_HIGH or PinMode.OUTPUT_LOW
        """
        self._pin_mode_set(mode.value)

    def read(self):
        if self._pin_mode_get() not in [PinMode.INPUT, PinMode.INPUT_PULLUP]:
            raise Exception("Pin mode needs to be either PinMode.INPUT or PinMode.INPUT_PULLUP to read")
        return self._pin_read()


class ServoBoard(Board):

    def __init__(self, socket_path):
        super().__init__(socket_path)
        self._serial = Path(socket_path).stem

        servo_ids = range(0, 16)  # servos with a port 0-15
        gpio_pins = range(2, 13)  # gpio pins 2-12

        self._servos = {}
        for x in servo_ids:
            self._servos[x] = Servo(
                x,
                (lambda pos, x=x: self._set_servo_pos(x, pos)),
                (lambda x=x: self._get_servo_pos(x)),
            )
        self._gpios = {
            x: Gpio(
                x,
                (lambda x=x: self._read_pin(x)),
                (lambda x=x: self._get_pin_mode(x)),
                (lambda value, x=x: self._set_pin_mode(x, value))
            )
            for x in gpio_pins
            }

    @property
    def serial(self):
        """
        Serial number for the board
        """

        return self._serial

    # Servo code

    @property
    def servos(self):
        """
        List of `Servo` objects for the servo board
        """
        return self._servos

    def _set_servo_pos(self, servo, pos):
        self._send_recv_data({'servos': {servo: pos}})

    def _get_servo_pos(self, servo):
        data = self._send_recv_data({})
        values = data['servos']
        return values[str(servo)]

    # GPIO code

    def gpios(self):
        return self._gpios

    def _read_pin(self, pin):
        # request a check for that pin by trying to set it to None
        data = self._send_recv_data({'pins': {pin, None}})
        # example data value:
        # {'pin-values':{2:'high'}}
        values = data['pin-values']
        return PinValue[values[pin]]

    def _get_status(self):
        status = self.send_and_receive({})
        return status['servos'][str(port)]

    def _get_pin_mode(self, pin):
        data = self._send_recv_data({})
        # example data value:
        # {'pins':{2:'pullup'}}
        values = data['pins']
        return PinMode[values[pin]]

    def _set_pin_mode(self, pin, value: PinMode):
        self._send_recv_data({'pins': {pin, value.value}})
