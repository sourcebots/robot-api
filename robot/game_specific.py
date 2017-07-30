# ***************************************************************************
#   NOTICE: IF YOU CHANGE THIS FILE PLEASE CHANGE ITS COUNTERPART IN ROBOTD
# ****************************************************************************
# Try to put all game specific code in here

WALL = set(range(0, 28))  # 0 - 27

# 'Tin Can Rally'
CENTRAL_RESERVATION = set(range(28, 40))
TOKEN = set(range(100, 200))

# The following constants are used to define the marker sizes

MARKER_SIZES = {}
MARKER_SIZES.update({m: (0.25, 0.25) for m in (WALL | CENTRAL_RESERVATION)})
MARKER_SIZES.update({m: (0.8, 0.8) for m in TOKEN})
