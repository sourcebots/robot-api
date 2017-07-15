from robot.robot import Robot
from robot import COAST

robot = Robot()

robot.motor_boards[0].m0.voltage = 1
robot.motor_boards[0].m1.voltage = COAST

