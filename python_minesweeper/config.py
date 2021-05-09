import os

DIRECTORY = os.path.dirname(os.path.abspath(_file_))

number = {
    "1" : DIRECTORY + "/python_minesweeper/resources/images/one.png",
    "2" : DIRECTORY + "/python_minesweeper/resources/images/two.png",
    "3" : DIRECTORY + "/python_minesweeper/resources/images/three.png",
    "4" : DIRECTORY + "/python_minesweeper/resources/images/four.png",
    "5" : DIRECTORY + "/python_minesweeper/resources/images/five.png",
    "6" : DIRECTORY + "/python_minesweeper/resources/images/six.png",
    "7" : DIRECTORY + "/python_minesweeper/resources/images/seven.png",
    "8" : DIRECTORY + "/python_minesweeper/resources/images/eight.png",
    "size" : [65, 65],
}

element_address = {
    "clicked_bordered" : DIRECTORY + "/python_minesweeper/resources/images/clicked_bordered.png",
    "clicked_unbordered" : DIRECTORY + "/python_minesweeper/resources/images/clicked_unbordered.png",
    "background_bordered": DIRECTORY + "/python_minesweeper/resources/images/background_bordered.png",
    "background_unbordered" : DIRECTORY + "/python_minesweeper/resources/images/background_unbordered.png",
    "bomb_icon" : DIRECTORY + "/python_minesweeper/resources/images/bomb_icon.png",
    "bomb_explode" : DIRECTORY + "/python_minesweeper/resources/images/bomb_explode.png",
    "flag_black_background" : DIRECTORY + "/python_minesweeper/resources/images/flag_black_background.png",
    "flag_no_background" : DIRECTORY + "/python_minesweeper/resources/images/flag_no_background.png",
    "size" : [65, 65], 
}

mainscreen_image_address = {
    "translucent_overlay" : DIRECTORY + "/python_minesweeper/resources/images/translucent_overlay.png",
    "translucent" : DIRECTORY + "/python_minesweeper/resources/images/translucent.png",
    "welcome_screen_background" : DIRECTORY + "/python_minesweeper/resources/images/welcome_screen_background.png",
    "size" : [1920, 1080],
}

initial_position = {
    "mainscreen_image" : [0, 0],
    "tile" : [30, 30],
}

def getTilePos(i=0, j=0):
    return [30+68*i, 30+68*j]