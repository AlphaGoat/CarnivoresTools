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

    def render(self, world):
        """
        Render 3-D worldspace visible by camera

        :params:
            world (World): world object that defines
                the current game state.
        """
        # Get visible coordinates 
        vis_coords = self.get_render_coords()

        # Retrieve textures and objects that are visible to our peon player
        textures, grid_positions = world.fetch_textures_based_on_coords(vis_coords) 
#        objects = world.fetch_objects_based_on_coords(vis_coords)

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
    def get_bounds_of_view_furstrum(
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
        # Get the height / width of the view window at the edge
        # of the view distance
        far_width = far_height = 2 * math.tan( math.radians(fov) / 2 ) * view_distance

        # Get coordinates of the point at the center of the view
        # window at the edge of the view distance
        x = view_distance * math.sin( math.radians(90.0 - elevation) ) * \
                math.cos( math.radians(azimuth) )
        y = view_distance * math.sin( math.radians(90.0 - elevation) ) * \
                math.sin( math.radians(azimuth) )
        z = view_distance * math.cos( math.radians(90.0 - elevation) )

        return (x, y, z), (far_width, far_height)

    @staticmethod
    def get_planes_composing_view_furstrum():
        pass


