import numpy as np
from v2.red_gym_env_v2 import RedGymEnv


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
