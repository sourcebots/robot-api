from robot.robot import Robot

robot = Robot()

# Set a motor of id 1 to 100.
left_motor = robot.motor_boards['sgkjn'].m0
# m1.voltage is from -1 to 1
# EXCEPT it automatically brakes unless set to ROBOT.COAST
robot.motor_boards['sgkjn'].m1.voltage = robot.COAST

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
