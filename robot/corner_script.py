#!/usr/bin/env python3
"""
HOW TO USE THIS SCRIPT:

put this as an .autorun file in the root of the USB stick,
along with a file named corner_<X> where <X> is the id of the corner (0 to 3) to use.
(The file can be blank and should have no extension)
"""
import socket
import json

import time

from enum import Enum
from threading import Event


sock = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)


class State(Enum):
    CONNECT = 1
    MESSAGE = 2
    DONE = 3


def poll(robot_root_path, corner_id, stop_event: Event = None):
    message = '{{"corner":{}, "mode":"competition"}}\n'.format(corner_id).encode('utf-8')
    state = State.CONNECT
    while not stop_event.is_set():
        try:
            if state is State.CONNECT:
                sock.connect(robot_root_path+"game/state")
                state = State.MESSAGE

            if state is State.MESSAGE:
                sock.send(message)
                resp = sock.recv(2048)
                resp = json.loads(resp)
                if 'corner' in resp and resp['corner'] == corner_id:
                    print("done")
                    state = State.DONE
                else:
                    state = State.MESSAGE

            if state is State.DONE:
                time.sleep(1)
                state = State.MESSAGE

        except (ConnectionRefusedError, OSError):
            time.sleep(0.1)
            print("cant connect")
            state = State.CONNECT


if __name__ == "__main__":
    import os
    import glob
    import re
    from pathlib import Path
    path = Path(os.path.dirname(os.path.realpath(__file__)))
    # Get all files named corner_1, corner_2, etc..
    corner_file = glob.glob(str(path/"corner*")).group(0)
    # Get the first number in the filename
    corner_id = int(re.search(r'\d', corner_file))
    poll("/var/robotd/", corner_id)
