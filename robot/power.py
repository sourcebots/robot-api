import enum
import logging
import time
from typing import Callable

from robot.board import Board

LOGGER = logging.getLogger(__name__)


# Keep this in sync with `robotd`
class PowerOutput(enum.Enum):
    """An enumeration of the outputs on the power board."""

    HIGH_POWER_1 = 0
    HIGH_POWER_2 = 1
    LOW_POWER_1 = 2
    LOW_POWER_2 = 3
    LOW_POWER_3 = 4
    LOW_POWER_4 = 5


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
        on_start_signal: Callable[[], None]=lambda: None,
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

    def set_output(self, output: PowerOutput, value: bool) -> None:
        """
        Turn off individual power output.
        """
        self._send_and_receive({
            'power-output': output.value,
            'power-level': value,
        })

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
