from enum import Enum
from typing import List, Dict

from robot.board import Board


class PinMode(Enum):
    """A pin-mode for a pin on the servo board."""

    INPUT = 'hi-z'
    INPUT_PULLUP = 'pullup'
    OUTPUT_HIGH = 'high'
    OUTPUT_LOW = 'low'


class PinValue(Enum):
    """A value state for a pin on the servo board."""

    HIGH = 'high'
    LOW = 'low'


class Servo:
    """A servo output on a ``ServoBoard``."""

    def __init__(self, servo_id, set_pos, get_pos):
        self.servo_id = servo_id
        self._set_pos = set_pos
        self._get_pos = get_pos

    @property
    def position(self) -> float:
        """The configured position the servo output."""
        return self._get_pos()

    @position.setter
    def position(self, position):
        if position > 1 or position < -1:
            raise ValueError("servo position must be between -1 and 1")
        self._set_pos(position)


class Gpio:
    """A general-purpose input-output pin on a ``ServoBoard``."""

    def __init__(self, pin_id, pin_read, pin_mode_get, pin_mode_set):
        self._pin_id = pin_id
        self._pin_read = pin_read
        self._pin_mode_get = pin_mode_get
        self._pin_mode_set = pin_mode_set

    @property
    def mode(self) -> PinMode:
        """The ``PinMode`` the pin is currently in."""
        return PinMode(self._pin_mode_get())

    @mode.setter
    def mode(self, mode: PinMode):
        """
        Set the mode the pin should be in.

        :param mode: The ``PinMode`` to set the pin to.
        """
        if mode not in (
            PinMode.INPUT,
            PinMode.INPUT_PULLUP,
            PinMode.OUTPUT_HIGH,
            PinMode.OUTPUT_LOW,
        ):
            raise ValueError("Mode should be a valid 'PinMode', got {!r}".format(mode))
        self._pin_mode_set(mode)

    def read(self) -> PinValue:
        """Read the current ``PinValue`` of the pin."""
        valid_read_modes = (PinMode.INPUT, PinMode.INPUT_PULLUP)
        if self._pin_mode_get() not in valid_read_modes:
            raise Exception(
                "Pin mode needs to be in a valid read ``PinMode`` to be read. "
                "Valid modes are: {}.".format(
                    ", ".join(str(x) for x in valid_read_modes),
                ),
            )
        return self._pin_read()


class ArduinoError(Exception):
    """Base class for exceptions fed back from the ``ServoBoard`` (arduino)."""

    pass


class CommandError(ArduinoError):
    """The servo assembly experienced an error in processing a command."""

    pass


class InvalidResponse(ArduinoError):
    """The servo assembly emitted a response which could not be processed."""

    pass


class ServoBoard(Board):
    """
    A servo board, providing access to ``Servo``s and ``Gpio`` pins.

    This is an arduino with a servo shield attached.
    """

    def __init__(self, socket_path):
        super().__init__(socket_path)

        servo_ids = range(0, 16)  # servos with a port 0-15
        gpio_pins = range(2, 13)  # gpio pins 2-12

        self._servos = {}  # type: Dict[int, Servo]
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
                (lambda value, x=x: self._set_pin_mode(x, value)),
            )
            for x in gpio_pins
        }  # type: Dict[int, Gpio]

    def direct_command(self, command_name: str, *args) -> List[str]:
        """
        Issue a command directly to the arduino.

        :Example:
        >>> # arrives on the arduino as "my-command 4"
        >>> servo_board.direct_command('my-command', 4)
        ["first line response from my command", "second line"]

        The arguments to this method are bundled as a list and passed to robotd.
        We expect to immediately get back a response message (as well as the
        usual status blob) which contains either valid data from the arduino or
        a description of the failure.
        """
        command = (command_name,) + args
        response = self._send_and_receive({'command': command})['response']
        status = response['status']

        # consume the broadcast status
        self._receive()

        if status == 'ok':
            return response['data']
        else:
            for cls in (CommandError, InvalidResponse):
                if cls.__name__ == response['type']:
                    raise cls(response['description'])

            raise ArduinoError(response['description'])

    # Servo code

    @property
    def servos(self) -> Dict[int, Servo]:
        """List of ``Servo`` outputs for the servo board."""
        return self._servos

    def _set_servo_pos(self, servo: int, pos: float):
        self._send_and_receive({'servos': {servo: pos}})

    def _get_servo_pos(self, servo: int) -> float:
        data = self._send_and_receive({})
        values = data['servos']
        return float(values[str(servo)])

    # GPIO code
    @property
    def gpios(self) -> Dict[int, Gpio]:
        """List of ``Gpio`` pins for the servo board."""
        return self._gpios

    def _read_pin(self, pin) -> PinValue:
        # request a check for that pin by trying to set it to None
        data = self._send_and_receive({'read-pins': [pin]})
        # example data value:
        # {'pin-values':{2:'high'}}
        values = data['pin-values']
        return PinValue(values[str(pin)])

    def _get_pin_mode(self, pin) -> PinMode:
        data = self._send_and_receive({})
        # example data value:
        # {'pins':{2:'pullup'}}
        values = data['pins']
        return PinMode(values[str(pin)])

    def _set_pin_mode(self, pin, value: PinMode):
        self._send_and_receive({'pins': {pin: value.value}})

    def read_analogue(self) -> Dict[str, str]:
        """Read analogue values from the connected board."""
        command = {'read-analogue': True}
        return self._send_and_receive(command)['analogue-values']

    def read_ultrasound(self, trigger_pin, echo_pin):
        """
        Read an ultrasound value from an ultrasound sensor.

        :param trigger_pin: The pin number on the servo board that the sensor's
                            trigger pin is connected to.
        :param echo_pin: The pin number on the servo board that the sensor's
                         echo pin is connected to.
        """
        command = {'read-ultrasound': [trigger_pin, echo_pin]}
        return float(self._send_and_receive(command)['ultrasound'])
