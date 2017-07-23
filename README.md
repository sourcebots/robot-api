# Robot

This is the userspace API for the robot, which is what students will interface with to program their robots

# How to use

Currently the code is designed to be imported then ran, however we hope to move the robot initialisation into the `__init__.py` to not need this

Markers can be seen by:

``` python
markers = r.cameras[0].see()
# or
markers = r.camera.see()
```

Servo positions can be set by:

``` python
r.servo_boards[0].ports[0].position = -1
# or
r.servo_board.ports[0].position = -1
```

Motors can be set with:

``` python
r.motor_boards[0].m0.voltage = -1
# or
r.motor_board.m0.voltage = -1
```

The corner the robot is going to start in can be gotten with:

``` python
r.corner
# or
r.game.corner
```

# Testing

the robot-api tests require `robotd` (available at [https://github.com/sourcebots/robotd] ) in the python path (ie in the same directory as the `tests` folder ) Personally I create a soft link to the robotd directory

to run the tests, simply run `nosetests` (requires the `nose` python package) and it will run all tests


# Corner ID script

To run the corner script on USB insert, you must install the runusb script in [https://github.com/sourcebots/runusb]

The corner ID script can be found at `robot/corner_script.py`, to use this for real robots you must put that script in a USB stick
In the same directory as a file named `corner_<x>`, where `<x>` is the ID of the corner the robot should be with.
