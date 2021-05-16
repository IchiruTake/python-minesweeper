import numpy as np
from typing import Tuple, Union, List, Optional
from sys import maxsize
from copy import deepcopy
from logging import warning
from preprocessing import measure_execution_time
from config import NOTATION


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
                size: Tuple[int, int] = (NOTATION["Default Size"], NOTATION["Default Size"])
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

            pass

        # [1]: Setup Core for data implementation
        self.__coreMatrix: np.ndarray = np.zeros(shape=size, dtype=np.int8)
        self.size: Tuple[int, int] = size
        self.__bombPosition: List[Tuple[int, int]] = []
        self.__bombNumber: int = int(NOTATION["Bomb Coefficient"] * self.__coreMatrix.size ** (NOTATION["Bomb Ratio"]))

        # [2]: Set Configuration
        self.BombNotation = NOTATION["Bomb Notation"]
        self.FlagNotation = NOTATION["Flag Notation"] if NOTATION["Flag Notation"] not in [0, 1] else -1
        self.interface_matrix: np.ndarray = np.zeros(shape=self.size, dtype=np.int8)

        # [3]: Set Undo & Redo Features
        self.__max_size_for_UndoRedo = 24
        self.__undo_stack: List[np.ndarray] = []
        self.__redo_stack: List[np.ndarray] = []

        # [4]: Set other controller
        self.verbose = verbose

        # [5]: Gaming Status
        self.is_wining: Optional[bool] = None

        # [6]: Running Function
        self._build()

    # ----------------------------------------------------------------------------------------------------------------
    # [0]: Core Functions to Task Handling
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

    def _assignCoreMatrix(self, y: int, x: int, value: int) -> None:
        self.__coreMatrix[y, x] = value

    def _updateCoreValue(self, y: int, x: int) -> None:
        self.__coreMatrix[y, x] += 1

    def _getCoreValue(self, y: int, x: int) -> Optional[int]:
        return self.__coreMatrix[y, x]

    def _checkEqual(self, y: int, x: int, value: int) -> bool:
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

    def _updateInterfaceMatrix(self, graph_index: int) -> None:
        y, x = self._convert_GraphIndex_to_MatrixIndex(graph_index=graph_index)
        self.getInterfaceMatrix()[y, x] = 1

    def _updateBombPositions(self, y: int, x: int) -> None:
        self.__bombPosition.append((y, x))

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

            if self._checkEqual(y=y, x=x, value=notation) is True:
                continue
            else:
                self._assignCoreMatrix(y=y, x=x, value=notation)

            # Check top-left
            if self._checkInput(y=y - 1, x=x - 1) is True:
                if self._checkEqual(y=y - 1, x=x - 1, value=notation) is False:
                    self._updateCoreValue(y=y - 1, x=x - 1)

            # Check top-mid
            if self._checkInput(y=y - 1, x=x) is True:
                if self._checkEqual(y=y - 1, x=x, value=notation) is False:
                    self._updateCoreValue(y=y - 1, x=x)

            # Check top-right
            if self._checkInput(y=y - 1, x=x + 1) is True:
                if self._checkEqual(y=y - 1, x=x + 1, value=notation) is False:
                    self._updateCoreValue(y=y - 1, x=x + 1)

            # Check mid-left
            if self._checkInput(y=y, x=x - 1) is True:
                if self._checkEqual(y=y, x=x - 1, value=notation) is False:
                    self._updateCoreValue(y=y, x=x - 1)

            # Check mid-right
            if self._checkInput(y=y, x=x + 1) is True:
                if self._checkEqual(y=y, x=x + 1, value=notation) is False:
                    self._updateCoreValue(y=y, x=x + 1)

            # Check bottom-left
            if self._checkInput(y=y + 1, x=x - 1) is True:
                if self._checkEqual(y=y + 1, x=x - 1, value=notation) is False:
                    self._updateCoreValue(y=y + 1, x=x - 1)

            # Check bottom-mid
            if self._checkInput(y=y + 1, x=x) is True:
                if self._checkEqual(y=y + 1, x=x, value=notation) is False:
                    self._updateCoreValue(y=y + 1, x=x)

            # Check bottom-right
            if self._checkInput(y=y + 1, x=x + 1) is True:
                if self._checkEqual(y=y + 1, x=x + 1, value=notation) is False:
                    self._updateCoreValue(y=y + 1, x=x + 1)

            bomb += 1  # Update bomb counter
        pass

    def _build(self):
        self._buildBombPositions()

    # ----------------------------------------------------------------------------------------------------------------
    # [2.1]: Setter and Getter functions used to perform core-task and UI-task
    def setInterfaceMatrix(self, new_matrix: np.ndarray) -> None:
        if new_matrix.shape != self.getInterfaceMatrix().shape:
            raise ValueError("The new matrix is not fit with the original matrix : Current {} // New {}"
                             .format(new_matrix.shape, self.getInterfaceMatrix().shape))
        self.interface_matrix = new_matrix

    def updateInterfaceMatrix(self, y: int, x: int) -> None:
        if self._checkEqual(y=y, x=x, value=0) is False:
            self.getInterfaceMatrix()[y, x] = 1
        elif self._checkEqual(y=y, x=x, value=0) is True:
            print("This position has been clicked")
        else:
            warning(" The selected position cannot be found (y={}, x={})".format(y, x))

    # [2.2]: Functions used to perform core-task and UI-task: Stack for Undo-Redo
    def click_undo(self) -> None:
        if not self.__undo_stack:
            warning(" No state is saved")
        else:
            new_matrix = self.__undo_stack.pop()
            self.setInterfaceMatrix(new_matrix=new_matrix)
            self.__redo_stack.append(new_matrix)

    def click_redo(self) -> None:
        if not self.__redo_stack:
            warning(" No state is saved")
        else:
            new_matrix = self.__redo_stack.pop()
            self.setInterfaceMatrix(new_matrix=new_matrix)
            self.__undo_stack.append(new_matrix)

    def reset_undoStack(self) -> None:
        del self.__undo_stack
        self.__undo_stack = []

    def reset_redoStack(self) -> None:
        del self.__redo_stack
        self.__redo_stack = []

    def reset_all(self):
        self.reset_undoStack()
        self.reset_redoStack()

    # ----------------------------------------------------------------------------------------------------------------
    # [3]: User Interface Function
    def update_state(self) -> None:
        if len(self.__undo_stack) > self.__max_size_for_UndoRedo:
            warning("The core: Undo Stack has held too many object. Automatically delete some entity")
            self.__undo_stack.pop(0)
        self.__undo_stack.append(deepcopy(self.getInterfaceMatrix()))

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
            if self._checkEqual(y=y, x=x, value=0) is True:
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
        if self._checkEqual(y=y_start, x=x_start, value=0) is True:
            visiting_stack: List[bool] = [False] * int(self.getNumberOfNodes())
            index_start = self._convert_MatrixIndex_to_GraphIndex(y=y_start, x=x_start)
            self._recursiveDepthFirstFlow(index=index_start, recorded_stack=visiting_stack)

            for graph_index, value in enumerate(visiting_stack):
                if value is True:
                    self._updateInterfaceMatrix(graph_index=graph_index)

        pass

    def click(self, y: int, x: int, message: Optional[str]):
        # Chưa hoàn thiện TODO
        if self.check_if_clickable(y=y, x=x):
            is_bomb = self.check_if_bomb(y=y, x=x)
            if is_bomb is True:
                self.is_wining = False

            else:
                pass
                self._graphFlowing(y_start=y, x_start=x)

    def check_if_clickable(self, y: int, x: int):
        if self._checkInput(y=y, x=x) is True and self.getInterfaceMatrix()[y, x] == 0:
            return True
        return False

    def check_if_bomb(self, y: int, x: int):
        if self._checkInput(y=y, x=x) is True and self._checkEqual(y=y, x=x, value=self.BombNotation) is True:
            return True
        return False

    def check_if_wining(self) -> bool:
        bomb_position: List[Tuple[int, int]] = self.getBombPosition(descending=False)
        for position in range(len(bomb_position) - 1, -1, -1):
            y, x = bomb_position[position]
            if self._checkEqual(y=y, x=x, value=self.BombNotation) is True:
                bomb_position.pop()
            else:
                return False
        return True

    def _openingSubmission(self) -> bool:
        return bool(np.count_nonzero(self.interface_matrix, axis=None) != self.getNumberOfNodes())

    def _submit(self):
        # TODO
        self.is_wining = self.check_if_wining()
        return self.is_wining

    # [x] Get Matrix and Display Matrix --------------------------------------------------------
    def getNumberOfNodes(self) -> int:
        return self.size[0] * self.size[1]

    def getInterfaceMatrix(self) -> np.ndarray:
        return self.interface_matrix

    def getCoreMatrix(self) -> np.ndarray:
        return self.__coreMatrix

    def getBombNumber(self) -> int:
        return self.__bombNumber

    def getBombPosition(self, descending: bool = False) -> List[Tuple[int, int]]:
        return self.__bombPosition.copy() if descending is False else list(reversed(self.__bombPosition)).copy()

    def getFlagsPosition(self) -> List[List[int]]:
        return np.argwhere(self.getInterfaceMatrix() == self.FlagNotation).tolist()

    def displayCoreMatrix(self):
        print("=" * 100)
        print("Hashing Core Matrix: ")
        print(self.getCoreMatrix())
        print("Matrix Size: {} --> Association Node: {} <---> Bomb Number: {}"
              .format(self.size, self.getNumberOfNodes(), self.getBombNumber()))
        print("=" * 100, "\n")

    def displayBetterCoreMatrix(self):
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

    def displayInterfaceMatrix(self):
        print("=" * 100)
        print("Hashing Interface Matrix: ")
        matrix = self.getInterfaceMatrix()
        for row in range(0, matrix.shape[0]):
            print(matrix[row].tolist())
        print("=" * 100, "\n")

    def displayBetterInterfaceMatrix(self):
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

game.click(y=5, x=5, message=None)
game.displayBetterInterfaceMatrix()

