# addresses from https://datacrystal.romhacking.net/wiki/Pok%C3%A9mon_Red/Blue:RAM_map
# https://github.com/pret/pokered/blob/91dc3c9f9c8fd529bb6e8307b58b96efa0bec67e/constants/event_constants.asm

# Number of Pokémon currently in the player's party.
PARTY_SIZE_ADDRESS = 0xD163

# Player's in-map x and y coordinates.
X_POS_ADDRESS, Y_POS_ADDRESS = 0xD362, 0xD361

# Identifier of the current map.
MAP_N_ADDRESS = 0xD35E

# Bitfield representing obtained badges.
BADGE_COUNT_ADDRESS = 0xD356

# Addresses storing the level for each party Pokémon.
LEVELS_ADDRESSES = [0xD18C, 0xD1B8, 0xD1E4, 0xD210, 0xD23C, 0xD268]

# Memory locations for each party slot's Pokémon ID.
PARTY_ADDRESSES = [0xD164, 0xD165, 0xD166, 0xD167, 0xD168, 0xD169]

# Locations of the opponent team Pokémon levels.
OPPONENT_LEVELS_ADDRESSES = [0xD8C5, 0xD8F1, 0xD91D, 0xD949, 0xD975, 0xD9A1]

# Start and end addresses of the game's event flag table.
EVENT_FLAGS_START_ADDRESS = 0xD747
EVENT_FLAGS_END_ADDRESS = 0xD886

# Flag used after purchasing the Pewter Museum ticket.
MUSEUM_TICKET_ADDRESS = 0xD754

# Current and maximum HP values for each party Pokémon.
HP_ADDRESSES = [0xD16C, 0xD198, 0xD1C4, 0xD1F0, 0xD21C, 0xD248]
MAX_HP_ADDRESSES = [0xD18D, 0xD1B9, 0xD1E5, 0xD211, 0xD23D, 0xD269]

# BCD-encoded money value split across three bytes.
MONEY_ADDRESS_1 = 0xD347
MONEY_ADDRESS_2 = 0xD348
MONEY_ADDRESS_3 = 0xD349
