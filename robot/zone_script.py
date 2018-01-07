#!/usr/bin/env python3
"""
HOW TO USE THIS SCRIPT:

put this as an .autorun file in the root of the USB stick,
along with a file named zone-<X> where <X> is the id of the zone (0 to 3) to use.
(The file can be blank and should have no extension)
"""
import json
import socket
import time
from enum import Enum
from threading import Event

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)


class State(Enum):
    CONNECT = 1
    MESSAGE = 2
    DONE = 3


def poll(robot_root_path, zone_id, stop_event: Event = Event()):
    message = '{{"zone":{}, "mode":"competition"}}\n'.format(zone_id).encode('utf-8')
    state = State.CONNECT
    while not stop_event.is_set():
        try:
            if state is State.CONNECT:
                sock.connect(robot_root_path+"game/state")
                state = State.MESSAGE

            if state is State.MESSAGE:
                sock.sendall(message)
                resp = sock.recv(2048)
                resp = json.loads(resp.decode('utf-8'))
                if 'zone' in resp and resp['zone'] == zone_id:
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
    # Get all files named zone-1, zone-2, etc..
    id_files = glob.glob(str(path / "zone-*"))
    if not id_files:
        print("Could not find any zone ids (files like zone-1 or zone-0)")
        exit(0)
    id_file = id_files[0]
    if len(id_files) > 1:
        print("Warning, found more than 1 zone file!")
    # Get the first number in the filename
    zone_id = int(re.search(r'\d', id_file).group(0))
    print("ID:", zone_id)
    poll("/var/robotd/", zone_id)
