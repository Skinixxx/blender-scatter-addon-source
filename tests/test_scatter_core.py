import pytest
import numpy as np
import importlib.util

spec = importlib.util.spec_from_file_location(
    "texture_utils",
    "blender_scatter_addon/texture_utils.py",
)
texture_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(texture_utils)

get_value_from_map = texture_utils.get_value_from_map


class TestScatterCoreUtils:
    def test_get_value_from_map_default(self):
        assert get_value_from_map(None, 0.0, 0.0, 0.5) == 0.5

    def test_get_value_from_map_sampling(self):
        tex = np.ones((4, 4), dtype=np.float32) * 0.8
        assert abs(get_value_from_map(tex, 0.0, 0.0, 0.0) - 0.8) < 1e-6
