import numpy as np
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from time import time, sleep
import config
from typing import Tuple, List, Union, Optional, Callable
from core import minesweeper
from component_interface import InterfaceNode, GamingMode, HoveringButton, TableModel
from preprocessing import ReadFile, ExportFile
import pandas as pd


class GameWindow(QMainWindow):
    # https://zetcode.com/gui/pyqt5/eventssignals/

    dialogSignal = pyqtSignal()

    def __init__(self, *args, **kwargs):
        # [1]: Initialize Window
        super(GameWindow, self).__init__(*args, **kwargs)
        self.setGeometry(0, 0, *config.WINDOW_SIZE)
        self.setFixedSize(*config.WINDOW_SIZE)
        self.setWindowIcon(QIcon(config.getIcon(get_size=False)))
        self.setIconSize(QSize(*config.getIcon(get_size=True)))
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

        self._playingWidth: int = -1
        self._playingHeight: int = -1

        # ----------------------------------------------------------------------------------------------------------
        # [3.1]: Opening Interface
        self.welcome_background: QLabel = QLabel(self)
        self.welcome_title: QLabel = QLabel(self)
        self.welcome_playButton: HoveringButton = HoveringButton(self)
        self.dialog: GamingMode = GamingMode(self._playingMatrixSize, self._playingDifficulty,
                                             self._playerName, self)
        self.dialog.currentSignal.connect(self._assignGame)
        self.dialogSignal.connect(self.deactivateDialog)
        self.dialog.update()
        self.dialog.hide()

        self.displayOpeningStatus: bool = True

        # [3.2]: Ending Interface
        # [3.2.1]: Setup Core
        self.ending_background: QLabel = QLabel(self)
        self.ending_title: QLabel = QLabel(self)
        self.ending_performanceLabel: QLabel = QLabel(self)
        self.ending_matchResult: QLabel = QLabel(self)
        self.ending_displayRanking: QTableView = QTableView(self)
        self.ending_replayButton: HoveringButton = HoveringButton(self)

        self.displayEndingStatus: bool = False

        # [3.2.2]: Setup Extra Attribute for Transferring
        self._viewingTimeToEnding: Union[int, float] = config.VIEWING_TIME_FOR_TRANSFER

        # [4]: Playing Ground
        # In the playing background we have timer to display, number of assigned flags, redo - undo button
        # [4.1]: Setup Core
        self.interface_matrix: Optional[List[List[Union[InterfaceNode, int]]]] = None
        self.playing_background: QLabel = QLabel(self)
        self.displayGamingStatus: bool = False

        # [4.2.1]: Setup Associated Attribute
        self._startingDate: Optional[float] = None  # Used to save the date when playing the game
        self._startingTime: Optional[float] = None  # Used to save the time when playing the game

        self._playingTime: Optional[float] = None  # Used to save the time of playing when start the match
        self._playingRunningTime: Optional[float] = None  # Used to save the time of playing when start the match

        self._countingQTimerClock2: QTimer = QTimer(self)  # This clock only activate when you start the game
        self._countingQTimerClock2.timeout.connect(self._updateSettingClock2)

        self._countingTimerQLCDClock2: QLCDNumber = QLCDNumber(self)  # Used to display amount of time spent on the game
        self._countingTimerQLCDClock2.display(self._playingRunningTime)

        # [4.2.3]: Setup Associated Button & Label for Display
        self._countingFlagsQLCDClock3: QLCDNumber = QLCDNumber(self)  # Used to number of remaining flags
        self._remainingFlagsSample: QLabel = QLabel(self)

        self._TimerSample: QLabel = QLabel(self)

        self.UndoButton: HoveringButton = HoveringButton(self)
        self.RedoButton: HoveringButton = HoveringButton(self)

        # ----------------------------------------------------------------------------------------------------------
        # [5]: Running Function
        self.keyClickEvent: List[Union[Qt.Key, int, hex]] = []
        self.isReplay: bool = False

        self._setup()
        self.prepareGame()

    # ----------------------------------------------------------------------------------------------------------
    # [1]: Setup Function
    def _setup(self):
        ComboBoxSize: Tuple[int, int] = (180, 60)
        InformationSize: Tuple[int, int] = (95, 60)
        # [1]: Initialize Window
        if True:
            self.setEnabled(True)
            self.setMouseTracking(True)
            self.setUpdatesEnabled(True)
            self.setVisible(True)
            self.setFocus()
            self.setWindowIcon(QIcon(config.getIcon(get_size=False)))
            self.setIconSize(QSize(*config.getIcon(get_size=True)))
            self.setStyleSheet("QMainWindow {background-color: darkgrey; border-style: outset; "
                               "background: transparent; color: red; font: bold;}")

        # [2.1]: Opening Interface
        if True:
            self.welcome_background.setEnabled(True)
            self.welcome_background.setMouseTracking(True)
            self.welcome_background.setUpdatesEnabled(True)
            self.welcome_background.setVisible(True)
            self.welcome_background.setScaledContents(True)
            self.welcome_background.setFocus()
            self.welcome_background.hide()

            self.welcome_title.setEnabled(True)
            self.welcome_title.setMouseTracking(True)
            self.welcome_title.setUpdatesEnabled(True)
            self.welcome_title.setVisible(True)
            self.welcome_title.setScaledContents(True)
            self.welcome_title.setFocus()
            self.welcome_title.hide()

            self.welcome_playButton.setEnabled(True)
            self.welcome_playButton.setMouseTracking(True)
            self.welcome_playButton.setUpdatesEnabled(True)
            self.welcome_playButton.setVisible(True)
            self.welcome_playButton.setFocus()
            self.welcome_playButton.hide()

        # [2.2]: Ending Interface
        if True:
            self.ending_background.setMouseTracking(True)
            self.ending_background.setUpdatesEnabled(True)
            self.ending_background.setVisible(True)
            self.ending_background.setScaledContents(True)
            self.ending_background.setFocus()
            self.ending_background.hide()

            self.ending_title.setMouseTracking(True)
            self.ending_title.setUpdatesEnabled(True)
            self.ending_title.setVisible(True)
            self.ending_title.setScaledContents(True)
            self.ending_title.setFocus()
            self.ending_title.hide()

            self.ending_performanceLabel.setMouseTracking(True)
            self.ending_performanceLabel.setUpdatesEnabled(True)
            self.ending_performanceLabel.setVisible(True)
            self.ending_performanceLabel.setScaledContents(True)
            self.ending_performanceLabel.setFocus()
            self.ending_performanceLabel.hide()

            self.ending_matchResult.setMouseTracking(True)
            self.ending_matchResult.setUpdatesEnabled(True)
            self.ending_matchResult.setVisible(True)
            self.ending_matchResult.setScaledContents(True)
            self.ending_matchResult.setFocus()
            self.ending_matchResult.hide()

            self.ending_displayRanking.setMouseTracking(True)
            self.ending_displayRanking.setSortingEnabled(True)
            self.ending_displayRanking.setUpdatesEnabled(True)
            self.ending_displayRanking.setVisible(True)
            self.ending_displayRanking.setFocus()
            self.ending_displayRanking.hide()

            self.ending_replayButton.setMouseTracking(True)
            self.ending_replayButton.setUpdatesEnabled(True)
            self.ending_replayButton.setVisible(True)
            self.ending_replayButton.setFocus()
            self.ending_replayButton.ensurePolished()
            self.ending_replayButton.setFlat(False)
            self.ending_replayButton.setAutoFillBackground(False)
            self.ending_replayButton.hide()

        # [3]: Playing Ground
        if True:
            self.playing_background.setEnabled(True)
            self.playing_background.setMouseTracking(True)
            self.playing_background.setUpdatesEnabled(True)
            self.playing_background.setVisible(True)
            self.playing_background.setScaledContents(True)
            self.playing_background.setFocus()
            self.playing_background.setStyleSheet("border-style: outset; background: transparent; "
                                                  "background-repeat: no-repeat")
            self.playing_background.hide()

            self._countingFlagsQLCDClock3.setDecMode()
            self._countingFlagsQLCDClock3.setDigitCount(4)
            self._countingFlagsQLCDClock3.setNumDigits(4)
            self._countingFlagsQLCDClock3.setStyleSheet("color: red; border-style: outset;")
            self._countingFlagsQLCDClock3.setSmallDecimalPoint(False)
            self._countingFlagsQLCDClock3.hide()

            self._remainingFlagsSample.setEnabled(True)
            self._remainingFlagsSample.setMouseTracking(True)
            self._remainingFlagsSample.setUpdatesEnabled(True)
            self._remainingFlagsSample.setVisible(True)
            self._remainingFlagsSample.setScaledContents(True)
            self._remainingFlagsSample.setFocus()
            self._remainingFlagsSample.hide()

            self._countingTimerQLCDClock2.setDecMode()
            self._countingTimerQLCDClock2.setDigitCount(4)
            self._countingTimerQLCDClock2.setNumDigits(4)
            self._countingTimerQLCDClock2.setStyleSheet("color: red; border-style: outset;")
            self._countingTimerQLCDClock2.setSmallDecimalPoint(False)
            self._countingTimerQLCDClock2.hide()

            self._TimerSample.setEnabled(True)
            self._TimerSample.setMouseTracking(True)
            self._TimerSample.setUpdatesEnabled(True)
            self._TimerSample.setVisible(True)
            self._TimerSample.setScaledContents(True)
            self._TimerSample.setFocus()
            self._TimerSample.hide()

            self.RedoButton.setEnabled(True)
            self.RedoButton.setMouseTracking(True)
            self.RedoButton.setUpdatesEnabled(True)
            self.RedoButton.setVisible(True)
            self.RedoButton.setFocus()
            self.RedoButton.ensurePolished()
            self.RedoButton.setFlat(False)
            self.RedoButton.setAutoFillBackground(False)
            self.RedoButton.hide()

            self.UndoButton.setEnabled(True)
            self.UndoButton.setMouseTracking(True)
            self.UndoButton.setUpdatesEnabled(True)
            self.UndoButton.setVisible(True)
            self.UndoButton.setFocus()
            self.UndoButton.ensurePolished()
            self.UndoButton.setFlat(False)
            self.UndoButton.setAutoFillBackground(False)
            self.UndoButton.hide()

        # [4]: Extra Attribute
        pass

    # ----------------------------------------------------------------------------------------------------------
    # [2]: Timing Function
    def _updateSettingClock1(self):
        self._updatingTimingClock1 -= config.CLOCK_UPDATE_SPEED
        if self._updatingTimingClock1 <= 0:
            self._updatingTimingClock1 = config.UPDATING_TIMING  # Reset the clock

            # Close the setting dialog when necessary
            if self._gameSetting is True:
                self._viewingTimeToEnding -= 5 * config.CLOCK_UPDATE_SPEED
                if self._viewingTimeToEnding <= 0:
                    self._viewingTimeToEnding = config.UPDATING_TIMING
                    self.deactivateGameSetting()
                    self.dialogSignal.emit()
                    self.startGame()

    def _updateSettingClock2(self):
        self._playingRunningTime = time() - self._playingTime

        self._countingFlagsQLCDClock3.display(self.__gameCore.getRemainingFlags())
        self._countingTimerQLCDClock2.display(int(self._playingRunningTime))

        if self.__gameCore.checkIfPlayable() is False:
            self._viewingTimeToEnding -= config.CLOCK_UPDATE_SPEED
            if self._viewingTimeToEnding <= 0:
                self._viewingTimeToEnding = config.VIEWING_TIME_FOR_TRANSFER
                # Create a message box to win
                text = "CONGRAT :) YOU HAVE WON THE GAME" \
                    if self.__gameCore.checkIfVictory() else "OH NO :( YOU HAVE LOST THE GAME"
                pixmap = QPixmap(config.getIcon(get_size=False))
                pixmap.scaled(*config.getIcon(get_size=True), Qt.KeepAspectRatio, Qt.SmoothTransformation)

                messageBox: QMessageBox = QMessageBox(self)
                messageBox.setIconPixmap(pixmap)
                messageBox.setText(text)
                messageBox.setWindowTitle("Performance Status")
                messageBox.setStyleSheet("color: white; font: bold; background: translucent; border-style: outset")
                messageBox.setFocus()
                messageBox.setWindowOpacity(0.85)
                messageBox.setFixedSize(600, 300)
                messageBox.exec()
                messageBox.deleteLater()

                self.stopGame()

    # ----------------------------------------------------------------------------------------------------------
    # [3]: Opening Function
    def _updateDialog(self):
        self.dialog.update()

    def activateDialog(self):
        self._updateDialog()
        self.dialog.show()

    def deactivateDialog(self):
        self._updateDialog()
        self.dialog.hide()

    def _assignGame(self, width: int, height: int, difficulty: str, name: str) -> None:
        # This is the function called (slots) of the input dialog that would raise when click on play button
        self.activateGameSetting()
        self.setMatrixSize(width=width, height=height)
        self.setDifficultyLevel(difficulty=difficulty)
        self.setPlayerName(name=name)

    def _makeDialog(self) -> None:
        # [1]: Hide the main window and resize its later
        self.move((config.WINDOW_SIZE[0] - config.DIALOG_SIZE[0]) // 2,
                  (config.WINDOW_SIZE[1] - config.DIALOG_SIZE[1]) // 2)
        self.setFixedSize(*config.DIALOG_SIZE)
        self.deactivateOpeningInterface()
        self.update()
        self.show()

        self.activateDialog()

    def _initializeOpeningInterface(self) -> None:
        # [1]: Make background and associated title
        self.welcome_background.lower()
        self.welcome_background.setPixmap(QPixmap(config.getOpenInterface(key="Opening")))
        self.welcome_background.setGeometry(0, 0, *config.getOpenInterface(key="Opening", get_size=True))

        self.welcome_title.raise_()
        self.welcome_title.setPixmap(QPixmap(config.getOpenInterface(key="Title")))
        self.welcome_title.setGeometry(1100, 100, *config.getOpenInterface(key="Title", get_size=True))

        # [3]: Making self.welcome_playButton
        self.welcome_playButton.raise_()
        width, height = config.getOpenInterface(key="Play", get_size=True)
        self.welcome_playButton.setImage(width=width, height=height,
                                         defaultImage=config.getOpenInterface(key="Play"),
                                         hoverImage=config.getOpenInterface(key="Play-hover"))
        self.welcome_playButton.setGeometry(1300, 700, width, height)
        self.welcome_playButton.clicked.connect(self._makeDialog)

    def prepareGame(self) -> None:
        # [0]: Set corresponding window size
        self.move(0, 0)
        self.setFixedSize(*config.WINDOW_SIZE)

        # [1]: Initialize All of Them
        if self.isReplay is False:
            self._initializeOpeningInterface()

        # [2]: Display Result
        self.activateOpeningInterface()

        self.update()
        self.show()

    # ----------------------------------------------------------------------------------------------------------
    # [4]: Gaming Function
    # [4.1]: Initialization
    def _buildGameEngine(self):
        # [1]: Setup Game Engine
        # [1.1]: Setup Game Engine
        if self.__gameCore is not None:
            del self.__gameCore  # Adaptation when replay

        self.__gameCore = minesweeper(size=self._playingMatrixSize, difficulty=self._playingDifficulty, verbose=False)
        getNode: Callable = self.__gameCore.getCoreNode
        y_size: int = self.__gameCore.getNumberOfNodesInVerticalAxis()
        x_size: int = self.__gameCore.getNumberOfNodesInHorizontalAxis()

        # [1.2]: Finding Image Scaling Size - Scale if not fit with the matrix. Note that we also have
        # extra section on top for drawing

        size: List[int] = list(config.NODES_SIZE)  # The size of each nodes on the tables (x, y)
        maximum_nodes: int = (min(config.WINDOW_SIZE) - config.BOARD_LENGTH - 75) // \
                             (min(size) + min(config.BOMB_NUMBER_DISPLAY["Separation"]))

        while maximum_nodes <= x_size:  # Adaptation Only
            # Update Nodes Size - Update Separation - Calculate max nodes again
            size[0] -= 1
            size[1] -= 1
            config.BOMB_NUMBER_DISPLAY["Separation"] = [int(size[0] // 4), int(size[1] // 4)]
            maximum_nodes: int = (min(config.WINDOW_SIZE) - config.BOARD_LENGTH - 75) // \
                                 (min(size) + min(config.BOMB_NUMBER_DISPLAY["Separation"]))

        # Get Image Scaling Factor
        scale: Tuple[float, float] = (size[0] / config.getBombNumberImage(key=-1)[0],
                                      size[1] / config.getBombNumberImage(key=-1)[1])

        # [2]: Build Interface Matrix
        if self.interface_matrix:
            self.interface_matrix.clear()  # Adaptation when replay

        self.interface_matrix = [[InterfaceNode(y, x, int(getNode(y=y, x=x)), tuple(scale), self.clickOnNodes, self)
                                  for x in range(0, x_size)] for y in range(0, y_size)]
        sleep(0.05)
        self._playingWidth = x_size * (size[0] + config.BOMB_NUMBER_DISPLAY["Separation"][0]) + \
                             config.BOMB_NUMBER_DISPLAY["Initial"][1]
        self._playingHeight = y_size * (size[1] + config.BOMB_NUMBER_DISPLAY["Separation"][1]) + \
                              config.BOMB_NUMBER_DISPLAY["Initial"][1] + config.BOARD_LENGTH

    def _initializeGamingInterface(self) -> None:
        distance: int = int(config.BOARD_LENGTH * 0.9)  # Code Shortening
        sep: int = (config.BOARD_LENGTH - distance) // 2

        # [0]: Initialize Background
        self.playing_background.setGeometry(0, 0, self._playingWidth, self._playingHeight)
        self.playing_background.setPixmap(QPixmap(config.getGamingBackground(get_size=False)))
        self.playing_background.setScaledContents(True)
        self.playing_background.lower()

        # [1]: Assign remaining flags for display
        self._countingFlagsQLCDClock3.setMinimumSize(distance, distance)
        self._countingFlagsQLCDClock3.setGeometry(sep, sep, distance, distance)
        self._countingFlagsQLCDClock3.raise_()

        self._remainingFlagsSample.setPixmap(QPixmap(config.getFlagImage(key="Initial")))
        self._remainingFlagsSample.setGeometry(sep + distance, sep, distance, distance)

        # [2]: Build Timer
        self._countingTimerQLCDClock2.setMinimumSize(distance, distance)
        self._countingTimerQLCDClock2.setGeometry(self._playingWidth - 2 * distance - 4, sep, distance, distance)
        self._countingTimerQLCDClock2.raise_()

        self._TimerSample.setPixmap(QPixmap(config.getTimerImage(get_size=False)))
        self._TimerSample.setGeometry(self._playingWidth - distance - 2, sep, distance, distance)

        # [3]: Making Undo - Redo Button
        widthHeightRatio: float = int(config.getExtraButton(key=-1)[0]) / int(config.getExtraButton(key=-1)[1])

        # Undo on the Left
        self.UndoButton.raise_()
        self.UndoButton.setImage(width=int(distance * widthHeightRatio), height=distance,
                                 defaultImage=config.getExtraButton(key="Undo"),
                                 hoverImage=config.getExtraButton(key="Undo-hover"))
        self.UndoButton.setGeometry((self._playingWidth - distance) // 2 - int(distance * widthHeightRatio), 2,
                                    int(distance * widthHeightRatio), distance)
        self.UndoButton.clicked.connect(self.clickUndoButton)

        # Redo on the Right
        self.RedoButton.raise_()
        self.RedoButton.setImage(width=int(distance * widthHeightRatio), height=distance,
                                 defaultImage=config.getExtraButton(key="Redo"),
                                 hoverImage=config.getExtraButton(key="Redo-hover"))
        self.RedoButton.setGeometry((self._playingWidth + distance) // 2, 2, int(distance * widthHeightRatio), distance)
        self.RedoButton.clicked.connect(self.clickRedoButton)

    def _resetPlayingClock(self) -> None:
        from datetime import datetime

        # [1]: Set up the starting time
        current_time = datetime.now()
        self._startingDate: str = current_time.strftime("%d/%m/%Y")
        self._startingTime: str = current_time.strftime("%H:%M:%S")

        # [2]: Set up the playing time
        self._playingTime: float = time()
        self._playingRunningTime: float = 0

    def startGame(self) -> None:
        # [1]: Setup the game engine for the game
        self._buildGameEngine()

        # [2]: Initialize background
        self.move((config.WINDOW_SIZE[0] - self._playingWidth) // 2,
                  (config.WINDOW_SIZE[1] - self._playingHeight - config.BOARD_LENGTH) // 2)
        self.setFixedSize(self._playingWidth, self._playingHeight)
        self.update()
        self.show()

        # [3]: Configuring the clock
        self._resetPlayingClock()

        # [4]: Initialize background & associated label or button to click
        if self.isReplay is False:
            self._initializeGamingInterface()

        # [5]: Display Result
        self.activateGamingInterface()

        self.update()
        self.show()

    # [4.2]: (Interface) Matrix Clicking
    def _revealAllNodes(self) -> None:
        for y in range(0, self.__gameCore.getNumberOfNodesInVerticalAxis()):
            for x in range(0, self.__gameCore.getNumberOfNodesInHorizontalAxis()):
                self.interface_matrix[y][x].updateStatus(interfaceStatus=self.__gameCore.getInterfaceNode(y=y, x=x))
                self.interface_matrix[y][x].reveal()

    def _updateGamingStatus(self) -> None:
        for y in range(0, self.__gameCore.getNumberOfNodesInVerticalAxis()):
            for x in range(0, self.__gameCore.getNumberOfNodesInHorizontalAxis()):
                self.interface_matrix[y][x].updateStatus(interfaceStatus=self.__gameCore.getInterfaceNode(y=y, x=x))
                self.interface_matrix[y][x].updateGamingImage()

    def clickOnNodes(self, y: int, x: int, mouse: str):
        # Attached function that become an observer to receive - transmit communication
        # [1]: Update the core matrix
        self.__gameCore.click(y=y, x=x, message=mouse)

        # [2]: Get the interface matrix & Update
        # If the core does not allow to continue playing. Stopping the game
        if self.__gameCore.checkIfPlayable() is True:
            self._updateGamingStatus()
        else:
            self._revealAllNodes()

        # [3]: Update when needed
        self.update()

    def clickUndoButton(self) -> None:
        # This function only works if you can continue playing the game
        if self.__gameCore.checkIfPlayable() is False:
            self.__gameCore.checkGamingStatus()

        if self.__gameCore.checkIfPlayable() is True:
            # [1]: Click Undo Button
            self.__gameCore.clickUndo()

            # [2]: Apply back into interface nodes
            self._updateGamingStatus()

            # [3]: Update when needed
            self.update()

        return None

    def clickRedoButton(self) -> None:
        # This function only works if you can continue playing the game
        if self.__gameCore.checkIfPlayable() is False:
            self.__gameCore.checkGamingStatus()

        if self.__gameCore.checkIfPlayable() is True:
            # [1]: Click Redo Button
            self.__gameCore.clickRedo()

            # [2]: Apply back into interface nodes
            self._updateGamingStatus()

            # [3]: Update when needed
            self.update()

        return None

    # ----------------------------------------------------------------------------------------------------------
    # [5]: Ending Interface
    def replay(self) -> None:
        # Associated Function when you need to replay
        self.isReplay = True

        # [1]: Deactivate everything possible
        self.deactivateOpeningInterface()
        self.deactivateGamingInterface()
        self.deactivateEndingInterface()

        # [2]: Update Gaming Status
        self._setup()

        # [3]: Update & Display Result
        self.prepareGame()
        self.activateOpeningInterface()

        self.update()
        self.show()

    def _initializeEndingInterface(self) -> None:
        # [1]: Make background and associated performance
        self.ending_background.lower()
        self.ending_background.setPixmap(QPixmap(config.getEndInterface(key="Ending")))
        self.ending_background.setGeometry(0, 0, *config.getEndInterface(key="Ending", get_size=True))
        self.ending_background.setWindowOpacity(0.85)

        self.ending_title.raise_()
        self.ending_title.setPixmap(QPixmap(config.getOpenInterface(key="Title")))
        x = list(config.getOpenInterface(key="Title", get_size=True))
        self.ending_title.setGeometry((config.WINDOW_SIZE[0] - x[0]) // 2, 20, *x)

        self.ending_performanceLabel.raise_()
        mode: str = "Win" if self.__gameCore.checkIfVictory() is True else "Lose"
        self.ending_performanceLabel.setPixmap(QPixmap(config.getEndInterface(key=mode)))
        y = list(config.getEndInterface(key=mode, get_size=True))
        y[0], y[1] = int(y[0] // 2), int(y[1] // 2)
        self.ending_performanceLabel.setGeometry((config.WINDOW_SIZE[0] - y[0]) // 2, 2 * 20 + x[1], *y)

        # [2]: Making self.ending_replayButton
        z = list(config.getEndInterface(key="Replay", get_size=True))
        self.ending_replayButton.setImage(width=z[0], height=z[1], defaultImage=config.getEndInterface(key="Replay"),
                                          hoverImage=config.getEndInterface(key="Replay-hover"))
        self.ending_replayButton.setGeometry((config.WINDOW_SIZE[0] - z[0]) // 2, config.WINDOW_SIZE[1] - z[1] - 100, *z)
        self.ending_replayButton.raise_()
        self.ending_replayButton.clicked.connect(self.replay)

        # [3]: Viewing Pandas Record
        df = ReadFile(FilePath=config.DIRECTORY + "/resources/score/{}.csv".format(self._playingDifficulty),
                      nrows=config.TABLE_MAX_DISPLAY, header=0)
        t = config.TABLE_VIEW
        self.ending_displayRanking.setModel(TableModel(df))
        self.ending_displayRanking.setGeometry((config.WINDOW_SIZE[0] - t[0]) // 2, 2 * 35 + x[1] + y[1],
                                               *config.TABLE_VIEW)
        self.ending_displayRanking.setSortingEnabled(True)
        self.ending_displayRanking.resizeColumnsToContents()
        self.ending_displayRanking.resizeRowsToContents()
        self.ending_displayRanking.scrollToTop()

    def _updatePlayerPerformance(self) -> None:
        path: str = config.DIRECTORY + "/resources/score/{}.csv".format(self._playingDifficulty)
        value, columns = ReadFile(FilePath=path, header=0, get_values=True, get_columns=True)
        if self.__gameCore.checkIfPlayable() is True:
            winningStatus: str = "DROP"
        elif self.__gameCore.checkIfVictory() is True:
            winningStatus: str = "WIN"
        else:
            winningStatus: str = "LOSE"
        add_new = [[self._startingDate, self._startingTime, self._playerName,
                    round(self._playingRunningTime, 3), winningStatus]]
        ExportFile(DataFrame=pd.DataFrame(data=np.concatenate((add_new, value), axis=0), columns=columns, index=None),
                   FilePath=path, )

    def stopGame(self) -> None:
        # [0]: Set corresponding window size
        self.move(0, 0)
        self.setFixedSize(*config.WINDOW_SIZE)
        self.update()
        self.show()

        # [1]: Stopping everything of the game
        self.deactivateGamingInterface()

        # [2]: Upload Database by Performance
        self._updatePlayerPerformance()

        # [3]: Initialize Ending Interface
        if self.isReplay is False:
            self._initializeEndingInterface()

        # [4]: Activate everything of the ending interface and display result
        self.activateEndingInterface()

        self.update()
        self.show()

    # ----------------------------------------------------------------------------------------------------------
    # [7]: Window (Interface)
    def _updateOpeningInterface(self) -> None:
        self.welcome_title.update()
        self.welcome_background.update()
        self.welcome_playButton.update()

    def activateOpeningInterface(self) -> None:
        self._updateOpeningInterface()

        self.welcome_title.show()
        self.welcome_background.show()
        self.welcome_playButton.show()

        self.displayOpeningStatus = True

    def deactivateOpeningInterface(self) -> None:
        self._updateOpeningInterface()

        self.welcome_title.hide()
        self.welcome_background.hide()
        self.welcome_playButton.hide()

        self.displayOpeningStatus = False

    def _updateGamingInterface(self) -> None:
        self.playing_background.update()

        self._countingFlagsQLCDClock3.update()
        self._remainingFlagsSample.update()

        self._countingTimerQLCDClock2.update()
        self._TimerSample.update()

        self.RedoButton.update()
        self.UndoButton.update()

    def activateGamingInterface(self) -> None:
        self._updateGamingInterface()

        self._countingFlagsQLCDClock3.display(self.__gameCore.getRemainingFlags())
        self._countingFlagsQLCDClock3.show()

        self._countingTimerQLCDClock2.display(self._playingRunningTime)
        self._countingTimerQLCDClock2.show()

        self._countingQTimerClock2.start(config.CLOCK_UPDATE_SPEED)

        self._remainingFlagsSample.show()
        self._TimerSample.show()
        self.RedoButton.show()
        self.UndoButton.show()

        for y in range(len(self.interface_matrix)):
            for x in range(len(self.interface_matrix[y])):
                self.interface_matrix[y][x].show()

        self.displayGamingStatus = True

    def deactivateGamingInterface(self) -> None:
        self._updateGamingInterface()

        self._countingFlagsQLCDClock3.hide()
        self._countingTimerQLCDClock2.hide()

        self._countingQTimerClock2.stop()

        self._remainingFlagsSample.hide()
        self._TimerSample.hide()
        self.RedoButton.hide()
        self.UndoButton.hide()

        for sub_matrix in self.interface_matrix:
            for node in sub_matrix:
                node.hide()

        self.displayGamingStatus = False

    def _updateEndingInterface(self) -> None:
        self.ending_background.update()
        self.ending_title.update()
        self.ending_performanceLabel.update()
        self.ending_matchResult.update()
        self.ending_displayRanking.update()
        self.ending_replayButton.update()

    def activateEndingInterface(self) -> None:
        self._updateEndingInterface()

        self.ending_background.show()
        self.ending_title.show()
        self.ending_performanceLabel.show()
        self.ending_matchResult.show()
        self.ending_displayRanking.show()
        self.ending_replayButton.show()

        self.displayEndingStatus = True

    def deactivateEndingInterface(self) -> None:
        self._updateEndingInterface()

        self.ending_background.hide()
        self.ending_title.hide()
        self.ending_performanceLabel.hide()
        self.ending_matchResult.hide()
        self.ending_displayRanking.hide()
        self.ending_replayButton.hide()

        self.displayEndingStatus = False

    # ----------------------------------------------------------------------------------------------------------
    # [8]: Set Size
    def keyPressEvent(self, a0: QKeyEvent) -> None:
        self.keyClickEvent.append(a0.key())

    def keyReleaseEvent(self, a0: QKeyEvent) -> None:
        # TODO
        if self.keyClickEvent[0] == Qt.Key_Return:
            if self.displayOpeningStatus is True:
                self._makeDialog()

            elif self.displayEndingStatus is True:
                self.replay()

            self.keyClickEvent.pop()

        elif self.keyClickEvent[0] == Qt.Key_Control:
            if len(self.keyClickEvent) == 2:
                if self.keyClickEvent[1] == Qt.Key_Z:
                    self.clickUndoButton()

            if len(self.keyClickEvent) == 3:
                if self.keyClickEvent[1] == Qt.Key_Shift and self.keyClickEvent[2] == Qt.Key_Z:
                    self.clickRedoButton()

            del self.keyClickEvent
            self.keyClickEvent.clear()

    # ----------------------------------------------------------------------------------------------------------
    # [x]: Getter & Setter Function
    def setMatrixSize(self, width: int, height: int) -> None:
        if self.getMatrixSize() != (width, height):
            self._playingMatrixSize = (width, height)

    def setDifficultyLevel(self, difficulty: str) -> None:
        if self.getDifficultyLevel() != difficulty:
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

    def displayInterfaceMatrixStatus(self) -> None:
        copy_version = np.zeros(shape=(self._playingMatrixSize[0], self._playingMatrixSize[1]), dtype=np.uint8)
        for row in range(len(self.interface_matrix)):
            for col in range(len(self.interface_matrix[row])):
                copy_version[row, col] = self.interface_matrix[row][col].getInterfaceStatus()
            print(copy_version[row])
        return None

    def displayInterfaceNodesValue(self) -> None:
        copy_version = np.zeros(shape=(self._playingMatrixSize[0], self._playingMatrixSize[1]), dtype=np.int8)
        for row in range(len(self.interface_matrix)):
            for col in range(len(self.interface_matrix[row])):
                copy_version[row, col] = self.interface_matrix[row][col].getValue()
            print(copy_version[row])
        return None
