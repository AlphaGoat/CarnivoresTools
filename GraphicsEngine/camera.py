"""
Class defining player camera

Author: Peter Thomas
Date: 19 May 2024
"""
import math
import numpy as np
from typing import Tuple


class Camera():
    def __init__(
        self,
        pos_x: int,
        pos_y: int,
        pos_z: int,
        fov: float,
        azimuth: float,
        elevation: float,
        render_distance: int,
    ):
        """
        Initializes a camera that defines the
        viewpoint of a player character and defines
        the bounds of the 3-d render

        :params:
            pos_x (int): X-position of the camera
            pos_y (int): Y-position of the camera
            pos_z (int): Z-position of the camera
            fov (float): Field-of-view (in degrees) of the 
                player character.
            azimuth (float): Azimuthal direction of the camera
                wrt a vertical axis reaching up from the given
                position.
            elevation (float): Elevation angle of the camera
            render_distance (int): number of tiles to render in 
            each direction.
        """
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.pos_z = pos_z
        self.fov = fov
        self.azimuth = azimuth
        self.elevation = elevation
        self.render_distance = render_distance

    def generate_visible_mesh(self, world):
        """
        Generate mesh of objects that are visible

        :params:
            world (World): world object that defines
                the current game state.
        """
        # Get visible coordinates 
        vis_coords = self.get_render_coords()

        # Retrieve textures and objects that are visible to our peon player
        textures, grid_positions = world.fetch_textures_based_on_coords(vis_coords) 

        # for each texture, define vertices and convert
        # grid positions to coordinates in the camera
        for tex, grid_pos in zip(textures, grid_positions):

            pass

        pass


    def get_render_coords(self) -> Tuple[int, int, int]:
        """
        Get the grid spaces that are visible to the character based
        on their current position
        """
        # Get grid coordinate at center of frame
        z = math.ceil(self.render_distance * math.sin(math.radians(self.elevation)))
        v = self.render_distance * math.cos(self.elevation)
        y = math.ceil(v * math.cos(self.azimuth))
        x = math.ceil(v * math.sin(self.azimuth))

        # Based on FOV, get coordinates in grid space 
        top_z = math.ceil(self.render_distance * \
                math.sin(math.radians(self.elevation + (1/2) * self.fov)))
        top_v = self.render_distance * math.cost

        return (x, y, z)

    @staticmethod
    def get_coordinates_in_solid_angle(
        elevation: float,
        azimuth: float,
        view_distance: int,
        fov: float,
    ):
        """
        Get all coordinates contained within a solid
        angle (FOV projected from camera out on spherical
        view distance)
        """
        # Get the edge coordinates at the furthest extent
        # of the view distance in cartesian coordinates
        theta0 = azimuth - (1/2) * fov
        theta1 = azimuth + (1/2) * fov

        psi0 = 90.0 - elevation + (1/2) * fov
        psi1 = 90.0 - elevation - (1/2) * fov

        x00 = 

