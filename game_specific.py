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

# Other places to look:
# - camera.py Marker object has some helper if statements
