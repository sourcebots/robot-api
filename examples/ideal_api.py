from robot.robot import Robot

r = Robot()

left_motor = r.motor_boards['sgkjn'].m0
# m1.voltage is from -1 to 1
# EXCEPT it automatically brakes unless set to ROBOT.COAST
r.motor_boards['sgkjn'].m1.voltage = r.COAST
r.motor_boards[0].m1.voltage = 1.0
r.motor_boards[0].m1.voltage = 0  # 0 is indistinguishable from braking
r.motor_boards[0].m1.voltage = r.BRAKE  # NOTE, if this value is read back it will return 0, not BRAKE
assert (r.BRAKE == 0)
try:
    # Should Error:
    r.motor_boards[0].m1.voltage = 1.01
    r.motor_boards[0].m1.voltage = -1.01
    r.motor_boards[0].m1.voltage = "robot go fast plz"
except:
    pass

r.servo_boards[0]._servos[2].position = -1

# Results are sorted by distance
# r.see() returns a subclass of sequence (abstract base classes), which can then error things.
markers = r.see()

marker = markers[0]

if marker.type == r.ARENA:
    if marker.distance_metres > 1:
        if marker.polar.rot_x > 0:
            print("it's more than 1m away in some direction!")
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


# Indexing tokens
tokens = r.cameras[0].see()

if len(tokens) == 0:
    try:
        # Will Error
        tokens[0]
    except IndexError:
        # Shows a fancy "you're indexing an empty array" error! ooOooh!
        pass
