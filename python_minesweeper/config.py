from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time
import config
from typing import Tuple, List, Union, Optional
from core import minesweeper
from component_interface import NumberForUICore


class GameWindow(QMainWindow):
    gamingSignal = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        # [1]: Initialize Window
        super(GameWindow, self).__init__(*args, **kwargs)
        self.setEnabled(a0=True)
        self.setMouseTracking(enable=True)
        self.setUpdatesEnabled(enable=True)
        self.setVisible(visible=True)
        self.setAcceptDrops(on=True)
        self.setFocus()
        self.setTabletTracking(enable=True)

        # [2]: Setup Core & Associated Attribute
        self.playingTime: Optional[float] = None
        self.playingMatrixSize: Optional[Tuple[int, int]] = None
        self.playingDifficulty: Optional[str] = None
        self.gameCore: Optional[minesweeper] = None

        # Opening Background
        self.welcome_background: Optional[QPixmap] = QPixmap(self)
        self.welcome_title: Optional[QPixmap] = QPixmap(self)
        self.welcome_playButton: Optional[QPushButton] = QPushButton(self)

        # Gaming Level

        # Playing Background
        self.interface_matrix: List[List[NumberForUICore]] = []

    def welcome(self):
        # self.welcome_background: QLabel = QLabel(config.getOpenInterface(key="Opening"))
        pass

    def makeDialog(self):
        # In this task, we want to make a dialog to communicate with user about the gaming mode they want to play.
        # In fact, we don't worry about the memory as it would be deleted after its complete its job

        # [1]: Setup Difficulty Level based on its associated value
        difficulties_level: List[str] = [key for key, value in config.DIFFICULTY.items() if 0 < value <= 0.5]

        # [2]: Make a dialog
        mainDialog: QDialog = QDialog()
        mainDialog.setEnabled(a0=True)
        mainDialog.setMouseTracking(enable=True)
        mainDialog.setUpdatesEnabled(enable=True)
        mainDialog.setVisible(visible=True)
        mainDialog.setAcceptDrops(on=True)
        mainDialog.setFocus()
        mainDialog.setTabletTracking(enable=True)

        mainDialog.setFixedSize(*config.DIALOG_SIZE)
        mainDialog.setWindowTitle(a0="Minesweeper")

        # [3]:
        comboBox = QComboBox(mainDialog)
        comboBox.setEnabled(a0=True)
        comboBox.setMouseTracking(enable=True)
        comboBox.setUpdatesEnabled(enable=True)
        comboBox.setVisible(visible=True)
        comboBox.setAcceptDrops(on=True)
        comboBox.setFocus()
        comboBox.setTabletTracking(enable=True)
