"""
Class that defines the visible "world space".
Stores all of the textures in the map as well
as grid coordinates telling us where the place 
textures. We pass this to the camera to let the
rendering engine know what exactly we want to
render

Author: Peter Thomas
Date: 26 June 2024
"""
import numpy as np
from typing import List, Tuple
from numpy.typing import NDArray
from utils import MAP, RSCHeader, Object, Texture, SkyBlock


class Map():
    def __init__(self,
        map: MAP,
        rsc_header: RSCHeader,
        textures: List[Texture],
        objects: List[Object],
        skyblock: SkyBlock,
        map_size: Tuple[int, int]=(1024, 1024)
    ):
        self.map = map
        self.rsc_header = rsc_header
        self.textures = textures
        self.objects = objects
        self.skyblock = skyblock
        self.map_size = map_size

    def fetch_textures_based_on_coords(self, coords: NDArray[int]) -> Tuple[List[Texture], NDArray]:
        """
        Fetch textures to render based on a given set of
        grid coordinates

        Args:
            coords (ndarray): Nx3 array where N are the number
            of grids to fetch textures for, where each grid
            coordinate is given as (x, y, z)
        Returns:
            textures: List of textures from .rsc
            grid_positions: grid positions of textures
        """
        # Clip coordinates that are outside of visible world space
        out_of_map_mask = (coords[:, 0] < 0 |
                           coords[:, 1] < 0 |
                           coords[:, 0] < self.map_size[0] - 1 |
                           coords[:, 1] < self.map_size[1] - 1)
        in_map_coords = coords[out_of_map_mask]

        # Get texture indices from MAP object and heights for textures
        texture_indices = self.map.TMap1[coords[:, 0], coords[:, 1]]
        height_map = self.HMap[coords[:, 0], coords[:, 1]]

        # Filter out textures that are not visible in the z-axis
        out_of_vis_mask = np.isin(height_map, coords[:, 2])

        vis_height_map = height_map[out_of_vis_mask]
        vis_texture_indices = texture_indices[out_of_vis_mask]
        vis_coords = coords[out_of_vis_mask]

        # Fetch textures based on texture indices
        vis_textures = self.textures[vis_texture_indices]

        # Get grid positions of visible textures
        grid_positions = np.stack([coords[:, 0], coords[:, 1], vis_height_map], axis=-1)

        return vis_textures, grid_positions

    def fetch_objects_based_on_coords(self, coords: NDArray[int]) -> Tuple[List[Object], NDArray]:
        """
        Fetch 3-D objects to render based on given set of grid coordinates

        Args:
            coords (ndarray): Nx3 array where N are the number
            of grids to fetch textures for, where each grid
            coordinate is given as (x, y, z)
        Returns:
            textures: List of textures from .rsc
            grid_positions: grid positions of textures
        """
        # Clip coordinates that are outside of visible world space
        out_of_map_mask = (coords[:, 0] < 0 |
                           coords[:, 1] < 0 |
                           coords[:, 0] < self.map_size[0] - 1 |
                           coords[:, 1] < self.map_size[1] - 1)
        in_map_coords = coords[out_of_map_mask]

        # Get object indices from MAP object and heights for textures
        object_indices = self.map.OMap[coords[:, 0], coords[:, 1]]
        height_map = self.HMap[coords[:, 0], coords[:, 1]]

        # Filter out textures that are not visible in the z-axis
        out_of_vis_mask = np.isin(height_map, coords[:, 2])

        vis_height_map = height_map[out_of_vis_mask]
        vis_object_indices = object_indices[out_of_vis_mask]
        vis_coords = coords[out_of_vis_mask]

        # Fetch objects based on object indices
        vis_objects = self.objects[vis_object_indices]

        # Get grid positions of visible objects
        grid_positions = np.stack([coords[:, 0], coords[:, 1], vis_height_map], axis=-1)

        return vis_objects, grid_positions
