from typing import Tuple, List, Union, Optional, Callable

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from config import CORE_CONFIGURATION as CONFIG, getBombNumberImage, getFlagImage, getBombImage, getQuestionImage, \
    BOMB_NUMBER_DISPLAY as number_displayer, DIFFICULTY, DIALOG_SIZE


class InterfaceNode(QLabel):

    __slots__ = ("y", "x", "_value", "_interfaceStatus", "_isMine", "_imageSize", "_imageInterface",
                 "_bombInterface", "_flagInterface", "_questionInterface")

    currentSignal = pyqtSignal(int, int, str)

    # The node for displaying function only
    # _imageInterface[0]: Starting Block when Playing, _imageInterface[1]: Value Block when Opened,
    # _bombInterface[0]: Bomb Node for Displaying, _bombInterface[1]: Bomb Exploded when Clicked,
    # _flagInterface[0]: Flag Node when Assigning, _flagInterface[1]: Flag Node if Defused,

    def __init__(self, y: int, x: int, value: int, scalingFactor: Union[Tuple[float, float], float, int] = 1/6.5,
                 slot: Callable = None, *args, **kwargs):
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
                raise ValueError("The value must be integer")

            if isinstance(scalingFactor, (float, int)):
                scalingFactor: Tuple[float, float] = (scalingFactor, scalingFactor)

            pass

        # [1]: Attribute Match-up
        super(InterfaceNode, self).__init__(*args, **kwargs)

        self.y: int = y
        self.x: int = x
        self._value: int = value
        self._interfaceStatus: int = 0
        self._isMine: bool = True if CONFIG["Bomb Notation"] == self._value else False
        self._scalingSize: Tuple[float, float] = scalingFactor

        # [2]: Attribute Creation (by Image)
        # _imageSize: The size of nodes in UI, _imageInterface: The image path of 'number' block,
        # _bombInterface: The image path of 'bomb' block, _flagInterface: The image path of 'flag' block
        # _questionInterface: The image path of 'question' block
        self._imageSize: List[int] = list(getBombNumberImage(key=-1))
        if self._value in range(0, 9):
            self._imageInterface: Tuple[str, str] = (getBombNumberImage(key=None), getBombNumberImage(key=self._value))
        elif self._isMine is True:
            self._imageInterface: Tuple[str, str] = (getBombNumberImage(key=None), getBombImage(key="Excited"))
        else:
            print("False Nodes: y:{} - x:{} ---> Value: {}; isBomb: {}".format(self.y, self.x, self._value, self._isMine))
            raise ValueError("There is no compatible function for notation")
        self._bombInterface: Tuple[str, str] = (getBombImage(key="Initial"), getBombImage(key="Excited"))
        self._flagInterface: Tuple[str, str] = (getFlagImage(key="Initial"), getFlagImage(key="Excited"))
        self._questionInterface: str = getQuestionImage(get_size=False)

        # [3]: Building Function when instantiated
        if slot is not None:
            self.currentSignal.connect(slot)
        self._build()

    # ----------------------------------------------------------------------------------------------------------
    # [0]: Building Function
    def _initializeImage(self) -> None:
        self.setPixmap(QPixmap(self._imageInterface[0]))
        self._resetImageSize()

    def _resetImageSize(self) -> None:
        x_sep, y_sep = number_displayer["Separation"]
        size: Tuple[int, int] = (int(self._imageSize[1] * self._scalingSize[1]),  # x-axis
                                 int(self._imageSize[0] * self._scalingSize[0]))  # y-axis
        pos: List[int] = \
            [number_displayer["Initial"][1] + int(self.x * (size[0] + x_sep)),  # x-axis
             number_displayer["Initial"][0] + int(self.y * (size[1] + y_sep))]  # y-axis

        print(pos, size)
        self.setGeometry(pos[0], pos[1], size[0], size[1])

    def _build(self):
        self.ensurePolished()
        self.setVisible(True)
        self.setMouseTracking(True)
        self.setUpdatesEnabled(True)
        self.setEnabled(True)
        self.setScaledContents(True)
        self.setAcceptDrops(False)
        self.setFocus()

        self._initializeImage()

        self.update()
        self.show()

    def updateImage(self) -> None:
        if self._interfaceStatus == 1:
            if self.checkIfMine() is False:  # Representing Number
                self.setPixmap(QPixmap(self._imageInterface[1]))
            else:  # Displaying the bomb that has been clicked
                self.reveal()
        else:
            if self._interfaceStatus == 0:
                self.setPixmap(QPixmap(self._imageInterface[0]))
            elif self._interfaceStatus == CONFIG["Flag Notation"]:
                self.setPixmap(QPixmap(self._flagInterface[0]))
            elif self._interfaceStatus == CONFIG["Question Notation"]:
                self.setPixmap(QPixmap(self._questionInterface[0]))

        self._resetImageSize()
        self.update()
        self.show()

    def reveal(self) -> bool:
        reveal_status: bool = False
        if self._interfaceStatus != CONFIG["Question Notation"]:
            if self.checkIfMine() is False:
                if self._interfaceStatus == -1:  # If this is a flag that is NOT placed on the bomb
                    self.setPixmap(QPixmap(self._flagInterface[0]))
                else:  # Representing Number
                    self.setPixmap(QPixmap(self._imageInterface[1]))
            else:
                if self._interfaceStatus == -1:  # If this is a flag that is placed on the bomb
                    self.setPixmap(QPixmap(self._flagInterface[1]))
                elif self._interfaceStatus == 1:  # If user accidentally activated the bomb
                    self.setPixmap(QPixmap(self._bombInterface[1]))
                else:
                    self.setPixmap(QPixmap(self._bombInterface[0]))

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

    # ----------------------------------------------------------------------------------------------------------
    # [1]: Interface Function
    def mouseReleaseEvent(self, e: QMouseEvent):
        msg = {Qt.LeftButton: "LeftMouse", Qt.RightButton: "RightMouse"}
        self.currentSignal.emit(self.y, self.x, msg[e.button()])

    # ----------------------------------------------------------------------------------------------------------
    # [x]: Getter & Check and Setter Function
    def getPosition(self) -> Tuple[int, int]:
        return self.y, self.x

    def getValue(self) -> int:
        return self._value

    def checkIfMine(self) -> bool:
        return self._value == CONFIG["Bomb Notation"]

    def getInterfaceStatus(self) -> int:
        return self._interfaceStatus

    def setImageScalingSize(self, scalingSize: Union[Tuple[float, float], float, int]) -> None:
        if isinstance(scalingSize, (float, int)):
            scalingSize: Tuple[float, float] = (scalingSize, scalingSize)
            self._scalingSize = scalingSize

    def updateStatus(self, interfaceStatus: int):
        if interfaceStatus in (0, -1, CONFIG["Flag Notation"], CONFIG["Question Notation"]):
            self._interfaceStatus = interfaceStatus
        else:
            print("No update has been applied")


