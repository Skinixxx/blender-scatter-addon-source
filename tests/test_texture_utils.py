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


class TestSampleTexture:

    def test_returns_correct_value(self):
        tex = np.array([[0.0, 0.5], [1.0, 0.75]], dtype=np.float32)
        assert sample_texture(tex, 0.0, 0.0) == 0.0
        assert sample_texture(tex, 0.0, 0.999) == 1.0
        assert sample_texture(tex, 0.999, 0.0) == 0.5
        assert sample_texture(tex, 0.5, 0.5) == 0.75

    def test_wraps_uv(self):
        tex = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=np.float32)
        assert sample_texture(tex, 1.5, 0.0) == sample_texture(tex, 0.5, 0.0)
        assert sample_texture(tex, 2.0, 0.0) == sample_texture(tex, 0.0, 0.0)

    def test_negative_uv(self):
        tex = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=np.float32)
        assert sample_texture(tex, -0.5, 0.0) == sample_texture(tex, 0.5, 0.0)
        assert sample_texture(tex, 0.0, -0.001) == sample_texture(tex, 0.0, 0.999)

    def test_wrap_at_integer_boundary(self):
        tex = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=np.float32)
        assert sample_texture(tex, 1.0, 0.0) == sample_texture(tex, 0.0, 0.0)
        assert sample_texture(tex, 0.0, 1.0) == sample_texture(tex, 0.0, 0.0)

    def test_single_pixel_texture(self):
        tex = np.array([[0.75]], dtype=np.float32)
        assert sample_texture(tex, 0.0, 0.0) == 0.75
        assert sample_texture(tex, 0.999, 0.999) == 0.75
        assert sample_texture(tex, 100.0, 100.0) == 0.75

    def test_single_row_texture(self):
        tex = np.array([[0.1, 0.5, 0.9]], dtype=np.float32)
        assert sample_texture(tex, 0.0, 0.0) == pytest.approx(0.1)
        assert sample_texture(tex, 0.5, 0.0) == pytest.approx(0.5)
        assert sample_texture(tex, 0.999, 0.0) == pytest.approx(0.9)

    def test_single_column_texture(self):
        tex = np.array([[0.1], [0.5], [0.9]], dtype=np.float32)
        assert sample_texture(tex, 0.0, 0.0) == pytest.approx(0.1)
        assert sample_texture(tex, 0.0, 0.5) == pytest.approx(0.5)
        assert sample_texture(tex, 0.0, 0.999) == pytest.approx(0.9)


class TestGetValueFromMap:

    def test_without_texture_returns_default(self):
        val = get_value_from_map(None, 0.5, 0.5, default=0.42)
        assert val == 0.42

    def test_with_texture_returns_sampled(self):
        tex = np.array([[0.0, 0.0], [0.0, 1.0]], dtype=np.float32)
        val = get_value_from_map(tex, 0.999, 0.999, default=0.0)
        assert val == 1.0

    def test_default_is_used_when_texture_none(self):
        assert get_value_from_map(None, 0.0, 0.0, default=1.0) == 1.0
        assert get_value_from_map(None, 0.5, 0.5, default=0.0) == 0.0

    def test_with_empty_texture_returns_default(self):
        with pytest.raises((ValueError, IndexError)):
            tex = np.array([[]], dtype=np.float32)
            get_value_from_map(tex, 0.0, 0.0, default=0.5)

    def test_out_of_range_uv_does_not_crash(self):
        tex = np.ones((4, 4), dtype=np.float32)
        val = get_value_from_map(tex, 999.0, -999.0, default=0.0)
        assert val == pytest.approx(1.0)


class TestLoadTextureAsGrayscale:

    def test_returns_none_for_none(self):
        assert load_texture_as_grayscale(None) is None

    def test_returns_none_for_zero_size(self):
        img = MockImage(0, 0, [])
        assert load_texture_as_grayscale(img) is None

    def test_converts_correctly(self):
        w, h = 2, 2
        pixels = [0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                  0.5, 0.5, 0.5, 1.0, 0.0, 0.0, 0.0, 1.0]
        img = MockImage(w, h, pixels)
        result = load_texture_as_grayscale(img)
        assert result is not None
        assert result.shape == (h, w)
        assert result[0, 0] == pytest.approx(0.0)
        assert result[0, 1] == pytest.approx(1.0)
        assert result[1, 0] == pytest.approx(0.5)
        assert result[1, 1] == pytest.approx(0.0)

    def test_zero_texture(self):
        w, h = 2, 2
        pixels = [0.0, 0.0, 0.0, 1.0] * 4
        img = MockImage(w, h, pixels)
        result = load_texture_as_grayscale(img)
        assert result is not None
        assert result.shape == (h, w)
        assert np.allclose(result, 0.0)

    def test_white_texture(self):
        w, h = 2, 2
        pixels = [1.0, 1.0, 1.0, 1.0] * 4
        img = MockImage(w, h, pixels)
        result = load_texture_as_grayscale(img)
        assert np.allclose(result, 1.0)

    def test_negative_pixel_values(self):
        w, h = 1, 1
        pixels = [-0.5, -0.5, -0.5, 1.0]
        img = MockImage(w, h, pixels)
        result = load_texture_as_grayscale(img)
        assert result is not None
        assert result[0, 0] < 0
