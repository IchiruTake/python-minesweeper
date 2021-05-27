import os
from typing import Dict, List, Tuple, Union, Optional

DIRECTORY: str = os.path.dirname(os.path.abspath(__file__))
WINDOW_SIZE: Tuple[int, int] = (1920, 1080)


# -----------------------------------------------------------------------------------------------------------
# interface.py --> key = -1: Image Size
# CORE.py Association (Corresponding to y and x in order, no exception for everything)
# [1]: Number Image
def getBombNumberImage(key: Optional[Union[str, int]]) -> Union[Tuple[int, int], str]:
    # Function to get property of bomb images for display.
    # If key = None: originated nodes, If key = -1, return its size, else, return its associated images
    if key is None or key in ["NULL"]:
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
    print("key ({}) is in-valid. Only accept key = [Initial, Excited, -1] only".format(key))
    raise ValueError("key ({}) is in-valid. Only accept key = [Initial, Excited, -1] only".format(key))


# [4]: Question Mark
def getQuestionImage(get_size: bool = False) -> Union[str, Tuple[int, int]]:
    return (65, 65) if get_size is True else DIRECTORY + "/resources/images/question/Question.png"


# [5]: Gaming Background
def getGamingBackground(get_size: bool = False) -> Union[str, Tuple[int, int]]:
    return WINDOW_SIZE if get_size is True else DIRECTORY + "/resources/images/background/Background.png"


# [6]: Get Timer Button
def getTimerImage(get_size: bool = False) -> Union[str, Tuple[int, int]]:
    return (65, 65) if get_size is True else DIRECTORY + "/resources/images/timer/Timer.png"


# [7]: Get Extra Button
def getExtraButton(key: Union[str, int]) -> Union[str, Tuple[int, int]]:
    if key == -1:
        return 267, 138

    request_key: List[str] = ["Undo", "Undo-hover", "Submit", "Submit-hover", "Redo", "Redo-hover"]
    if key in request_key:
        return DIRECTORY + "/resources/images/extra/{}.png".format(key)

    print("Invalid Key ({}). Only accept key = {} only".format(key, request_key))
    raise ValueError("Invalid Key ({}). Only accept key = {} only".format(key, request_key))


# -----------------------------------------------------------------------------------------------------------
# Interface Association
# [1]: Opening Interface
def getOpenInterface(key: str, get_size: bool = False) -> Union[str, Tuple[int, int]]:
    request_key: List[str] = ["Background", "Opening", "Title", "Play", "Play-hover"]
    try:
        idx: int = request_key.index(key)
        if get_size is False:
            return DIRECTORY + "/resources/images/opening/{}.png".format(key)

        if idx in (0, 1):
            return WINDOW_SIZE
        elif idx == 2:
            return 714, 130
        elif idx in (3, 4):
            return 267, 138
        print("Invalid Key ({}). Only accept key = {} only".format(key, request_key))
    except (ValueError, IndexError):
        pass
    raise ValueError("Invalid Key ({}). Only accept key = {} only".format(key, request_key))


# [2]: Ending Interface
def getEndInterface(key: str, get_size: bool = False) -> Union[str, Tuple[int, int]]:
    request_key: List[str] = ["Background", "Ending", "Win", "Lose", "Replay", "Replay-hover"]
    try:
        idx: int = request_key.index(key)
        if get_size is False:
            return DIRECTORY + "/resources/images/ending/{}.png".format(key)

        if idx in (0, 1):
            return WINDOW_SIZE
        elif idx in (2, 3):
            return 918, 373
        elif idx in (4, 5):
            return 267, 138
        print("Invalid Key ({}). Only accept key = {} only".format(key, request_key))
    except (ValueError, IndexError):
        pass

    raise ValueError("Invalid Key ({}). Only accept key = {} only".format(key, request_key))


# [3]: Dialog Interface
def getDialogBackground(get_size: bool = False) -> Union[str, Tuple[int, int]]:
    main_directory: str = DIRECTORY + "/resources/images/dialog/"
    return (1080, 1080) if get_size is True else main_directory + "Dialog.png"


def getIcon(get_size: bool = False) -> Union[str, Tuple[int, int]]:
    return (48, 48) if get_size is True else DIRECTORY + "/resources/images/icon/Icon.ico"


# -----------------------------------------------------------------------------------------------------------
# [3]: Supplementary
def getRelativePath(path: str) -> str:
    if isinstance(path, str):
        return path.replace(DIRECTORY, "")
    print("Invalid Path ({})".format(path))
    raise ValueError("Invalid Path ({})".format(path))


DIALOG_SIZE: Tuple[int, int] = (300, 300)
CLOCK_UPDATE_SPEED: int = 100  # Update your time spent on the game (by milliseconds)
UPDATING_TIMING: int = 1000
VIEWING_TIME_FOR_TRANSFER: int = 2500
NODES_SIZE: Tuple[int, int] = getBombNumberImage(key=-1)
TABLE_VIEW: Tuple[int, int] = (500, 400)
TABLE_MAX_DISPLAY: int = 20
BOARD_LENGTH: int = 45

BOMB_NUMBER_DISPLAY: Dict[str, List[int]] = \
    {
        "Initial": [3 + BOARD_LENGTH, 3],
        "Separation": [int(NODES_SIZE[0] // 4), int(NODES_SIZE[1] // 4)]
    }

# "MOUSE_MESSAGE": Used to emit a signal when clicking mouse
MOUSE_MESSAGE: Dict[Union[int, str], Union[int, str]] = \
    {
        "LeftMouse": "L",
        "RightMouse": "R",
    }
# -----------------------------------------------------------------------------------------------------------
# CORE.py
# "CORE_CONFIGURATION": Dictionary about specific notation in core.py
CORE_CONFIGURATION: Dict[str, Union[int, float]] = \
    {
        "Bomb Notation": -20,
        "Flag Notation": -1,
        "Question Notation": -5,
        "Default Size": 15,
        "Maximum Stack": 48,
        "Clean Time": 6,
    }

__EASY: Tuple[float, float] = (0.125, 1.75)
__MEDIUM: Tuple[float, float] = (0.15, 1.8)
__HARD: Tuple[float, float] = (0.2, 1.8)
__EXTREME: Tuple[float, float] = (0.25, 1.875)

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
    print("key ({}) is in-valid. Only accept key = {} only".format(key, list(DIFFICULTY.keys())))
    raise ValueError("key ({}) is in-valid. Only accept key = {} only".format(key, list(DIFFICULTY.keys())))


# [4]: Extra Function
def estimateBombLevel() -> None:
    game_play: Dict[str, int] = {"Tiny": 8, "Small": 16, "Small-Med": 25,
                                 "Medium": 40, "Large": 75, "Extreme": 99}
    for game_key, game_value in game_play.items():
        for difficulty_key, difficulty_value in DIFFICULTY.items():
            bomb: int = int(difficulty_value[0] * game_value ** difficulty_value[1])
            nodes: int = game_value * game_value
            print("(Size: {} --- Difficulty: {}) --> Bomb Number(s): {} / {} (Ratio: {} % - Overwhelming: {})"
                  .format(game_key, difficulty_key, bomb, nodes, round(bomb / nodes * 100, 2), 9 * bomb >= nodes))
        print()
    return None
