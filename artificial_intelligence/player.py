"""
Base class for Player character.

Author: Peter Thomas
Date: 19 May 2024
"""

class Player():
    HEIGHT = 5
    SPEED = 5
    def __init__(self, 
                 init_pos_x: int,
                 init_pos_y: int,
                 init_pos_z: int,
                 inventory: Inventory):

        self.curr_pos_x = init_pos_x
        self.curr_pos_y = init_pos_y
        self.curr_pos_z = init_pos_z

        # initialize player with level elevation
        # and azimuth
        self.elevation = 0.0
        self.azimuth = 0.0

        self.inventory = inventory

    def move_right(self):
        self.curr_pos_x += self.SPEED

    def move_left(self):
        self.curr_pos_x -= self.SPEED

    def move_up(self):
        self.curr_pos_y += self.SPEED

    def move_down(self):
        self.curr_pos_x += self.SPEED

    def primary_action(self):
        # Check what piece of equipment the hunter
        # has out and use its primary action
        if self.inventory.active_equipment is not None:
            self.inventory.active_equipment.primary_action()

    def secondary_action(self):
        # Check what piece of equipment the hunter
        # has out and use its secondary action
        if self.inventory.active_equipment is not None:
            self.inventory.active_equipment.secondary_action()


class Inventory():
    def __init__(self, items):
        self.items = items
        self.active_equipment = None

    def make_active(self, idx: int):
        # Make a piece of equipment in the 
        # inventory "active"
        self.active_equipment = self.items[idx]
