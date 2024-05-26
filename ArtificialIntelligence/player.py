"""
Base class for Player character.

Author: Peter Thomas
Date: 19 May 2024
"""

class Player():
    HEIGHT = 5
    def __init__(self, 
                 init_pos_x: int,
                 init_pos_y: int,
                 init_pos_z: int):
        self.curr_pos_x = init_pos_x
        self.curr_pos_y = init_pos_y
        self.curr_pos_z = init_pos_z
