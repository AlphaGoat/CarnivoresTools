"""
Utilities for working with images and converting
between image formats
"""
import numpy as np
from PIL import Image
from numpy.typing import NDArray


def load_tga(image_path):
    """
    Load image in TGA format
    """
    image = Image.open(image_path)
    return image


def convert_rgb555_to_rgb888(im_rgb555: NDArray[np.uint16]) -> NDArray[np.uint8]:
    """
    Convert 16-bit bitmap in RGB555 format to RGB888 24-bit bitmap
    """
    mask5 = 0b011111
    b = (im_rgb555 & mask5) << 3
    g = ((im_rgb555 >> 5) & mask5) << 3
    r = ((im_rgb555 >> (5 + 5)) & mask5) << 3

    return np.dstack((r, g, b)).astype(np.uint8)


def convert_rgb565_to_rgb888(im_rgb565: NDArray[np.uint16]) -> NDArray[np.uint8]:
    """
    Convert 16-bit bitmap in RGB565 format to RGB888 24-bit bitmap
    """
    r = (im_rgb565 >> 11) & 0x1F
    g = (im_rgb565 >> 5) & 0x3F
    b = im_rgb565 & 0x1F

    r = (r * 255) // 31
    g = (g * 255) // 63
    b = (b * 255) // 31

    r = (im_rgb565 >> 11) & 0x1F
    g = (im_rgb565 >> 5) & 0x3F
    b = im_rgb565 & 0x1F

    r = (r * 255) // 31
    g = (g * 255) // 63
    b = (b * 255) // 31

    return np.dstack((r, g, b)).astype(np.uint8)
