# ***************************************************************************
#   NOTICE: IF YOU CHANGE THIS FILE PLEASE CHANGE ITS COUNTERPART IN ROBOTD
# ****************************************************************************
# Try to put all game specific code in here

WALL = set(range(28))  # 0 - 27

# 'Tin Can Rally'
# CENTRAL_RESERVATION = MarkerTag(set(range(28,40))) # 28 - 39
# TOKEN = MarkerTag(set())

# 'Collect'
POISON_TOKEN = {32}
SILVER_TOKEN = set(range(33, 53))
GOLD_TOKEN = set(range(53, 73))

TOKEN = POISON_TOKEN | SILVER_TOKEN | GOLD_TOKEN

# The following constants are used to define the marker sizes

MARKER_SIZES = {}
MARKER_SIZES.update({m: (0.25, 0.25) for m in WALL})  # | CENTRAL_RESERVATION
MARKER_SIZES.update({m: (0.1, 0.1) for m in TOKEN})
