import os
from typing import Dict, List, Tuple, Union, Optional

DIRECTORY: str = os.path.dirname(os.path.abspath(__file__))
WINDOW_SIZE: Tuple[int, int] = (1920, 1080)
DIALOG_SIZE: Tuple[int, int] = (300, 250)
CLOCK_UPDATE_SPEED: int = 100  # Update your time spent on the game (by milliseconds)

# -----------------------------------------------------------------------------------------------------------
# CORE.py
# "CORE_CONFIGURATION": Dictionary about specific notation in core.py
CORE_CONFIGURATION: Dict[str, Union[int, float]] = \
    {
        "Bomb Notation": -20,
        "Flag Notation": -1,
        "Question Notation": -5,
        "Default Size": 15,
        "Maximum Stack": 24,
    }

__EASY: Tuple[float, float] = (0.125, 1.75)
__MEDIUM: Tuple[float, float] = (0.15, 1.8)
__HARD: Tuple[float, float] = (0.2, 1.8)
__EXTREME: Tuple[float, float] = (0.225, 1.875)

DIFFICULTY: Dict[str, Tuple] = \
    {
        "Easy": __EASY,
        "Medium": __MEDIUM,
        "Hard": __HARD,
        "Extreme": __EXTREME,
    }


def difficulty_validation(key: str) -> Tuple[int, int]:
    if key in DIFFICULTY.keys():
        return DIFFICULTY[key]
    raise ValueError("key ({}) is in-valid. Only accept key = {} only".format(key, list(DIFFICULTY.keys())))


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
BOMB_NUMBER_DISPLAY: Dict[str, Tuple[int, int]] = \
    {
        "Initial": (0, 0),
        "Separation": (3, 3)
    }


def getBombNumberImage(key: Optional[int]) -> Union[Tuple[int, int], str]:
    # Function to get property of bomb images for display.
    # If key = None: originated nodes, If key = -1, return its size, else, return its associated images
    if key is None:
        return DIRECTORY + "/resources/images/numbers/{}.png".format(key)

    if not isinstance(key, int) or key not in range(-1, 9):
        raise TypeError("Your key value is incompatible, try key = -1 or key between [0, 8]")

    return (65, 65) if key == -1 else DIRECTORY + "/resources/images/numbers/{}.png".format(key)


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


# [4]: Question Mark
def getQuestionImage(get_size: bool = False) -> Union[str, Tuple[int, int]]:
    return (65, 65) if get_size is True else "/resources/images/question/Question.png"


# [5]: Gaming Background
def getGamingBackground(get_size: bool = False) -> Union[str, Tuple[int, int]]:
    return WINDOW_SIZE if get_size is True else "/resources/images/background/Background.png"


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
    request_key: Tuple[str, str, str, str, str] = ("Background", "Ending", "Win", "Lose", "Replay")
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


# -----------------------------------------------------------------------------------------------------------
# [3]: Supplementary
def getUndoRedoImage(key: str, get_size: bool = False) -> Union[str, Tuple[int, int]]:
    main_directory: str = DIRECTORY + "/resources/images/undo_redo/"
    request_key: Tuple[str, str] = ("Undo", "Redo")
    if key in request_key:
        return main_directory + "{}.png".format(key) if get_size is False else (267, 138)

    raise ValueError("Invalid Key ({}). Only accept key = {} only".format(key, request_key))


# -----------------------------------------------------------------------------------------------------------
# [4]: Extra Function
def estimateBombLevel():
    game_play: Dict[str, int] = {"Tiny": 8, "Small": 16, "Small-Med": 25,
                                 "Medium": 40, "Large": 75, "Extreme": 99}
    for game_key, game_value in game_play.items():
        for difficulty_key, difficulty_value in DIFFICULTY.items():
            bomb: int = int(difficulty_value[0] * game_value ** difficulty_value[1])
            nodes: int = game_value * game_value
            print("(Size: {} --- Difficulty: {}) --> Bomb Number(s): {} / {} (Ratio: {} % - Overwhelming: {})"
                  .format(game_key, difficulty_key, bomb, nodes, round(bomb / nodes * 100, 2), 9 * bomb >= nodes))
        print()


def getRelativePath(path: str) -> str:
    if isinstance(path, str):
        return path.replace(DIRECTORY, "")
    raise ValueError("Invalid Path ({})".format(path))
