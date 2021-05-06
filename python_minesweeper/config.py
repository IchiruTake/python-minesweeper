number = {
    "one" : "/resources/images/one.png",
    "two" : "/resources/images/two.png",
    "three" : "/resources/images/three.png",
    "four" : "/resources/images/four.png",
    "five" : "/resources/images/five.png",
    "six" : "/resources/images/six.png",
    "seven" : "/resources/images/seven.png",
    "eight" : "/resources/images/eight.png",
    "size" : [65, 65],
}

element_address = {
    "clicked_unbordered" : "/resources/images/clicked_unbordered.png",
    "background_unbordered" : "/resources/images/background_unbordered.png",
    "bomb_icon" : "/resources/images/bomb_icon.png",
    "bomb_explode" : "/resources/images/bomb_explode.png",
    "flag_no_background" : "/resources/images/flag_no_background.png",
    "size" : [65, 65], 
}

mainscreen_image_address = {
    "translucent_overlay" : "/resources/images/translucent_overlay.png",
    "translucent" : "/resources/images/translucent.png",
    "welcome_screen_background" : "/resources/images/welcome_screen_background.png",
    "size" : [1920, 1080],
}

initial_position = {
    "mainscreen_image" : [0, 0],
    "tile" : [30, 30],
}

def getTilePos(i=0, j=0):
    return [30+68*i, 30+68*j]