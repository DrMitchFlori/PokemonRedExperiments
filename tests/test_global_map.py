import pytest
from global_map import (
    local_to_global,
    MAP_DATA,
    GLOBAL_MAP_SHAPE,
    MAP_ROW_OFFSET,
    MAP_COL_OFFSET,
)


def test_local_to_global_valid():
    map_n = 0
    r, c = 5, 10
    gy, gx = local_to_global(r, c, map_n)
    map_x, map_y = MAP_DATA[map_n]["coordinates"]
    assert gy == r + map_y + MAP_ROW_OFFSET
    assert gx == c + map_x + MAP_COL_OFFSET


def test_local_to_global_invalid():
    gy, gx = local_to_global(0, 0, 9999)
    assert (gy, gx) == (GLOBAL_MAP_SHAPE[0] // 2, GLOBAL_MAP_SHAPE[1] // 2)
