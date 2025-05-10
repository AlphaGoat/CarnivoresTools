import numpy as np
from numpy.typing import NDArray


def convert_uint16_to_bit_string(val: np.uint16):
    return np.unpackbits(val.view(np.uint8)).astype(bool)


def get_bisecting_triangle_pts_from_grid_dims(grid_height, grid_width):
    triangles_1 = []
    triangles_2 = []
    for y in range(grid_height):
        for x in range(grid_width):
            tri_pts_1 = (x + y * (grid_height + 1), x + 1 + y * (grid_height + 1), x + (y + 1) * (grid_height + 1))
            tri_pts_2 = (x + 1 + y * (grid_height + 1), x + 1 + (y + 1) * (grid_height + 1), x + (y + 1) * (grid_height + 1))
            triangles_1.append(tri_pts_1)
            triangles_2.append(tri_pts_2)
    import pdb; pdb.set_trace()
    return triangles_1, triangles_2


def get_bisecting_triangles_from_grid(grid_height, grid_width):
    triangles_1 = np.empty((grid_height - 1, grid_width - 1, 3), dtype=int)
    triangles_2 = np.empty((grid_height - 1, grid_width - 1, 3), dtype=int)

    r = np.arange(grid_height * grid_width).reshape(grid_height, grid_width)

    triangles_1[..., 0] = r[:-1, :-1]
    triangles_2[..., 0] = r[:-1, 1:]
    triangles_1[..., 1] = r[:-1, 1:]
    triangles_2[..., 1] = r[1:, 1:]
    triangles_1[..., 2] = r[1:, :-1]
    triangles_2[..., 2] = r[1:, :-1]

    triangles_1 = triangles_1.reshape(-1, 3)
    triangles_2 = triangles_2.reshape(-1, 3)

#    triangles_1_y = (triangles_1 // grid_height)[..., np.newaxis]
#    triangles_1_x = (triangles_1 % grid_width)[..., np.newaxis]
#    triangles_1 = np.concatenate([triangles_1_y, triangles_1_x], axis=-1)
#
#    triangles_2_y = (triangles_2 // grid_height)[..., np.newaxis]
#    triangles_2_x = (triangles_2 % grid_width)[..., np.newaxis]
#    triangles_2 = np.concatenate([triangles_2_y, triangles_2_x], axis=-1)

    return triangles_2, triangles_2


def bitreverse16(x: NDArray[np.uint16]):
    """
    Reverse bits of uint16 numpy array
    """
    x = ((x & 0x00FF) << 8) | ((x & 0xFF00) >> 8)
    x = ((x & 0x0F0F) << 4) | ((x & 0xF0F0) >> 4)
    x = ((x & 0x3333) << 2) | ((x & 0xCCCC) >> 2)
    x = ((x & 0x5555) << 1) | ((x & 0xAAAA) >> 1)

    return x


def get_coordinates_in_solid_angle(
    elevation: float,
    azimuth: float,
    view_distance: int,
):
    """
    Get all coordinates contained within a solid
    angle (FOV projected from camera out on spherical
    view distance)
    """
    pass
