import robot
from robot import Robot

r = Robot()

r.motor_boards[0].m0.voltage = 1
r.motor_boards[0].m1.voltage = robot.COAST

tokens = r.cameras[0].see()

if len(tokens) == 0:
    try:
        # Will Error
        tokens[0]
    except IndexError:
        # Shows a fancy "you're indexing an empty array" error! ooOooh!
        pass
else:
    if tokens[0].distance_metres > 1:
        print("too far!!")
    if tokens[0].polar.rot_x > 1:
        print("In some direction!")