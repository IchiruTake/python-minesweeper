import os
from typing import*

DIRECTORY = os.path.dirname(os.path.abspath(__file__))

NOTATION: Dict[str, Union[int, float]] = \
    {
        "Bomb Notation": -20,
        "Flag Notation": 50,
        "Bomb Coefficient": 1,
        "Bomb Ratio": 1/2,
    }

#NUMBER: key is the number of bombs of surrounding tile
NUMBER: Dict[Union[str, int], Union[Tuple[int, int], str, int]] = \
    {
        1: DIRECTORY + "/resources/images/one.png", #1 bomb surrounding
        2: DIRECTORY + "/resources/images/two.png", #2 bombs surrounding
        3: DIRECTORY + "/resources/images/three.png", #3 bombs surrounding
        4: DIRECTORY + "/resources/images/four.png", #4 bombs surrounding
        5: DIRECTORY + "/resources/images/five.png", #5 bombs surrounding
        6: DIRECTORY + "/resources/images/six.png", #6 bombs surrounding
        7: DIRECTORY + "/resources/images/seven.png", #7 bombs surrounding
        8: DIRECTORY + "/resources/images/eight.png", #8 bombs surrounding
        "size": (65, 65), #size of bomb number's image
    }

#ELEMENT_ADDRESS: key is element shown when you interact with game
ELEMENT_ADDRESS = \
    {
        "clicked_bordered": DIRECTORY + "/resources/images/clicked_bordered.png", #this is shown when you click on the tile. Image with no white border on edge (dark gray)
        "clicked_unbordered": DIRECTORY + "/resources/images/clicked_unbordered.png", #this is shown when you click on the tile. Image with white border on edge (dark gray)
        "background_bordered": DIRECTORY + "/resources/images/background_bordered.png", #tile background when unclicked (gray)
        "background_unbordered": DIRECTORY + "/resources/images/background_unbordered.png", #tile background when unclicked, (gray with white border)
        "bomb_icon": DIRECTORY + "/resources/images/bomb_icon.png", #a bomb image
        "bomb_explode": DIRECTORY + "/resources/images/bomb_explode.png", #an image of explosion, shown when player missclick on a bomb tile
        "flag_black_background": DIRECTORY + "/resources/images/flag_black_background.png", #flag image, shown when user right click to set the flag on a tile, not preferred to use
        "flag_no_background": DIRECTORY + "/resources/images/flag_no_background.png", #flag image with preferred transparent background, preferred to use
        "size": (65, 65), #size of image
    }

#MAINSCREEN_IMAGE_ADDRESS: any fullscreen element or elements shown on main screen
MAINSCREEN_IMAGE_ADDRESS = {
    "translucent_overlay": DIRECTORY + "/resources/images/translucent_overlay.png", #a blurred overlay, shown when player clicks start game, use at result screen
    "translucent": DIRECTORY + "/resources/images/translucent.png", #different colored overlay with glass effect, preferred & use this
    "welcome_screen_background": DIRECTORY + "/resources/images/welcome_screen_background.png", #shown firstly when you start the game
    "game_name": DIRECTORY + "/resources/images/game_name.png", #game title, image with "Minesweeper" red text
    "size": (1920, 1080), #general size~window size??
}

INITIAL_POSITION = {
    "mainscreen_image" : [0, 0],
    "tile" : [30, 30],
}

def getTileSize(number_of_tile) -> int: #calculate tile size base on screen size and number of tile per column
    return int((1080 - 60) / number_of_tile) - 3

def getTilePos(i=0, j=0, tile_size=65) -> int: #calculate tile position
    return [30 + tile_size * i + i * 3, 30 + tile_size * j + j * 3]

def getXYfromIndex(index, tile_size, number_of_tile) -> int:  # suy ra index từ tọa độ X và Y của tile
    x, y = 30 + int(index % number_of_tile) * tile_size + int(index % number_of_tile) * 3, 30 + tile_size * int(
        index / number_of_tile) + int(index / number_of_tile) * 3
    return x, y
