import os
from typing import Dict, List, Tuple, Union

DIRECTORY: str = os.path.dirname(os.path.abspath(__file__))
WINDOW_SIZE: Tuple[int, int] = (1920, 1080)
CLOCK_UPDATE_SPEED: int = 100  # Update your time spent on the game (by milliseconds)

# -----------------------------------------------------------------------------------------------------------
# CORE.py
# "CORE_CONFIGURATION": Dictionary about specific notation in core.py
CORE_CONFIGURATION: Dict[str, Union[int, float]] = \
    {
        "Bomb Notation": -20,
        "Flag Notation": -1,
        "Question Notation": -5,
        "Bomb Coefficient": 0.125,
        "Bomb Power": 1,
        "Default Size": 15,
        "Maximum Stack": 24,
    }

# "MOUSE_MESSAGE": Used to emit a signal when clicking mouse
MOUSE_MESSAGE: Dict[Union[int, str], Union[int, str]] = \
    {
        "LeftMouse": "L",
        "RightMouse": "R",
    }


# -----------------------------------------------------------------------------------------------------------
# interface.py --> key = -1: Image Size
# CORE.py Association (Corresponding to y and x in order, no exception for everything)
# [1]: Number Image
def getBombNumberImageProperty(key: int) -> Union[Tuple[int, int], str]:
    # Function to get property of bomb images for display. With key = -1, its values were the image's size
    # With key != -1, while key represented the number of possible surrounding bombs, its values were directory
    if not isinstance(key, int) or key not in range(-1, 9):
        raise TypeError("Your key value is incompatible, try key = -1 or key between [0, 8]")

    return (65, 65) if key == -1 else DIRECTORY + "/resources/images/numbers/{}.png".format(key)


def getBombPositionForDisplay(y: int, x: int) -> Tuple[int, int]:
    # y first, x later (core match-up)
    BOMB_NUMBER_DISPLAY: Dict[str, Tuple[int, int]] = {"Initial": (0, 0), "Separation": (3, 3)}
    size: Tuple[int, int] = getBombNumberImageProperty(key=-1)
    return (BOMB_NUMBER_DISPLAY["Initial"][0] + y * size[0] + (y - 1) * BOMB_NUMBER_DISPLAY["Separation"][0],
            BOMB_NUMBER_DISPLAY["Initial"][1] + x * size[1] + (x - 1) * BOMB_NUMBER_DISPLAY["Separation"][1])


# [2]: Flag Image
def getFlagImage(key: Union[str, int]) -> Union[str, Tuple[int, int]]:
    # Opening Key: Initial and Defused
    if key in ["Initial", "Excited"]:
        return DIRECTORY + "/resources/images/flag/{} Flag.png".format(key)
    elif key == -1:
        return 65, 65
    raise ValueError("key ({}) is in-valid. Only accept key = [Initial, Excited, -1] only".format(key))


# [3]: Bomb Image
def getBombImage(key: Union[str, int]) -> Union[str, Tuple[int, int]]:
    # Opening Key: Initial and Defused
    if key in ["Initial", "Excited"]:
        return DIRECTORY + "/resources/images/bomb/{} Bomb.png".format(key)
    elif key == -1:
        return 65, 65
    raise ValueError("key ({}) is in-valid. Only accept key = [Initial, Excited, -1] only".format(key))


# [4]: Core Background
def getGameBackground(key: Union[str, int]) -> Union[str, Tuple[int, int]]:
    # TODO
    # Opening Key: Initial and Defused
    if key in ["Initial", "Excited"]:
        return DIRECTORY + "/resources/images/bomb/{} Bomb.png".format(key)
    elif key == -1:
        return 65, 65
    raise ValueError("key ({}) is in-valid. Only accept key = [Initial, Excited, -1] only".format(key))


# -----------------------------------------------------------------------------------------------------------
# Interface Association
# [1]: Opening Interface
def getOpenInterface(key: str, get_size: bool = False) -> Union[str, Tuple[int, int]]:
    main_directory: str = DIRECTORY + "/resources/images/opening/"
    request_key: List[str] = ["Background", "Opening", "Title", "Play"]
    if key in request_key:
        if get_size is False:
            return main_directory + "{}.png".format(key)

        idx: int = request_key.index(key)
        if idx in (0, 1):
            return WINDOW_SIZE
        # TODO
        elif idx == 2:
            return 0, 0
        elif idx == 3:
            return 0, 0
    raise ValueError("Invalid Key ({}). Only accept key = {} only".format(key, request_key))


# [2]: Ending Interface
def getEndInterface(key: str, get_size: bool = False) -> Union[str, Tuple[int, int]]:
    main_directory: str = DIRECTORY + "/resources/images/ending/"
    request_key: List[str] = ["Background", "Ending", "Win", "Lose", "Replay"]
    if key in request_key:
        if get_size is False:
            return main_directory + "{}.png".format(key)

        idx: int = request_key.index(key)
        if idx in (0, 1):
            return WINDOW_SIZE
        # TODO
        elif idx == (2, 3):
            return 0, 0
        elif idx == 4:
            return 0, 0
    raise ValueError("Invalid Key ({}). Only accept key = {} only".format(key, request_key))
