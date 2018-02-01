import time

from robot.board import Board


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

    def set_start_led(self, value):
        """Set the state of the start LED."""
        self._send_and_receive({'start-led': bool(value)})

    @property
    def start_button_pressed(self):
        """
        Read the status of the start button.
        """

        status = self._send_and_receive({})
        return status["start-button"]

    def wait_start(self):
        """
        Block until the start button is pressed.
        """
        start_time = time.time()
        led_value = True
        while not self.start_button_pressed:
            if time.time() - start_time >= 0.1:
                led_value = not led_value
                start_time = time.time()
                self.set_start_led(led_value)
        self.set_start_led(False)

    def buzz(self, duration, *, note=None, frequency=None):
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
