import enum
import logging
import time
from typing import Callable

from robot.board import Board

LOGGER = logging.getLogger(__name__)


# Keep this in sync with `robotd`
class PowerOutput(enum.Enum):
    """An enumeration of the outputs on the power board."""

    H0 = 0
    H1 = 1
    L0 = 2
    L1 = 3
    L2 = 4
    L3 = 5


class PowerBoard(Board):
    """A power board, controlling the power distribution for the robot."""

    BUZZ_NOTES = {
        'c': 261,
        'd': 294,
        'e': 329,
        'f': 349,
        'g': 392,
        'a': 440,
        'b': 493,
        'uc': 523,
    }

    def __init__(
        self,
        *args,
        on_start_signal: Callable[[], None] = lambda: None,
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self._on_start_signal = on_start_signal

    def power_on(self):
        """
        Turn on power to all power board outputs.
        """

        self._send_and_receive({'power': True})

    def power_off(self):
        """
        Turn off power to all power board outputs.
        """
        self._send_and_receive({'power': False})

    def _set_output(self, output: PowerOutput, value: bool) -> None:
        """
        Turn on and off individual power outputs.
        """
        if not isinstance(value, bool):
            raise TypeError("Value must be a boolean (True/False)")
        self._send_and_receive({
            'power-output': output.value,
            'power-level': value,
        })

    def power_on_output(self, output: PowerOutput) -> None:
        """
        Turn on power to a specific power board output.
        """
        self._set_output(output, True)

    def power_off_output(self, output: PowerOutput) -> None:
        """
        Turn off power to a specific power board output.
        """
        self._set_output(output, False)

    def set_start_led(self, value: bool):
        """Set the state of the start LED."""
        self._send_and_receive({'start-led': value})

    @property
    def start_button_pressed(self) -> bool:
        """
        Read the status of the start button.
        """
        status = self._send_and_receive({})
        return status["start-button"]

    def wait_start(self) -> None:
        """
        Block until the start button is pressed.
        """
        LOGGER.info('Waiting for start button.')
        start_time = time.time()
        led_value = True
        while not self.start_button_pressed:
            if time.time() - start_time >= 0.1:
                led_value = not led_value
                start_time = time.time()
                self.set_start_led(led_value)
        self.set_start_led(False)

        self._on_start_signal()

        LOGGER.info("Starting user code.")

    def buzz(self, duration, *, note=None, frequency=None) -> None:
        """Enqueue a note to be played by the buzzer on the power board."""
        if note is None and frequency is None:
            raise ValueError("Either note or frequency must be provided")
        if note is not None and frequency is not None:
            raise ValueError("Only provide note or frequency")
        if note is not None:
            frequency = self.BUZZ_NOTES[note.lower()]
        if frequency is None:
            raise ValueError("Invalid frequency")
        self._send_and_receive({'buzz': {
            'frequency': frequency,
            'duration': int(duration * 1000),
        }})