class GamingMode(QWidget):
    # In this task, we want to make a dialog to communicate with user about the gaming mode they want to play.
    # In fact, we don't worry about the memory as it would be deleted after its complete its job
    currentSignal = pyqtSignal(int, int, str, str)

    def __init__(self, size: int = None, difficulty: str = None, playerName: str = None, *args, **kwargs):
        super(GamingMode, self).__init__(*args, **kwargs)

        # [1.1]: Build a dialog to enable user-computer communication
        self.setFixedSize(*DIALOG_SIZE)
        self.setWindowTitle("Gaming Mode")

        self.background: QLabel = QLabel(self)
        self.background.setGeometry(0, 0, DIALOG_SIZE[0], DIALOG_SIZE[1])
        #
        pixmap = QPixmap(getBombNumberImage(key=0))
        pixmap.scaled(int(max(DIALOG_SIZE) * 1.5), int(max(DIALOG_SIZE) * 1.5), Qt.KeepAspectRatioByExpanding)
        self.background.setScaledContents(True)
        self.background.setPixmap(pixmap)
        self.background.setStyleSheet("background-color: red; ")

        # [1.2]: Building Attribute
        self.difficulty_comboBox: QComboBox = QComboBox(self)
        self.difficulty_info: QLabel = QLabel(self)

        self.matrix_comboBox: QComboBox = QComboBox(self)
        self.matrix_info: QLabel = QLabel(self)

        self.name_lineEdit: QLineEdit = QLineEdit(self)
        self.name_info: QLabel = QLabel(self)

        self.warning_message: QLabel = QLabel(self)
        self.button: QPushButton = QPushButton(self)
        self._setup()

        # [1.3]: Extra non-attribute
        ComboBoxSize: Tuple[int, int] = (190, 50)
        InformationSize: Tuple[int, int] = (85, 50)

        # ----------------------------------------------------------------------------------------------------------
        # [2.1]: Setup Difficulty Level based on its associated value --> self.difficulty_comboBox
        self._difficultyLevel: Tuple[str] = tuple(list(DIFFICULTY.keys()))

        self.difficulty_info.setText("Difficulty: ")
        self.difficulty_info.setGeometry(10, 10, *InformationSize)

        self.difficulty_comboBox.setGeometry(100, 10, *ComboBoxSize)
        self.difficulty_comboBox.addItems(self._difficultyLevel)
        if difficulty is None:
            self.difficulty_comboBox.setCurrentIndex(1)
        else:
            self.difficulty_comboBox.setCurrentIndex(self._difficultyLevel.index(difficulty))
        self.difficulty_comboBox.setPlaceholderText("Choose Your Difficulty Level: ")

        # [2.2]: Setup Size for Playing Matrix --> self.matrix_comboBox
        start_size, end_size = 8, 99
        default_num: int = 16
        self._matrixSize: Tuple[str] = tuple([str(value) for value in range(start_size, end_size)])

        self.matrix_info.setText("Matrix Size: ")
        self.matrix_info.setGeometry(10, 75, *InformationSize)

        self.matrix_comboBox.setGeometry(100, 75, *ComboBoxSize)
        self.matrix_comboBox.addItems(self._matrixSize)
        if size is None:
            self.matrix_comboBox.setCurrentIndex(default_num - start_size)
        else:
            self.matrix_comboBox.setCurrentIndex(size - start_size)
        self.matrix_comboBox.setPlaceholderText("Choose Your Matrix Size: ")

        # [2.3]: Setup Difficulty Level based on its associated value --> self.difficulty_comboBox
        self.name_info.setText("Your Name: ")
        self.name_info.setGeometry(10, 135, *InformationSize)

        self.name_lineEdit.setGeometry(100, 135, *ComboBoxSize)
        self.name_lineEdit.setPlaceholderText("Enter your name: ")
        if playerName is not None:
            self.name_lineEdit.setText(playerName)

        # ----------------------------------------------------------------------------------------------------------
        # [4]: Making a warning message & submission button
        self.warning_message.setGeometry(75, 200, 150, 50)

        self.button.setText("Submit")
        self.button.setGeometry(75, 255, 150, 40)
        self.button.clicked.connect(self.submit)

    def _setup(self) -> None:
        # [1]: Initialize Window
        if True:
            self.setEnabled(True)
            self.setMouseTracking(True)
            self.setUpdatesEnabled(True)
            self.setVisible(True)
            self.setFocus()

        # [2.1]: Initialize Difficulty
        if True:
            self.difficulty_info.setEnabled(True)
            self.difficulty_info.setMouseTracking(True)
            self.difficulty_info.setUpdatesEnabled(True)
            self.difficulty_info.setVisible(True)
            self.difficulty_info.setScaledContents(True)
            self.difficulty_info.setFocus()
            self.difficulty_info.setFont(QFont("Times New Roman", 11))
            self.difficulty_info.setStyleSheet("color: orange; font: bold; border-style: outset")

            self.difficulty_comboBox.setEnabled(True)
            self.difficulty_comboBox.setMouseTracking(True)
            self.difficulty_comboBox.setVisible(True)
            self.difficulty_comboBox.setFocus()
            self.difficulty_comboBox.setFont(QFont("Times New Roman", 11))
            self.difficulty_comboBox.setStyleSheet("color: red; font: bold; border-style: outset;")
            self.difficulty_comboBox.setDuplicatesEnabled(False)

        # [2.2]: Initialize Size
        if True:
            self.matrix_info.setEnabled(True)
            self.matrix_info.setMouseTracking(True)
            self.matrix_info.setUpdatesEnabled(True)
            self.matrix_info.setVisible(True)
            self.matrix_info.setScaledContents(True)
            self.matrix_info.setFocus()
            self.matrix_info.setFont(QFont("Times New Roman", 10))
            self.matrix_info.setStyleSheet("color: orange; font: bold; border-style: outset")

            self.matrix_comboBox.setEnabled(True)
            self.matrix_comboBox.setMouseTracking(True)
            self.matrix_comboBox.setVisible(True)
            self.matrix_comboBox.setFocus()
            self.matrix_comboBox.setFont(QFont("Times New Roman", 11))
            self.matrix_comboBox.setStyleSheet("color: red; font: bold; border-style: outset;")
            self.matrix_comboBox.setDuplicatesEnabled(False)

        # [2.3]: Initialize Name
        if True:
            self.name_info.setEnabled(True)
            self.name_info.setMouseTracking(True)
            self.name_info.setUpdatesEnabled(True)
            self.name_info.setVisible(True)
            self.name_info.setScaledContents(True)
            self.name_info.setFocus()
            self.name_info.setFont(QFont("Times New Roman", 10))
            self.name_info.setStyleSheet("color: orange; font: bold; border-style: outset")

            self.name_lineEdit.setEnabled(True)
            self.name_lineEdit.setMouseTracking(True)
            self.name_lineEdit.setVisible(True)
            self.name_lineEdit.setFocus()
            self.name_lineEdit.setFont(QFont("Times New Roman", 11))
            self.name_lineEdit.setStyleSheet("color: red; font: bold; border-style: outset;")

        # [3]: Making a warning message & submission button
        if True:
            self.warning_message.setEnabled(True)
            self.warning_message.setMouseTracking(True)
            self.warning_message.setUpdatesEnabled(True)
            self.warning_message.setVisible(True)
            self.warning_message.setScaledContents(True)
            self.warning_message.setFocus()
            self.warning_message.setFont(QFont("Times New Roman", 15))
            self.warning_message.setStyleSheet("color: red; font: bold; background-color: black; border-style: outset;")
            self.warning_message.setAlignment(Qt.AlignCenter)

            self.button.setEnabled(True)
            self.button.setMouseTracking(True)
            self.button.setVisible(True)
            self.button.setFocus()
            self.button.setFont(QFont("Times New Roman", 16))
            self.button.setStyleSheet("color: red; font: bold; background-color: black; border-style: outset;")

        return None

    def _submit(self) -> Tuple[Tuple[int, int], str, str]:
        # Attached Function with self.button
        from core import minesweeper

        # [1]: Obtain all the result
        difficulty: str = self.difficulty_comboBox.currentText()
        size: Tuple[int, int] = (int(self.matrix_comboBox.currentText()), int(self.matrix_comboBox.currentText()))
        name: str = self.name_lineEdit.text()
        if name == "":
            name = "Player"
            self.name_lineEdit.setText(name)

        # [2]: Making a game template for data validation
        template_core = minesweeper(size=size, difficulty=difficulty)
        bomb: int = template_core.getBombNumber()
        nodes: int = template_core.getNumberOfNodes()
        ratio: float = round(100 * bomb / nodes, 2)

        # [3]: Making warning function
        text: str = ""
        if ratio >= 15:
            text = "Extreme Mode"
        elif ratio >= 12.5:
            text = "Hard Mode"
        elif ratio <= 5:
            text = "Children Mode"

        self.warning_message.setText(text)
        self.warning_message.update()
        self.warning_message.show()

        print("(Size: {} --- Difficulty: {}) --> Bomb Number(s): {} / {} (Ratio: {} % - Overwhelming: {})"
              .format(size, difficulty, bomb, nodes, round(bomb / nodes * 100, 2), 9 * bomb >= nodes))

        return size, difficulty, name

    def submit(self) -> Optional[Tuple[Tuple[int, int], str, str]]:
        size, difficulty, name = self._submit()
        self.currentSignal.emit(size[0], size[1], difficulty, name)
        return size, difficulty, name
