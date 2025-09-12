import sys
import types
import numpy as np
import pytest
from enum import IntEnum, auto

class DummyWindowEvent(IntEnum):
    PRESS_ARROW_DOWN = auto()
    PRESS_ARROW_LEFT = auto()
    PRESS_ARROW_RIGHT = auto()
    PRESS_ARROW_UP = auto()
    PRESS_BUTTON_A = auto()
    PRESS_BUTTON_B = auto()
    PRESS_BUTTON_START = auto()
    RELEASE_ARROW_DOWN = auto()
    RELEASE_ARROW_LEFT = auto()
    RELEASE_ARROW_RIGHT = auto()
    RELEASE_ARROW_UP = auto()
    RELEASE_BUTTON_A = auto()
    RELEASE_BUTTON_B = auto()
    RELEASE_BUTTON_START = auto()

class DummyScreen:
    def __init__(self):
        self.ndarray = np.zeros((144, 160, 3), dtype=np.uint8)

class DummyPyBoy:
    def __init__(self, *args, **kwargs):
        self.memory = bytearray(0x10000)
        self.screen = DummyScreen()
    def set_emulation_speed(self, speed):
        pass
    def load_state(self, f):
        pass
    def send_input(self, action):
        self.last_input = action
    def tick(self, steps=1, render=True):
        pass

def _install_pyboy(monkeypatch):
    pyboy_module = types.ModuleType("pyboy")
    utils_module = types.ModuleType("pyboy.utils")
    utils_module.WindowEvent = DummyWindowEvent
    pyboy_module.PyBoy = DummyPyBoy
    pyboy_module.utils = utils_module
    sys.modules["pyboy"] = pyboy_module
    sys.modules["pyboy.utils"] = utils_module

@pytest.fixture(autouse=True)
def mock_pyboy(monkeypatch):
    _install_pyboy(monkeypatch)
    yield
    sys.modules.pop("pyboy", None)
    sys.modules.pop("pyboy.utils", None)
