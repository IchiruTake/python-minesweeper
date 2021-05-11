import os
from typing import*

DIRECTORY = os.path.dirname(os.path.abspath(__file__))

number = {
    "1" : DIRECTORY + "/resources/images/one.png",
    "2" : DIRECTORY + "/resources/images/two.png",
    "3" : DIRECTORY + "/resources/images/three.png",
    "4" : DIRECTORY + "/resources/images/four.png",
    "5" : DIRECTORY + "/resources/images/five.png",
    "6" : DIRECTORY + "/resources/images/six.png",
    "7" : DIRECTORY + "/resources/images/seven.png",
    "8" : DIRECTORY + "/resources/images/eight.png",
    "size" : 65,
}

element_address = {
    "clicked_bordered" : DIRECTORY + "/resources/images/clicked_bordered.png",
    "clicked_unbordered" : DIRECTORY + "/resources/images/clicked_unbordered.png",
    "background_bordered": DIRECTORY + "/resources/images/background_bordered.png",
    "background_unbordered" : DIRECTORY + "/resources/images/background_unbordered.png",
    "bomb_icon" : DIRECTORY + "/resources/images/bomb_icon.png",
    "bomb_explode" : DIRECTORY + "/resources/images/bomb_explode.png",
    "flag_black_background" : DIRECTORY + "/resources/images/flag_black_background.png",
    "flag_no_background" : DIRECTORY + "/resources/images/flag_no_background.png",
    "size" : [65, 65], 
}

mainscreen_image_address = {
    "translucent_overlay" : DIRECTORY + "/resources/images/translucent_overlay.png",
    "translucent" : DIRECTORY + "/resources/images/translucent.png",
    "welcome_screen_background" : DIRECTORY + "/resources/images/welcome_screen_background.png",
    "game_name" : DIRECTORY + "/resources/images/game_name.png",
    "size" : [1920, 1080],
}

initial_position = {
    "mainscreen_image" : [0, 0],
    "tile" : [30, 30],
}

def getTileSize(number_of_tile) -> int:
    return int(((1080 - 60) / number_of_tile) - 3)

def getTilePos(i=0, j=0, tile_size = 65) -> int:
    return [30+tile_size*i+i*3, 30+tile_size*j+j*3]