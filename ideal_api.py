from robot.robot import Robot

robot = Robot()

left_motor = robot.motor_boards['sgkjn'].m0
# m1.voltage is from -1 to 1
# EXCEPT it automatically brakes unless set to ROBOT.COAST
robot.motor_boards['sgkjn'].m1.voltage = robot.COAST
robot.motor_boards[0].m1.voltage = 1.0
robot.motor_boards[0].m1.voltage = 0  # 0 is indistinguishable from braking
robot.motor_boards[0].m1.voltage = robot.BRAKE  # NOTE, if this value is read back it will return 0, not BRAKE
assert(robot.BRAKE == 0)
# Will Error:
try:
    robot.motor_boards[0].m1.voltage = 1.01
    robot.motor_boards[0].m1.voltage = -1.01
    robot.motor_boards[0].m1.voltage = "robot go fast plz"
except:
    pass


robot.servo_boards[0].socket[2].position = -1

# Results are sorted by distance
# r.see() returns a subclass of sequence (abstract base classes), which can then error things.
markers = robot.see()

marker = markers[0]

if marker.type == robot.ARENA:
    if marker.distance_metres > 1:
        pass
        # decomposeHomographyMat:
        # - decomposeHomography:
        # - normalize:
        #     return K.inv() * H * K
        # - removeScale
        #   Mat
        #   W;
        #   SVD::compute(_Hnorm, W);
        #   _Hnorm = _Hnorm * (1.0 / W.at < double > (1));
        # - Inria decompose
        #   Line 305.
        #   - findRmatFrom_tstar_n
        #   R = H(I - (2 / v) * te_star * ne_t)
