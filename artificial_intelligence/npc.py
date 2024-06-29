"""
Base class for huntable NPC in Carnivores

Author: Peter Thomas
Date: 19 May 2024
"""
from statemachine import StateMachine, State


class HuntableNPC(StateMachine):
    restingState = State("resting") # Resting
    fleeingState = State("fleeing") # Fleeing from player character
    idleState = State("idle") # Idle


class HerbivorousNPC(HuntableNPC):
    grazingState = State("grazing") # Grazing on grass
    fleeingCarnivore = State("fleeing_carnivore") # Fleeing from Carnivore NPC


class CarnivorousNPC(HuntableNPC):
    huntingState = State("hunting") # Hunting another NPC dinosaur
    stalkingState = State("stalking") # Stalking player character
    attackingState = State("attacking") # Attacking player character
