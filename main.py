"""
Main game loop

Author: Peter Thomas
Date: 19 May 2024
"""
import os
import pygame
import struct
import moderngl
import random
from statemachine import StateMachine, State
from GraphicsEngine import Map
from artificial_intelligence import Player
from utils import RSCReader, MAPReader


def main(args):

    # Start game by initializing state machine to 
    # handle menus
    menus = Menus()
    main_menu = MainMenu()

    # Initialize pygame and set up the drawing window
    pygame.init()
    screen = pygame.display.set_mode([800, 600])

    # Run cursory game loop to handle user interactions
    # in the menus
    run_loop = True
    while run_loop:

        # Keep track of current game state
        if menus.current_state == "main":
            pass


    # Read in .rsc and .map file 
    with MAPReader(args.map_file_path) as map_reader:
        map_contents = map_reader.MAP

    with RSCReader(args.rsc_file_path) as rsc_reader:
        pass

    # Initialize "Map" object
    game_map = Map()

    # Initialize player character at a random
    # position
    # NOTE: Z-height is fixed because of texture
    #   placement, so that can't be randomized
    pos_x = random.randint(0, game_map.map_size)
    pos_y = random.randint(0, game_map.map_size)
    pos_z = game_map.elevation[pos_x, pos_y]

    player = Player(pos_x,
                    pos_y,
                    pos_z)

    # Run the game loop
    run_game_loop = True
    while run_game_loop:

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move_left()
        if keys[pygame.K_RIGHT]:
            player.move_right()
        if keys[pygame.K_UP]:
            player.move_up()
        if keys[pygame.K_DOWN]:
            player.move_down()

        # Switch out item in the player's hand
        if keys[pygame.K_0]:
            player.inventory.make_active(0)
        if keys[pygame.K_1]:
            player.inventory.make_active(1)
        if keys[pygame.K_2]:
            player.inventory.make_active(2)
        if keys[pygame.K_3]:
            player.inventory.make_active(3)
        if keys[pygame.K_4]:
            player.inventory.make_active(4)
        if keys[pygame.K_5]:
            player.inventory.make_active(5)
        if keys[pygame.K_6]:
            player.inventory.make_active(6)
        if keys[pygame.K_7]:
            player.inventory.make_active(7)
        if keys[pygame.K_8]:
            player.inventory.make_active(8)
        if keys[pygame.K_9]:
            player.inventory.make_active(9)

        if pygame.mouse.get_pressed()[0]:
            player.primary_action()
        if pygame.mouse.get_pressed()[1]:
            player.secondary_action()

        # see if the QUIT signal has been sent
        for event in pygame.events.get():
            if event.type == pygame.QUIT:
                run_game_loop = False

        
