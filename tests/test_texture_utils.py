import numpy as np
import pytest

import sys
import importlib.util

spec = importlib.util.spec_from_file_location(
    "texture_utils",
    "blender_scatter_addon/texture_utils.py",
)
texture_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(texture_utils)

load_texture_as_grayscale = texture_utils.load_texture_as_grayscale
sample_texture = texture_utils.sample_texture
get_value_from_map = texture_utils.get_value_from_map


class MockImage:
    def __init__(self, w, h, pixels):
        self._size = (w, h)
        self._pixels = pixels

    @property
    def size(self):
        return self._size

    @property
    def pixels(self):
        return self._pixels


def test_sample_texture_returns_correct_value():
    tex = np.array([[0.0, 0.5], [1.0, 0.75]], dtype=np.float32)
    assert sample_texture(tex, 0.0, 0.0) == 0.0
    assert sample_texture(tex, 0.0, 0.999) == 1.0
    assert sample_texture(tex, 0.999, 0.0) == 0.5
    assert sample_texture(tex, 0.5, 0.5) == 0.75


def test_sample_texture_wraps_uv():
    tex = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=np.float32)
    assert sample_texture(tex, 1.5, 0.0) == sample_texture(tex, 0.5, 0.0)
    assert sample_texture(tex, 2.0, 0.0) == sample_texture(tex, 0.0, 0.0)
    assert sample_texture(tex, 0.0, 1.0) == sample_texture(tex, 0.0, 0.0)


def test_get_value_from_map_without_texture():
    val = get_value_from_map(None, 0.5, 0.5, default=0.42)
    assert val == 0.42


def test_get_value_from_map_with_texture():
    tex = np.array([[0.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    val = get_value_from_map(tex, 0.999, 0.999, default=0.0)
    assert val == 1.0


def test_load_texture_as_grayscale_returns_none_for_none():
    assert load_texture_as_grayscale(None) is None


def test_load_texture_as_grayscale_returns_none_for_zero_size():
    img = MockImage(0, 0, [])
    assert load_texture_as_grayscale(img) is None


def test_load_texture_as_grayscale_converts_correctly():
    w, h = 2, 2
    pixels = [0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5, 0.5, 0.5, 1.0, 0.0, 0.0, 0.0, 1.0]
    img = MockImage(w, h, pixels)
    result = load_texture_as_grayscale(img)
    assert result is not None
    assert result.shape == (h, w)
    assert result[0, 0] == pytest.approx(0.0)
    assert result[0, 1] == pytest.approx(1.0)
    assert result[1, 0] == pytest.approx(0.5)
    assert result[1, 1] == pytest.approx(0.0)
