# Robot

[![CircleCI](https://circleci.com/gh/sourcebots/robot-api.svg?style=shield)](https://circleci.com/gh/sourcebots/robot-api)

This is the userspace API for the robot, which is what students will interface with to program their robots.

# Installation instructions

## Building the debian package

``` bash
# Install build tools:
sudo apt install build-essential devscripts debhelper equivs

# cd to the root of this project
cd path/to/robot-apis

# Install dependencies
sudo mk-build-deps -ir

# Build the package:
debuild -uc -us

```

## Installing the debian package

After building, the .deb file should appear in the parent directory, just run

``` bash
# Go up a directory (there should be a .deb file here)
cd ..
# Install the package
sudo dpkg -i robot-api_0_all.deb
```

to install the package

# Testing

The robot-api tests require `robotd` (available at [https://github.com/sourcebots/robotd] ) installed. 

To run the tests, simply run `nosetests` (requires the `nose` python package) and it will run all tests.


# Zone ID script

To run the zone script on USB insert, you must install the runusb script in [https://github.com/sourcebots/runusb]

The zone ID script can be found at `robot/zone_script.py`, to use this for real robots you must put that script in a USB stick in the same directory as a file named `zone-<x>`, where `<x>` is the ID of the zone the robot should be with.
