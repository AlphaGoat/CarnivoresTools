"""
Implement menu logic here, por favor. Gracias

Author: Peter Thomas
Date: 29 June 2024
"""
import os
import pygame
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from statemachine import StateMachine, State

from utils.images import load_tga


class Menus(StateMachine):
    # Define states, each corresponding to a 
    # separate menu
    introState = State("intro", initial=True)
    mainState = State("main")
    creditsState = State("credits")
    loadingState = State("loading")
    optionsState = State("options")
    trophyState = State("trophy")
    huntState = State("hunt")
    launchState = State("launch")
    quitState = State("quit")
    statisticsState = State("statistics")

    # Define transitions between states
    introToMain = introState.to(mainState)

    mainToCredits = mainState.to(creditsState)
    mainToOptions = mainState.to(optionsState)
    mainToTrophy = mainState.to(trophyState)
    mainToStatistics = mainState.to(statisticsState)
    mainToHunt = mainState.to(huntState)
    mainToQuit = mainState.to(quitState)

    huntToLoad = huntState.to(loadingState)
    huntToMain = huntState.to(mainState)

    creditsToMain = creditsState.to(mainState)

    optionsToMain = optionsState.to(mainState)

    statisticsToMain = statisticsState.to(mainState)

    
def load_menu_graphic(
    menu: StateMachine, 
    menu_graphics_path: str="./HUNTDAT/MENU",
):
    """
    Load in game menus
    """
    if menu.current_state.identifier == "intro":
        menu_graphic = load_tga(os.path.join(menu_graphics_path, "MENUD.TGA"))
    elif menu.current_state.identifier == "main":
        menu_graphic = load_tga(os.path.join(menu_graphics_path, "MENUM.TGA"))
    elif menu.current_state.identifier == "credits":
        menu_graphic = load_tga(os.path.join(menu_graphics_path, "CREDITS.TGA"))
    elif menu.current_state.identifier == "options":
        menu_graphic = load_tga(os.path.join(menu_graphics_path, "OPT_OFF.TGA"))
    elif menu.current_state.identifier == "trophy":
        # NOTE: implement this
        raise NotImplementedError("Haven't implemented trophy room yet!")
    elif menu.current_state.identifier == "statistics":
        menu_graphic = load_tga(os.path.join(menu_graphics_path, "MENUS.TGA"))
    elif menu.current_state.identifier == "quit":
        menu_graphic = load_tga(os.path.join(menu_graphics_path, "MENUQ_ON.TGA"))
    elif menu.current_state.identifier == "hunt":
        menu_graphic = load_tga(os.path.join(menu_graphics_path, "MENU2.TGA"))
    else:
        raise RuntimeError(f"Menu state {menu.current_state.identifier} not recognized.")
    return menu_graphic


class MainMenu():
    def __init__(self, game_state: StateMachine):
        self.game_state = game_state

        # Define 'Polygon' objects for all of the
        # buttons in the main menu (because I don't
        # have time to write my own function to 
        # eval if a mouse click fell within the pixel
        # box encompassed by a button)
        self.hunt_box = Polygon([(21, 220), (21, 280), (305, 280), (305, 220)])
        self.options_box = Polygon([(21, 283), (21, 343), (305, 343), (305, 283)])
        self.trophy_box = Polygon([(21, 357), (21, 417), (305, 417), (305, 357)])
        self.credits_box = Polygon([(21, 426), (21, 486), (305, 486), (305, 426)])
        self.quit_box = Polygon([(21, 494), (21, 554), (305, 554), (305, 494)])

    def __call__(self):
        run_loop = False
        while run_loop:
            events = pygame.events.get()
            for event in events:
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    self.evaluate_mouse_click(pos)

    def evaluate_mouse_click(self, position):
        if self.hunt_box.contains(position):
            self.game_state.send("mainToHunt")
        elif self.options_box.contains(position):
            self.game_state.send("mainToOptions")
        elif self.trophy_box.contains(position):
            self.game_state.send("mainToTrophy")
        elif self.credits_box.contains(position):
            self.game_state.send("mainToCredits")
        elif self.quit_box.contains(position):
            self.game_state.send("mainToQuit")
