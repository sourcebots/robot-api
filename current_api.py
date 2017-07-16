import robot
from robot import Robot

r = Robot()

r.motor_boards[0].m0.voltage = 1
r.motor_boards[0].m1.voltage = robot.COAST

