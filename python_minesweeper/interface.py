import numpy as np
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time
import config
from typing import Tuple, List, Union, Optional
from core import minesweeper
from component_interface import InterfaceNode, GamingMode


class GameWindow(QMainWindow):
    # https://zetcode.com/gui/pyqt5/eventssignals/
    gamingSignal = pyqtSignal(str)
    dialogSignal = pyqtSignal()

    def __init__(self, *args, **kwargs):
        # [1]: Initialize Window
        super(GameWindow, self).__init__(*args, **kwargs)
        self.setGeometry(0, 0, *config.WINDOW_SIZE)
        self.setWindowTitle("Minesweeper")

        # [2]: Setup Core & Associated Attribute
        # [2.1]: Setup Core
        self._playingMatrixSize: Optional[Tuple[int, int]] = None
        self._playingDifficulty: Optional[str] = None
        self._playerName: Optional[str] = None
        self.__gameCore: Optional[minesweeper] = None

        # [2.2]: Setup Associated Attribute
        self._gameSetting: bool = False
        self._gameSettingTiming: float = config.UPDATING_TIMING * 1

        self._updatingTimingClock1: float = config.UPDATING_TIMING
        self._updatingTimerClock1: QTimer = QTimer(self)
        self._updatingTimerClock1.timeout.connect(self._updateSettingClock1)
        self._updatingTimerClock1.start(config.CLOCK_UPDATE_SPEED)

        self._playingDate: Optional[float] = None
        self._playingTime: Optional[float] = None
        self._startingTime: Optional[float] = None

        # ----------------------------------------------------------------------------------------------------------
        # [3.1]: Opening Interface
        self.welcome_background: Optional[QLabel] = QLabel(self)
        self.welcome_title: Optional[QLabel] = QLabel(self)
        self.welcome_playButton: Optional[QPushButton] = QPushButton(self)

        # [3.2]: Ending Interface

        # [4]: Playing Ground
        self.interface_matrix: Optional[List[List[Union[InterfaceNode, int]]]] = None

        # [5]: Running Function
        self._setup()
        self.welcome()

    # ----------------------------------------------------------------------------------------------------------
    # [1]: Setup Function
    def _setup(self):
        # [1]: Initialize Window
        if True:
            self.setEnabled(True)
            self.setMouseTracking(True)
            self.setUpdatesEnabled(True)
            self.setVisible(True)
            self.setFocus()

        # [2.1]: Opening Interface
        if True:
            self.welcome_background.setEnabled(True)
            self.welcome_background.setMouseTracking(True)
            self.welcome_background.setUpdatesEnabled(True)
            self.welcome_background.setVisible(True)
            self.welcome_background.setScaledContents(True)
            self.welcome_background.setFocus()

            self.welcome_title.setEnabled(True)
            self.welcome_title.setMouseTracking(True)
            self.welcome_title.setUpdatesEnabled(True)
            self.welcome_title.setVisible(True)
            self.welcome_title.setScaledContents(True)
            self.welcome_title.setFocus()

            self.welcome_playButton.setEnabled(True)
            self.welcome_playButton.setMouseTracking(True)
            self.welcome_playButton.setUpdatesEnabled(True)
            self.welcome_playButton.setVisible(True)
            self.welcome_playButton.setFocus()
            self.welcome_playButton.setStyleSheet("border-style: outset; background: transparent")

        # [2.2]: Ending Interface

        # [3]: Playing Ground

    # ----------------------------------------------------------------------------------------------------------
    # [2]: Interface Function
    def _assignGame(self, width: int, height: int, difficulty: str, name: str):
        from time import sleep
        # This is the function called (slots) of the input dialog that would raise when click on play button
        self.setMatrixSize(width=width, height=height)
        self.setDifficultyLevel(difficulty=difficulty)
        self.setPlayerName(name=name)

        self.activateGameSetting()

    def _makeDialog(self):
        dialog: GamingMode = GamingMode(self._playingMatrixSize, self._playingDifficulty, self._playerName, self)
        dialog.currentSignal.connect(self._assignGame)
        self.dialogSignal.connect(dialog.close)
        dialog.show()

    def welcome(self):
        # [1]: Make background and associated title
        self.welcome_background.lower()
        self.welcome_background.setPixmap(QPixmap(config.getOpenInterface(key="Opening")))
        self.welcome_background.setGeometry(0, 0, *config.getOpenInterface(key="Opening", get_size=True))

        self.welcome_title.raise_()
        self.welcome_title.setPixmap(QPixmap(config.getOpenInterface(key="Title")))
        self.welcome_title.setGeometry(1100, 100, *config.getOpenInterface(key="Title", get_size=True))

        # [2]: Making self.welcome_playButton
        self.welcome_playButton.raise_()
        self.welcome_playButton.setIcon(QIcon(config.getOpenInterface(key="Play")))
        self.welcome_playButton.setIconSize(QSize(*config.getOpenInterface(key="Play", get_size=True)))
        self.welcome_playButton.setGeometry(1300, 700, *config.getOpenInterface(key="Play", get_size=True))
        self.welcome_playButton.clicked.connect(self._makeDialog)

    # ----------------------------------------------------------------------------------------------------------
    # [3]: Timing Function
    def _resetTimerClock1(self):
        self._updatingTimingClock1 = config.UPDATING_TIMING

    def _updateSettingClock1(self):
        self._updatingTimingClock1 -= config.CLOCK_UPDATE_SPEED
        if self._updatingTimingClock1 <= 0:
            self._resetTimerClock1()  # Reset the clock

            # Close the setting dialog when necessary
            if self._gameSetting is True:
                self._gameSettingTiming -= config.CLOCK_UPDATE_SPEED * 2.5
                if self._gameSettingTiming <= 0:
                    self._gameSetting = False
                    self.dialogSignal.emit()
                    self._build()

    # ----------------------------------------------------------------------------------------------------------
    # [4]: Game Building Time
    def _build(self):
        # [1]: Setup Game Engine
        # [1.1]: Setup Game Engine
        self.__gameCore = minesweeper(size=self._playingMatrixSize, difficulty=self._playingDifficulty, verbose=False)
        temporary_interface_matrix: np.ndarray = self.__gameCore.getInterfaceMatrix()
        temporary_core_matrix: np.ndarray = self.__gameCore.getCoreMatrix()

        # [1.2]: Finding Image Scaling Size
        size: Tuple[int, int] = config.NODES_SIZE
        scale: Tuple[float, float] = (size[0] / config.getBombNumberImage(key=-1)[0],
                                      size[1] / config.getBombNumberImage(key=-1)[1])
        print(size, scale)
        self.interface_matrix = [[0] * temporary_interface_matrix.shape[1]] * temporary_interface_matrix.shape[0]
        print(self.interface_matrix)

        for row in range(0, temporary_core_matrix.shape[0]):
            for col in range(0, temporary_core_matrix.shape[1]):
                node = InterfaceNode(row, col, int(temporary_core_matrix[row, col]), scale, self.__gameCore.click, self)

                self.interface_matrix[row][col] = node



    # ----------------------------------------------------------------------------------------------------------
    # [x]: Getter & Setter Function
    def setMatrixSize(self, width: int, height: int) -> None:
        self._playingMatrixSize = (width, height)

    def setDifficultyLevel(self, difficulty: str) -> None:
        self._playingDifficulty = difficulty

    def setPlayerName(self, name: str) -> None:
        if name != self.getPlayerName():
            self._playerName = name

    def getMatrixSize(self) -> Tuple[int, int]:
        return self._playingMatrixSize

    def getDifficultyLevel(self) -> str:
        return self._playingDifficulty

    def getPlayerName(self) -> str:
        return self._playerName

    def activateGameSetting(self) -> None:
        self._gameSetting = True

    def deactivateGameSetting(self) -> None:
        self._gameSetting = False
