"""
Class defining player camera

Author: Peter Thomas
Date: 19 May 2024
"""


class Camera():
    def __init__(
        self,
        pos_x: int,
        pos_y: int,
        pos_z: int,
        azimuth: float,
        elevation: float,
    ):
        """
        Initializes a camera that defines the
        viewpoint of a player character and defines
        the bounds of the 3-d render

        :params:
            pos_x (int): X-position of the camera
            pos_y (int): Y-position of the camera
            pos_z (int): Z-position of the camera
            azimuth (float): Azimuthal direction of the camera
                wrt a vertical axis reaching up from the given
                position
            elevation (float): Elevation angle of the camera
        """
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.pos_z = pos_z
        self.azimuth = azimuth
        self.elevation = elevation

    def render(self, world):
        """
        Render 3-D worldspace visible by camera

        :params:
            world (World): world object that defines
                the current game state.
        """
        pass

