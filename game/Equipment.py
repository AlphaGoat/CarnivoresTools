"""
Class definitions for pieces of equipment
the hunter can carry

Author: Peter Thomas
Date: 26 June 2024
"""
from abc import ABC, abstractmethod
from physics.ballistics import Bullet


class Equipment(ABC):
    @abstractmethod
    def primary_action(self):
        pass

    @abstractmethod
    def secondary_action(self):
        pass


class Gun(Equipment):
    def __init__(self,
                 name: str,
                 ):

        # Flags for the gun
        raised = False

    def primary_action(self):
        if self.raised:
            return Bullet()
