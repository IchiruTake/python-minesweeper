from typing import Tuple, List, Union, Optional
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from config import CORE_CONFIGURATION as CONFIG, getBombNumberImage, getFlagImage, getBombImage, getQuestionImage, \
    BOMB_NUMBER_DISPLAY as number_displayer
from logging import warning


class Number_CoreUI(QLabel):

    __slots__ = ("y", "x", "_value", "_interfaceStatus", "_isMine", "_imageSize", "_imageInterface",
                 "_bombInterface", "_flagInterface", "_questionInterface")

    updatingSignalSender = pyqtSignal(int, int, str)

    # The node for displaying function only
    # _imageInterface[0]: Starting Block when Playing, _imageInterface[1]: Value Block when Opened,
    # _bombInterface[0]: Bomb Node for Displaying, _bombInterface[1]: Bomb Exploded when Clicked,
    # _flagInterface[0]: Flag Node when Assigning, _flagInterface[1]: Flag Node if Defused,

    def __init__(self, y: int, x: int, value: int, imageScalingSize: Union[float, int] = 1, *args, **kwargs):
        # [0]: Hyper-parameter Verification
        if True:
            if not isinstance(y, int):
                raise ValueError("The position of y-axis must be integer")
            if y < 0:
                raise ValueError("The position of y-axis must be non-negative")

            if not isinstance(x, int):
                raise ValueError("The position of x-axis must be integer")
            if x < 0:
                raise ValueError("The position of x-axis must be non-negative")

            if not isinstance(value, int):
                raise ValueError("The position of value must be integer")

            pass

        # [1]: Attribute Match-up
        super(Number_CoreUI, self).__init__(*args, **kwargs)

        self.y: int = y
        self.x: int = x
        self._value: int = value
        self._interfaceStatus: int = 0
        self._isMine: bool = True if CONFIG["Bomb Notation"] == self._value else False
        self._scalingSize: Union[float, int] = imageScalingSize

        # [2]: Attribute Creation (by Image)
        # _imageSize: The size of nodes in UI, _imageInterface: The image path of 'number' block,
        # _bombInterface: The image path of 'bomb' block, _flagInterface: The image path of 'flag' block
        # _questionInterface: The image path of 'question' block
        self._imageSize: List[int] = list(getBombNumberImage(key=-1))
        self._imageInterface: Tuple[str, str] = (getBombNumberImage(key=0), getBombNumberImage(key=self._value))
        self._bombInterface: Tuple[str, str] = (getBombImage(key="Initial"), getBombImage(key="Excited"))
        self._flagInterface: Tuple[str, str] = (getFlagImage(key="Initial"), getFlagImage(key="Excited"))
        self._questionInterface: str = getQuestionImage(get_size=False)

        # [3]: Building Function when instantiated
        self._build()

    # ----------------------------------------------------------------------------------------------------------
    # [0]: Building Function
    def _initializeImage(self) -> None:
        self.setPixmap(a0=QPixmap(self._imageInterface[0]))
        self._resetImageSize()

    def _resetImageSize(self) -> None:
        pos: List[int] = \
            [number_displayer["Initial"][0] + int(self.y * self._scalingSize * self._imageSize[0]),
             number_displayer["Initial"][1] + int(self.x * self._scalingSize * self._imageSize[1])]
        size = int(self._imageSize[1] * self._scalingSize)
        if self.y != 0:
            pos[0] += number_displayer["Separation"][1]
        if self.x != 0:
            pos[1] += number_displayer["Separation"][0]
        self.setGeometry(pos[1], pos[0], size, size)

    def _build(self):
        self.ensurePolished()
        self.setVisible(True)
        self.setMouseTracking(True)
        self.setUpdatesEnabled(True)
        self.setEnabled(True)
        self.setScaledContents(True)

        self._initializeImage()

        self.update()
        self.show()

    def updateStatus(self, interfaceStatus: int):
        if interfaceStatus in (0, -1, CONFIG["Flag Notation"], CONFIG["Question Notation"]):
            self._interfaceStatus = interfaceStatus
        else:
            print("No update has been applied")

    def updateImage(self) -> None:
        # TODO
        if self._interfaceStatus == 1:
            self.setPixmap(a0=QPixmap(self._imageInterface[1]))
        else:
            if self._interfaceStatus == 0:
                self.setVisible(False)
            elif self._interfaceStatus == CONFIG["Flag Notation"]:
                self.setPixmap(a0=QPixmap(self._flagInterface[0]))
            elif self._interfaceStatus == CONFIG["Question Notation"]:
                self.setPixmap(a0=QPixmap(self._questionInterface[0]))

        self._resetImageSize()
        self.update()
        self.show()

    def reveal(self) -> bool:
        # TODO
        reveal_status: bool = False
        if self._interfaceStatus != CONFIG["Question Notation"]:
            if self._isMine is False:
                if self._value in range(1, 9):
                    self.setPixmap(a0=QPixmap(self._imageInterface[1]))
                else:
                    self.setPixmap(a0=QPixmap(self._bombInterface[0]))
            else:
                if self._value == 1:
                    self.setPixmap(a0=QPixmap(self._bombInterface[1]))
                elif self._interfaceStatus == CONFIG["Flag Notation"]:
                    self.setPixmap(a0=QPixmap(self._flagInterface[1]))
            reveal_status = True

            self._resetImageSize()
            self.update()
            self.show()

        return reveal_status

    def reset(self) -> None:
        self.y = -1
        self.x = -1
        self._value = 0
        self._interfaceStatus = 0
        self._isMine = False

    # ----------------------------------------------------------------------------------------------------------
    # [1]: Interface Function
    def mouseReleaseEvent(self, e: QMouseEvent):
        msg = {Qt.LeftButton: "LeftMouse", Qt.RightButton: "RightMouse"}
        self.updatingSignalSender.emit(self.y, self.x, msg[e.button()])

    # ----------------------------------------------------------------------------------------------------------
    # [x]: Getter Function
    def getPosition(self) -> Tuple[int, int]:
        return self.y, self.x

    def getValue(self) -> int:
        return self._value

    def getIsMine(self) -> bool:
        return self._isMine
