import numpy as np
import importlib
import sys
import types


def load_env_module():
    """Import RedGymEnv from v3 with stubbed dependencies."""
    stubs = {
        "skimage": types.ModuleType("skimage"),
        "skimage.transform": types.ModuleType("skimage.transform"),
        "matplotlib": types.ModuleType("matplotlib"),
        "matplotlib.pyplot": types.ModuleType("matplotlib.pyplot"),
        "pyboy": types.ModuleType("pyboy"),
        "pyboy.utils": types.ModuleType("pyboy.utils"),
        "mediapy": types.ModuleType("mediapy"),
        "einops": types.ModuleType("einops"),
        "gymnasium": types.ModuleType("gymnasium"),
    }

    stubs["skimage"].transform = stubs["skimage.transform"]
    stubs["skimage.transform"].downscale_local_mean = lambda *a, **k: None

    stubs["matplotlib"].pyplot = stubs["matplotlib.pyplot"]

    stubs["pyboy"].PyBoy = object
    stubs["pyboy.utils"].WindowEvent = object

    stubs["mediapy"].write_video = lambda *a, **k: None
    stubs["einops"].repeat = lambda *a, **k: None

    class _Env:  # minimal gymnasium.Env stub
        pass

    stubs["gymnasium"].Env = _Env
    stubs["gymnasium"].spaces = types.SimpleNamespace(
        Box=object,
        Dict=object,
        MultiBinary=object,
        MultiDiscrete=object,
        Discrete=object,
    )

    for name, module in stubs.items():
        sys.modules.setdefault(name, module)

    return importlib.import_module("v3.red_gym_env_v3")


RedGymEnv = load_env_module().RedGymEnv


def make_env(freqs=4):
    env = RedGymEnv.__new__(RedGymEnv)
    env.enc_freqs = freqs
    return env


def test_bit_count():
    env = make_env()
    assert env.bit_count(0b0) == 0
    assert env.bit_count(0b1011) == 3
    assert env.bit_count(255) == 8


def test_fourier_encode_zero():
    env = make_env(4)
    result = env.fourier_encode(0)
    assert np.allclose(result, np.zeros(4))


def test_fourier_encode_values():
    env = make_env(3)
    val = np.pi / 2
    expected = np.sin(val * 2 ** np.arange(3))
    assert np.allclose(env.fourier_encode(val), expected)
