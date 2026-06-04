import numpy as np
from typing import Optional


def load_texture_as_grayscale(image) -> Optional[np.ndarray]:
    if image is None:
        return None
    w = image.size[0]
    h = image.size[1]
    if w == 0 or h == 0:
        return None
    pixels = np.array(image.pixels[:], dtype=np.float32).reshape(h, w, 4)
    grayscale = 0.299 * pixels[:, :, 0] + 0.587 * pixels[:, :, 1] + 0.114 * pixels[:, :, 2]
    return grayscale


def sample_texture(tex: np.ndarray, u: float, v: float) -> float:
    h, w = tex.shape
    x = min(int(u % 1.0 * w), w - 1)
    y = min(int(v % 1.0 * h), h - 1)
    return float(tex[y, x])


def get_value_from_map(tex: Optional[np.ndarray], u: float, v: float, default: float) -> float:
    if tex is None:
        return default
    return sample_texture(tex, u, v)
