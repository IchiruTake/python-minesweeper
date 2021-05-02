import numpy as np
from typing import Tuple, Union, List, Optional
from sys import maxsize
from copy import deepcopy
from logging import warning
from preprocess import measure_execution_time


class minesweeper:
    """
    The main core (logic for the game) (matrix = array)
    + self.__size: The shape of the self.__matrix
    + self.__matrix: The main matrix used to defined everything needed. Once assigned, unchanged attribute
    + self.__graph: The array to make __graph flowing if clicking on the position that contains no data in
                    self.__matrix. When defined, this attribute is unchanged. Counting from horizontal all ->
                    move to next row
    + self.__flag_matrix: The matrix used to defined the position that player assign flags for bomb deactivation.
                          The matrix can be changed its value.
    + self.interface_matrix: The matrix that user can see on the screen. Attached to the interface
    """
    def __init__(self, size: Union[int, Tuple[int]], bomb_number: int, verbose: bool = False):
        # [0]: Hyper-parameter Verification
        if True:
            if not isinstance(size, (int, Tuple)):
                raise ValueError(" False Initialization. The size should be an integer or tuple.")
            if not isinstance(bomb_number, int):
                raise ValueError(" False Initialization. The number of bombs should be an integer.")

            if isinstance(size, Tuple):
                if len(size) != 2:
                    raise TypeError("False Initialization: The size should be a tuple with two positive value")
                for i in size:
                    if i <= 0:
                        raise TypeError("False Initialization: The size should be a tuple with two positive value")

            else:
                if size <= 0:
                    raise TypeError("False Initialization: The size should be a tuple with positive integer")
                size: Tuple[int] = (size, size)

            if bomb_number <= 0:
                raise ValueError(" False Initialization. The number of bombs should be larger than zero")
            elif bomb_number >= size[0] * size[1]:
                raise ValueError("The number of bomb is exceeded")

            if not isinstance(verbose, bool):
                raise ValueError(" False Initialization. verbose should be boolean")

            pass
        np.set_printoptions(threshold=maxsize)

        # [1]: Setup Core for data implementation
        self.__matrix: np.ndarray = np.zeros(shape=size, dtype=np.int8)
        self.size = size
        self.__bombNumber: int = bomb_number

        # [2]: Set Configuration
        self.__bomb_notation = -20
        self.__flag_notation = 50

        # [3]: Set Undo & Redo Features
        self.__max_size_for_UndoRedo = 24
        self.__undo_stack: List[np.ndarray] = []
        self.__redo_stack: List[np.ndarray] = []

        # [4]: Set Connection Graph & Attribute
        self.__graph: np.ndarray = np.zeros(shape=(self.__matrix.size, self.__matrix.size), dtype=np.uint8)
        self.__flag_matrix: np.ndarray = np.zeros(shape=self.size, dtype=np.uint8)
        self.interface_matrix: np.ndarray = np.zeros(shape=self.size, dtype=np.uint8)

        # [5]: Set other controller
        self.verbose = verbose

        # [6]: Running Function
        self.build()

    # ----------------------------------------------------------------------------------------------------------------
    # [0]: Core Functions to Task Handling
    def __check_input(self, y: int, x: int) -> bool:
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

    def __assignCoreMatrix(self, y: int, x: int, value: int) -> None:
        self.__matrix[y, x] = value

    def __updateCoreValue(self, y: int, x: int) -> None:
        self.__matrix[y, x] += 1

    def __getCoreValue(self, y: int, x: int) -> Optional[int]:
        return self.__matrix[y, x]

    def __checkIdentical(self, y: int, x: int, value: int) -> Optional[bool]:
        return True if self.__matrix[y, x] == value else False

    def __convert_matrix_index_to_graph_index(self, y: int, x: int) -> Optional[int]:
        return int(y * self.size[0] + x)

    def __convert_graph_index_to_matrix_index(self, graph_index: int) -> Optional[Tuple[int, int]]:
        if not isinstance(graph_index, int):
            raise TypeError("Hyper-parameter only accepts positive integer value only (index={index})")

        if graph_index < 0 or graph_index >= self.size[0] * self.size[1]:
            raise TypeError("Hyper-parameter is overwhelming (index={} != [0, {}))"
                            .format(graph_index, self.size[0] * self.size[1]))

        return int(graph_index // self.size[1]), int(graph_index % self.size[1])

    def __update_graph_edge(self, y: int, x: int, current_graph_index: int) -> None:
        selection_graph_index = self.__convert_matrix_index_to_graph_index(y=y, x=x)
        if 0 <= selection_graph_index < self.__graph.shape[0]:
            self.__graph[current_graph_index, selection_graph_index] += 1

    # ----------------------------------------------------------------------------------------------------------------
    # [1]: Building Information for Matrix before Running the Game
    @measure_execution_time
    def __build_bombs(self):
        """ Implementation to build the matrix by filling with bomb and other """
        print("---------------------------------------------------------------------------------------")
        print("The game core is building the position for the bomb")
        bomb: int = 0
        notation: int = self.__bomb_notation

        while bomb < self.__bombNumber:
            x = int(np.random.randint(0, self.size[0], size=1, dtype=np.uint8)[0])
            y = int(np.random.randint(0, self.size[1], size=1, dtype=np.uint8)[0])

            if self.__checkIdentical(y=y, x=x, value=notation) is True:
                continue
            else:
                self.__assignCoreMatrix(y=y, x=x, value=notation)

            # Check top-left
            if self.__check_input(y=y - 1, x=x - 1) is True:
                if self.__checkIdentical(y=y - 1, x=x - 1, value=notation) is False:
                    self.__updateCoreValue(y=y - 1, x=x - 1)

            # Check top-mid
            if self.__check_input(y=y - 1, x=x) is True:
                if self.__checkIdentical(y=y - 1, x=x, value=notation) is False:
                    self.__updateCoreValue(y=y - 1, x=x)

            # Check top-right
            if self.__check_input(y=y - 1, x=x + 1) is True:
                if self.__checkIdentical(y=y - 1, x=x + 1, value=notation) is False:
                    self.__updateCoreValue(y=y - 1, x=x + 1)

            # Check mid-left
            if self.__check_input(y=y, x=x - 1) is True:
                if self.__checkIdentical(y=y, x=x - 1, value=notation) is False:
                    self.__updateCoreValue(y=y, x=x - 1)

            # Check mid-right
            if self.__check_input(y=y, x=x + 1) is True:
                if self.__checkIdentical(y=y, x=x + 1, value=notation) is False:
                    self.__updateCoreValue(y=y, x=x + 1)

            # Check bottom-left
            if self.__check_input(y=y + 1, x=x - 1) is True:
                if self.__checkIdentical(y=y + 1, x=x - 1, value=notation) is False:
                    self.__updateCoreValue(y=y + 1, x=x - 1)

            # Check bottom-mid
            if self.__check_input(y=y + 1, x=x) is True:
                if self.__checkIdentical(y=y + 1, x=x, value=notation) is False:
                    self.__updateCoreValue(y=y + 1, x=x)

            # Check bottom-right
            if self.__check_input(y=y + 1, x=x + 1) is True:
                if self.__checkIdentical(y=y + 1, x=x + 1, value=notation) is False:
                    self.__updateCoreValue(y=y + 1, x=x + 1)

            bomb += 1  # Update bomb counter

    @measure_execution_time
    def __build_graph(self) -> None:
        """
        Implementation of building graph by activate the edge. In fact, we can assign a new matrix that denote the
        graph index and use linear searching to find the respective index for connection instead. However, we believe
        it will cost O(N) instead of O(1). This function should end-up with general-time complexity of O(N) instead
        of O(N^2)
        """
        print("---------------------------------------------------------------------------------------")
        print("The game core is connecting all of the position by active edge")
        for graph_index in range(0, self.__graph.shape[0]):
            # [1]: Finding the position in which the graph index is pointing using mathematical formulation
            y, x = self.__convert_graph_index_to_matrix_index(graph_index=graph_index)

            # [2]: Update all connected position
            # self.__update_graph_edge(y=y - 1, x=x - 1, current_graph_index=graph_index)  # Check Top-Left

            self.__update_graph_edge(y=y - 1, x=x, current_graph_index=graph_index)  # Check Top-Middle

            # self.__update_graph_edge(y=y - 1, x=x + 1, current_graph_index=graph_index)  # Check Top-Right

            self.__update_graph_edge(y=y, x=x - 1, current_graph_index=graph_index)  # Check Middle-Left

            self.__update_graph_edge(y=y, x=x + 1, current_graph_index=graph_index)  # Check Middle-Right

            # self.__update_graph_edge(y=y + 1, x=x - 1, current_graph_index=graph_index)  # Check Bottom-Left

            self.__update_graph_edge(y=y + 1, x=x, current_graph_index=graph_index)  # Check Bottom-Middle

            # self.__update_graph_edge(y=y + 1, x=x + 1, current_graph_index=graph_index)  # Check Bottom-Right

    def build(self):
        self.__build_bombs()
        self.__build_graph()

    # ----------------------------------------------------------------------------------------------------------------
    # [2.1]: Setter and Getter functions used to perform core-task and UI-task
    def setInterfaceMatrix(self, new_matrix: np.ndarray) -> None:
        if new_matrix.shape != self.getInterfaceMatrix().shape:
            raise ValueError("The new matrix is not fit with the original matrix : Current {} // New {}"
                             .format(new_matrix.shape, self.getInterfaceMatrix().shape))
        self.interface_matrix = new_matrix

    def updateInterfaceMatrix(self, y: int, x: int) -> None:
        if self.__checkIdentical(y=y, x=x, value=0) is False:
            self.getInterfaceMatrix()[y, x] = 1
        elif self.__checkIdentical(y=y, x=x, value=0) is True:
            print("This position has been clicked")
        else:
            warning(" The selected position cannot be found (y={}, x={})".format(y, x))

    def getInterfaceMatrix(self) -> np.ndarray:
        return self.interface_matrix

    def getCoreMatrix(self) -> np.ndarray:
        return self.__matrix

    def getGraphMatrix(self) -> np.ndarray:
        return self.__graph

    def getGraphFromCore(self):
        pass

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

    def searchingDataFlowing(self):
        pass

    def click(self, y: int, x: int):
        pass

    def check_if_clickable(self, y: int, x: int):
        if self.__check_input(y=y, x=x) is True and self.interface_matrix[y, x] == 0:
            return True
        return False

    def check_if_bomb(self, y: int, x: int):
        if self.__check_input(y=y, x=x) is True and self.get_matrix()[y, x] == self.__bomb_notation:
            return True
        return False

    # [ ] --------------------------------------------------------
    def display_original(self):
        print(self.getCoreMatrix())
        print()

    def display_interface_matrix(self):
        print(self.getInterfaceMatrix())
        print()

    def display_graph_matrix(self):
        print(self.getGraphMatrix())
        print()

    # [ ] --------------------------------------------------------

game = minesweeper(size=15, bomb_number=20)
game.display_original()
game.display_interface_matrix()
game.display_graph_matrix()
