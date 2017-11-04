import json
from robot.board import Board


class PowerBoard(Board):
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
