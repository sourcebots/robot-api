# Robot

This is the userspace API for the robot, which is what students will interface with to program their robots

# How to use

Currently the code is designed to be imported then ran, however we hope to move the robot initialisation into the __init__.py to not need this

``` python
from robot import Robot
robot = Robot() # TODO move this to the __init__.py so students don't need to do it

robot.motor_boards[0].m0.voltage = 1
```
