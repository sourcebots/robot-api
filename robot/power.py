import json
from pathlib import Path

from robot.board import Board


class PowerBoard(Board):
    BUZZ_NOTES = {
        'c': 261,
        'd': 294,
        'e': 329,
        'f': 349,
        'g': 392,
        'a': 440,
        'b': 493,
        'uc': 523
    }

    def __init__(self, socket_path):
        super().__init__(socket_path)
        self._serial = Path(socket_path).stem

    @property
    def serial(self):
        """
        Serial number for the board
        """

        return self._serial

    def power_on(self):
        """
        Turn on power to all power board outputs
        """

        self.send_and_receive({'power': True})

    def power_off(self):
        """
        Turn off power to all power board outputs
        """
        self.send_and_receive({'power': False})

    def set_start_led(self, value):
        self.send_and_receive({'start-led': bool(value)})

    @property
    def start_button_pressed(self):
        """
        Read the status of the start button.
        """

        status = self.send_and_receive({})
        return status["start-button"]

    def buzz(self, duration, *, note=None, frequency=None):
        if note is None and frequency is None:
            raise ValueError("Either note or frequency must be provided")
        if note is not None and frequency is not None:
            raise ValueError("Only provide note or frequency")
        if note is not None:
            frequency = self.BUZZ_NOTES[note.lower()]
        if frequency is None:
            raise ValueError("Invalid frequency")
        self.send_and_receive({'buzz': {'frequency': frequency, 'duration': duration * 1000}})
