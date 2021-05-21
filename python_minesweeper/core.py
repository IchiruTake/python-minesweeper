import numpy as np
from typing import Tuple, Union, List, Optional
from sys import maxsize
from copy import deepcopy
from logging import warning
from preprocessing import measure_execution_time
from config import CORE_CONFIGURATION as CONFIG, MOUSE_MESSAGE
import gc


class minesweeper:
    """
    The main core (logic for the game) (matrix = array)
    + self.size: The shape of the self.__coreMatrix
    + self.__coreMatrix: The main matrix used to defined everything needed. Once assigned, unchanged attribute
    + self.interface_matrix: The matrix that user can see on the screen. Attached to the interface
    """
    def __init__(self, size: Union[int, Tuple[int]], verbose: bool = False):
        # [0]: Hyper-parameter Verification
        np.set_printoptions(threshold=maxsize)
        if True:
            if size is None:
                size: Tuple[int, int] = (CONFIG["Default Size"], CONFIG["Default Size"])
            elif not isinstance(size, (int, Tuple)):
                raise ValueError(" False Initialization. The size should be an integer or tuple.")

            if isinstance(size, Tuple):
                if len(size) != 2:
                    raise TypeError("False Initialization: The size should be a tuple with two positive value")
                for i in size:
                    if i <= 0:
                        raise TypeError("False Initialization: The size should be a tuple with two positive value")

            else:
                if size <= 0:
                    raise TypeError("False Initialization: The size should be a tuple with positive integer")
                size: Tuple[int, int] = (size, size)

            if not isinstance(verbose, bool):
                raise ValueError(" False Initialization. verbose should be boolean")

            if CONFIG["Flag Notation"] == CONFIG["Question Notation"]:
                raise ValueError("Flag Notation ({}) is not equal with Question Notation ({})."
                                 .format(CONFIG["Flag Notation"], CONFIG["Question Notation"]))

            if not isinstance(CONFIG["Maximum Stack"], int):
                raise ValueError("Maximum Stack ({}) should be non-negative integer".format(CONFIG["Maximum Stack"]))

            if CONFIG["Maximum Stack"] <= 0:
                raise ValueError("Maximum Stack ({}) should be non-negative integer".format(CONFIG["Maximum Stack"]))

            if CONFIG["Bomb Notation"] in range(0, 9):
                CONFIG["Bomb Notation"]: int = -20

            if CONFIG["Flag Notation"] in (0, 1):
                CONFIG["Flag Notation"]: int = -1

            if CONFIG["Question Notation"] in (0, 1):
                CONFIG["Question Notation"]: int = -5

            pass

        # [1]: Setup Core for Data Implementation
        self.__coreMatrix: np.ndarray = np.zeros(shape=size, dtype=np.int8)
        self.size: Tuple[int, int] = size
        self.__bombPosition: List[Tuple[int, int]] = []
        self.__bombNumber: int = int(CONFIG["Bomb Coefficient"] * self.__coreMatrix.size **
                                     CONFIG["Bomb Power"])

        # [2]: Set Configuration
        self.interface_matrix: np.ndarray = np.zeros(shape=self.size, dtype=np.int8)
        self.BombNotation: int = CONFIG["Bomb Notation"]
        self.FlagNotation: int = CONFIG["Flag Notation"]
        self.QuestionNotation: int = CONFIG["Question Notation"]

        # [3]: Set Undo & Redo Features
        self._maxStackSizeForUndoRedo = CONFIG["Maximum Stack"]
        self.__undo_stack: List[np.ndarray] = []
        self.__redo_stack: List[np.ndarray] = []

        # [4]: Gaming Status
        self.verbose: bool = verbose
        self.is_wining: bool = False
        self.is_playing: bool = True

        # [6]: Running Function
        self._build()

    # ----------------------------------------------------------------------------------------------------------------
    # [0]: Core Functions for Task Handling
    # [0.1]: For Core Matrix
    def _checkInput(self, y: int, x: int) -> bool:
        # True: Input can be used
        # False: In-valid input
        if not isinstance(y, int) or not isinstance(x, int):
            if self.verbose is True:
                warning(" Hyper-parameter only accepts integer value only (y={}, x={})".format(y, x))
            return False
        elif y < 0 or y >= self.size[0] or x < 0 or x >= self.size[1]:
            if self.verbose is True:
                if not 0 <= y < self.size[0]:
                    warning(" The selected position cannot be found (y={} != [0, {})".format(y, self.size[0]))
                if not 0 <= x < self.size[1]:
                    warning(" The selected position cannot be found (x={} != [0, {})".format(x, self.size[1]))
            return False

        return True

    def _assignCoreNodeByValue(self, y: int, x: int, value: int) -> None:
        self.__coreMatrix[y, x] = value

    def _updateCoreValue(self, y: int, x: int) -> None:
        self.__coreMatrix[y, x] += 1

    def _checkCoreNode(self, y: int, x: int, value: int) -> bool:
        # Return Whether the value in the core matrix is equal
        return True if self.__coreMatrix[y, x] == value else False

    def _convert_MatrixIndex_to_GraphIndex(self, y: int, x: int) -> Optional[int]:
        if not isinstance(y, int):
            raise TypeError("Hyper-parameter only accepts positive integer value only (y={y})")
        elif not 0 <= y < self.size[0]:
            raise TypeError("Hyper-parameter is overwhelming (y={} != [0, {}))".format(y, self.size[0]))

        if not isinstance(x, int):
            raise TypeError("Hyper-parameter only accepts positive integer value only (x={x})")
        elif not 0 <= x < self.size[1]:
            raise TypeError("Hyper-parameter is overwhelming (x={} != [0, {}))".format(x, self.size[1]))

        return int(y * self.size[0] + x)

    def _convert_GraphIndex_to_MatrixIndex(self, graph_index: int) -> Optional[Tuple[int, int]]:
        if not isinstance(graph_index, int):
            raise TypeError("Hyper-parameter only accepts positive integer value only (index={index})")

        if not (0 <= graph_index < self.getNumberOfNodes()):
            raise TypeError("Hyper-parameter is overwhelming (index={} != [0, {}))"
                            .format(graph_index, self.getNumberOfNodes()))

        return int(graph_index // self.size[1]), int(graph_index % self.size[1])

    def _updateBombPosition(self, y: int, x: int) -> None:
        self.__bombPosition.append((y, x))

    # ----------------------------------------------------------------------------------------------------------------
    # [0.2]: For Interface Matrix
    def _openNodeAtInterfaceMatrixByGraph(self, graph_index: int) -> bool:
        y, x = self._convert_GraphIndex_to_MatrixIndex(graph_index=graph_index)
        return self._openNodeAtInterfaceMatrixByMatrix(y=y, x=x)

    def _openNodeAtInterfaceMatrixByMatrix(self, y: int, x: int) -> bool:
        if self._checkInput(y=y, x=x) is True:
            self._setInterfaceNode(y=y, x=x, value=1)
            return True
        else:
            warning("No update has been found")
            return False

    def _setInterfaceNode(self, y: int, x: int, value: int) -> None:
        self.getInterfaceMatrix()[y, x] = value

    def _checkInterfaceNode(self, y: int, x: int, value: int) -> bool:
        return True if self.getInterfaceNode(y=y, x=x) == value else False

    def _checkInterfaceValidity(self) -> bool:
        max_valid_nodes: int = 0
        for value in (0, 1, self.FlagNotation, self.QuestionNotation):
            max_valid_nodes += np.argwhere(self.getInterfaceMatrix() not in value).shape[0]
        return True if max_valid_nodes == self.getNumberOfNodes() else False

    # ----------------------------------------------------------------------------------------------------------------
    # [1]: Building Information for Matrix before Running the Game
    @measure_execution_time
    def _buildBombPositions(self) -> None:
        """ Implementation to build the matrix by filling with bomb and other """
        print("---------------------------------------------------------------------------------------")
        print("The game core is building the position for the bomb")
        bomb: int = 0
        notation: int = self.BombNotation

        while bomb < self.__bombNumber:
            x = int(np.random.randint(0, self.size[0], size=1, dtype=np.uint8)[0])
            y = int(np.random.randint(0, self.size[1], size=1, dtype=np.uint8)[0])

            if self._checkCoreNode(y=y, x=x, value=notation) is True:
                continue
            else:
                self._assignCoreNodeByValue(y=y, x=x, value=notation)
                self._updateBombPosition(y=y, x=x)
            # Check top-left
            if self._checkInput(y=y - 1, x=x - 1) is True:
                if self._checkCoreNode(y=y - 1, x=x - 1, value=notation) is False:
                    self._updateCoreValue(y=y - 1, x=x - 1)

            # Check top-mid
            if self._checkInput(y=y - 1, x=x) is True:
                if self._checkCoreNode(y=y - 1, x=x, value=notation) is False:
                    self._updateCoreValue(y=y - 1, x=x)

            # Check top-right
            if self._checkInput(y=y - 1, x=x + 1) is True:
                if self._checkCoreNode(y=y - 1, x=x + 1, value=notation) is False:
                    self._updateCoreValue(y=y - 1, x=x + 1)

            # Check mid-left
            if self._checkInput(y=y, x=x - 1) is True:
                if self._checkCoreNode(y=y, x=x - 1, value=notation) is False:
                    self._updateCoreValue(y=y, x=x - 1)

            # Check mid-right
            if self._checkInput(y=y, x=x + 1) is True:
                if self._checkCoreNode(y=y, x=x + 1, value=notation) is False:
                    self._updateCoreValue(y=y, x=x + 1)

            # Check bottom-left
            if self._checkInput(y=y + 1, x=x - 1) is True:
                if self._checkCoreNode(y=y + 1, x=x - 1, value=notation) is False:
                    self._updateCoreValue(y=y + 1, x=x - 1)

            # Check bottom-mid
            if self._checkInput(y=y + 1, x=x) is True:
                if self._checkCoreNode(y=y + 1, x=x, value=notation) is False:
                    self._updateCoreValue(y=y + 1, x=x)

            # Check bottom-right
            if self._checkInput(y=y + 1, x=x + 1) is True:
                if self._checkCoreNode(y=y + 1, x=x + 1, value=notation) is False:
                    self._updateCoreValue(y=y + 1, x=x + 1)

            bomb += 1  # Update bomb counter
        pass

    def _build(self):
        self._buildBombPositions()

    # ----------------------------------------------------------------------------------------------------------------
    # [2]: Undo - Redo Function: Functions used to perform core-task and UI-task: Stack for Undo-Redo
    def _setInterfaceMatrix(self, new_matrix: np.ndarray) -> None:
        del self.interface_matrix
        self.interface_matrix = new_matrix

    def _reset_undoStack(self) -> None:
        del self.__undo_stack
        self.__undo_stack = []

    def _reset_redoStack(self) -> None:
        del self.__redo_stack
        self.__redo_stack = []

    def click_undoStack(self) -> None:
        if not self.__undo_stack:
            warning(" No state is saved")
        else:
            new_matrix = self.__undo_stack.pop()
            self._setInterfaceMatrix(new_matrix=new_matrix)
            self.__redo_stack.append(new_matrix)

    def click_redoStack(self) -> None:
        if not self.__redo_stack:
            warning(" No state is saved")
        else:
            new_matrix = self.__redo_stack.pop()
            self._setInterfaceMatrix(new_matrix=new_matrix)
            self.__undo_stack.append(new_matrix)

    def resetStack(self):
        self._reset_undoStack()
        self._reset_redoStack()
        gc.collect()

    def _updateGamingState(self) -> None:
        if len(self.__undo_stack) > self._maxStackSizeForUndoRedo:
            warning("The core: Undo Stack has held too many object. Automatically delete some entity")
            self.__undo_stack.pop(0)
        self.__undo_stack.append(self.getInterfaceMatrix().copy())

    # ----------------------------------------------------------------------------------------------------------------
    # [3]: User Interface Function
    def _recursiveDepthFirstFlow(self, index: int, recorded_stack: List[int]):
        # Time Complexity: O(1.5N) - Auxiliary Space: O(N)
        # Condition to check if that value has been pass yet, else discarded
        if recorded_stack[index] is False:
            # [1]: Add into the matrix
            recorded_stack[index] = True

            # [2]: Convert to Matrix Index for Calculation
            y, x = self._convert_GraphIndex_to_MatrixIndex(graph_index=index)

            # Condition to check whether the core matrix that zero.
            # If self.__core[y, x] = 0: No object found, continue to flow; else, don't flow it
            if self._checkCoreNode(y=y, x=x, value=0) is True:
                # [3]: Flow the graph into four direction: Bottom, Top, Left, Right
                # [3.1]: Flow to Bottom
                if y + 1 < self.size[0]:
                    self._recursiveDepthFirstFlow(index=self._convert_MatrixIndex_to_GraphIndex(y=y + 1, x=x),
                                                  recorded_stack=recorded_stack)
                # [3.2]: Flow to Top
                if y - 1 >= 0:
                    self._recursiveDepthFirstFlow(index=self._convert_MatrixIndex_to_GraphIndex(y=y - 1, x=x),
                                                  recorded_stack=recorded_stack)
                # [3.2]: Flow to Left
                if x - 1 >= 0:
                    self._recursiveDepthFirstFlow(index=self._convert_MatrixIndex_to_GraphIndex(y=y, x=x - 1),
                                                  recorded_stack=recorded_stack)
                # [3.3]: Flow to Right
                if x + 1 < self.size[1]:
                    self._recursiveDepthFirstFlow(index=self._convert_MatrixIndex_to_GraphIndex(y=y, x=x + 1),
                                                  recorded_stack=recorded_stack)

        pass

    def _graphFlowing(self, y_start: int, x_start: int) -> None:
        if self._checkCoreNode(y=y_start, x=x_start, value=0) is True:
            visiting_stack: List[bool] = [False] * int(self.getNumberOfNodes())
            index_start = self._convert_MatrixIndex_to_GraphIndex(y=y_start, x=x_start)
            self._recursiveDepthFirstFlow(index=index_start, recorded_stack=visiting_stack)

            for graph_index, state in enumerate(visiting_stack):
                if state is True:
                    self._openNodeAtInterfaceMatrixByGraph(graph_index=graph_index)

        pass

    def click(self, y: int, x: int, message: str) -> bool:
        """
        Main function used when clicking image the nodes. Return boolean if it is update

        :param y: The position in y-axis dimension
        :type y: int

        :param x: The position in x-axis dimension
        :type x: int

        :param message: The signal received from interface
        :type message: str

        :return: bool
        """
        if message not in MOUSE_MESSAGE.keys():
            raise ValueError("Re-check the source code for data validation. "
                             "Clicked mouse has emit unknown message ({})".format(message))

        updating_status: bool = False
        if self.is_playing is True:
            if self.getInterfaceNode(y=y, x=x) != 1:
                self._updateGamingState()
                updating_status = True

            if MOUSE_MESSAGE[message] == "L":
                if self.getInterfaceNode(y=y, x=x) == 0:
                    self._openNodeAtInterfaceMatrixByMatrix(y=y, x=x)

                if self._checkBomb(y=y, x=x) is True:
                    self.is_playing = False

            elif MOUSE_MESSAGE[message] == "R":
                if self.getInterfaceNode(y=y, x=x) == 0:
                    self._setInterfaceNode(y=y, x=x, value=self.FlagNotation)
                elif self.getInterfaceNode(y=y, x=x) == self.FlagNotation:
                    self._setInterfaceNode(y=y, x=x, value=self.QuestionNotation)
                elif self.getInterfaceNode(y=y, x=x) == self.QuestionNotation:
                    self._setInterfaceNode(y=y, x=x, value=0)

            return updating_status
        return updating_status

    # ----------------------------------------------------------------------------------------------------------------
    # [3]: User Interface Function
    def _checkClickable(self, y: int, x: int) -> bool:
        if self._checkInput(y=y, x=x) is True and self.getInterfaceNode(y=y, x=x) != 1:
            return True
        return False

    def _checkBomb(self, y: int, x: int) -> bool:
        if self._checkInput(y=y, x=x) is True and self._checkCoreNode(y=y, x=x, value=self.BombNotation) is True:
            return True
        return False

    def _checkWining(self) -> bool:
        # TODO
        bomb_position: List[Tuple[int, int]] = self.getBombPositions(descending=False)
        for position in range(len(bomb_position) - 1, -1, -1):
            y, x = bomb_position[position]
            if self._checkInterfaceNode(y=y, x=x, value=self.FlagNotation):
                bomb_position.pop()
            else:
                return False
        return True

    def openSubmission(self) -> bool:
        if self.getQuestionPositions().shape[0] == 0:
            return bool(np.count_nonzero(self.interface_matrix, axis=None) == self.getNumberOfNodes())
        return False

    # [x]: Getter and Display Function --------------------------------------------------------
    # [x.1] Getter Function
    def getCoreMatrix(self) -> np.ndarray:
        return self.__coreMatrix

    def getCoreNode(self, y: int, x: int) -> np.integer:
        return self.getCoreMatrix()[y, x]

    def getInterfaceMatrix(self) -> np.ndarray:
        return self.interface_matrix

    def getInterfaceNode(self, y: int, x: int):
        return self.getInterfaceMatrix()[y, x]

    def getNumberOfNodes(self) -> int:
        return self.size[0] * self.size[1]

    def getBombNumber(self) -> int:
        return self.__bombNumber

    def getBombPositions(self, descending: bool = False) -> List[Tuple[int, int]]:
        return self.__bombPosition.copy() if descending is False else list(reversed(self.__bombPosition)).copy()

    def getFlagPositions(self) -> np.ndarray:
        return np.argwhere(self.getInterfaceMatrix() == self.FlagNotation)

    def getQuestionPositions(self) -> np.ndarray:
        return np.argwhere(self.getInterfaceMatrix() == self.QuestionNotation)

    def checkIfWinning(self) -> bool:
        self.is_wining = self._checkWining()
        return self.is_wining

    def checkIfPlaying(self) -> bool:
        return self.is_playing

    # [x.2] Display Function
    def displayCoreMatrix(self) -> None:
        print("=" * 100)
        print("Hashing Core Matrix: ")
        print(self.getCoreMatrix())
        print("Matrix Size: {} --> Association Node: {} <---> Bomb Number: {}"
              .format(self.size, self.getNumberOfNodes(), self.getBombNumber()))
        print("=" * 100, "\n")

    def displayBetterCoreMatrix(self) -> None:
        print("=" * 100)
        print("Better Core Matrix: ")
        matrix: np.ndarray = np.array(self.getCoreMatrix().copy(), dtype=np.object_)
        matrix[matrix == self.BombNotation] = "*"
        matrix[matrix == 0] = "_"
        for value in range(1, 9):
            matrix[matrix == value] = str(value)

        for row in range(0, matrix.shape[0]):
            print(matrix[row].tolist())
        print("\nMatrix Size: {} --> Association Node: {} <---> Bomb Number: {}"
              .format(self.size, self.getNumberOfNodes(), self.getBombNumber()))
        print("=" * 100, "\n")

    def displayInterfaceMatrix(self) -> None:
        print("=" * 100)
        print("Hashing Interface Matrix: ")
        matrix = self.getInterfaceMatrix()
        for row in range(0, matrix.shape[0]):
            print(matrix[row].tolist())
        print("=" * 100, "\n")

    def displayBetterInterfaceMatrix(self) -> None:
        print("=" * 100)
        print("Better Interface Matrix: ")
        matrix: np.ndarray = np.array(self.getInterfaceMatrix().copy(), dtype=np.object_)
        matrix[matrix == 1] = "A"
        matrix[matrix == 0] = "_"
        matrix[matrix == self.FlagNotation] = "F"
        for row in range(0, matrix.shape[0]):
            print(matrix[row].tolist())
        print("=" * 100, "\n")
    # [ ] --------------------------------------------------------


game = minesweeper(size=15)
game.displayBetterCoreMatrix()
game.displayBetterInterfaceMatrix()

game.click(y=5, x=5, message="None")
game.displayBetterInterfaceMatrix()
