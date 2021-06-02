import numpy as np
from typing import Tuple, Union, List, Optional, Dict
from sys import maxsize
from logging import warning
from config import CORE_CONFIGURATION as CONFIG, MOUSE_MESSAGE, DIFFICULTY, difficulty_validation
import gc


class minesweeper:
    """
    The main core (logic for the game) (matrix = array)
    + self.size: The shape of the self.__coreMatrix
    + self.__coreMatrix: The main matrix used to defined everything needed. Once assigned, unchanged attribute
    + self.interface_matrix: The matrix that user can see on the screen. Attached to the interface
    """
    def __init__(self, size: Union[int, Tuple[int, int]] = 16, difficulty: str = "Medium", verbose: bool = False,
                 support_big_data: bool = False):
        # [0]: Hyper-parameter Verification
        np.set_printoptions(threshold=maxsize)
        if True:
            if size is None:
                size: Tuple[int, int] = (CONFIG["Default Size"], CONFIG["Default Size"])
            elif not isinstance(size, (int, Tuple)):
                raise ValueError(" False Initialization. The size should be an integer or tuple.")

            if isinstance(size, Tuple):
                if len(size) != 2:
                    raise TypeError("False Initialization: The size should be a tuple with two positive values")
                for i in size:
                    if i <= 0:
                        raise TypeError("False Initialization: The size should be a tuple with two positive values")

            else:
                if size <= 0:
                    raise TypeError("False Initialization: The size should be a tuple with positive integers")
                size: Tuple[int, int] = (size, size)

            if not isinstance(verbose, bool):
                raise ValueError(" False Initialization. verbose should be boolean")

            if not isinstance(CONFIG["Maximum Stack"], int):
                raise ValueError("Maximum Stack ({}) should be non-negative integer".format(CONFIG["Maximum Stack"]))

            if CONFIG["Maximum Stack"] <= 0:
                raise ValueError("Maximum Stack ({}) should be non-negative integer".format(CONFIG["Maximum Stack"]))

            if CONFIG["Bomb Notation"] in range(0, 9):
                raise ValueError("CONFIG[Bomb Notation] should not in the range of [0, 8]")

            if CONFIG["Flag Notation"] in (0, 1):
                raise ValueError("CONFIG[Flag Notation] should not in the range of [0, 1]")

            if CONFIG["Question Notation"] in (0, 1):
                raise ValueError("CONFIG[Question Notation] should not in the range of [0, 1]")

            if CONFIG["Flag Notation"] == CONFIG["Question Notation"]:
                raise ValueError("Flag Notation ({}) is not equal with Question Notation ({})."
                                 .format(CONFIG["Flag Notation"], CONFIG["Question Notation"]))

            difficulty_validation(key=difficulty)
            pass

        # [1]: Setup Core for Data Implementation
        self.__coreMatrix: np.ndarray = np.zeros(shape=size, dtype=np.int8)
        self.size: Tuple[int, int] = size
        self.__bombPosition: List[Tuple[int, int]] = []
        self._bombNumber: int = int(DIFFICULTY[difficulty][0] * (self.size[0] / 2 + self.size[1] / 2) **
                                    DIFFICULTY[difficulty][1])
        self._remainingFlags: int = self._bombNumber
        self._accomplishedNode: int = 0

        # [2]: Set Configuration
        self.interface_matrix: np.ndarray = np.zeros(shape=self.size, dtype=np.int8)
        self.adjacencyMatrixFour: np.ndarray = \
            np.zeros(shape=(self.size[0] * self.size[1], self.size[0] * self.size[1]), dtype=np.uint8)
        self.adjacencyMatrixEight: np.ndarray = \
            np.zeros(shape=(self.size[0] * self.size[1], self.size[0] * self.size[1]), dtype=np.uint8)
        self.adjacencyMatrixStatus: bool = False

        self.BombNotation: int = CONFIG["Bomb Notation"]
        self.FlagNotation: int = CONFIG["Flag Notation"]
        self.QuestionNotation: int = CONFIG["Question Notation"]
        self.difficulty: str = difficulty

        # [3]: Set Undo & Redo Features
        self._maxStackSizeForUndoRedo = CONFIG["Maximum Stack"]
        self.__undoStack: List[np.ndarray] = []
        self.__redoStack: List[np.ndarray] = []

        # [4]: Gaming Status
        self.verbose: bool = verbose
        self.VictoryStatus: bool = False
        self.PlayingStatus: bool = True

        # [5]: Randomized Function & Extra Attribute
        self.randomMaxSize: int = int(3e6) if support_big_data is False else int(1e5)
        self.randomCounter: int = 0
        self._random_positions: np.ndarray = self.resetRandom()

        self._location: Dict[int, Tuple[int, int]] = {i: self._convertGraphToMatrixWithMath(i)
                                                      for i in range(0, self.getNumberOfNodes())}
        self._reversedLocation: Dict[Tuple[int, int], int] = {value: key for key, value in self.getLocation().items()}

        # [6]: Running Function
        self.build()
        self.buildAdjacencyMatrix()
        self.displayInformation()

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

    def _setCoreValue(self, y: int, x: int, value: int) -> None:
        self.__coreMatrix[y, x] = value

    def _updateCoreValue(self, y: int, x: int) -> None:
        self.__coreMatrix[y, x] = self.__coreMatrix[y, x] + 1

    def _checkCoreNode(self, y: int, x: int, value: int) -> bool:
        # Return Whether the value in the core matrix is equal
        return True if self.__coreMatrix[y, x] == value else False

    def _convertMatrixToGraphWithMath(self, y: int, x: int) -> int:
        if not isinstance(y, (int, np.integer)):
            raise TypeError("Hyper-parameter only accepts positive integer value only (y={y})")
        elif not 0 <= y < self.size[0]:
            raise TypeError("Hyper-parameter is overwhelming (y={} != [0, {}))".format(y, self.size[0]))

        if not isinstance(x, (int, np.integer)):
            raise TypeError("Hyper-parameter only accepts positive integer value only (x={x})")
        elif not 0 <= x < self.size[1]:
            raise TypeError("Hyper-parameter is overwhelming (x={} != [0, {}))".format(x, self.size[1]))

        return int(y * self.size[0] + x)

    def _convertGraphToMatrixWithMath(self, graph_index: int) -> Tuple[int, int]:
        if not isinstance(graph_index, (int, np.integer)):
            raise TypeError("Hyper-parameter only accepts positive integer value only (index={index})")

        if not (0 <= graph_index < self.getNumberOfNodes()):
            raise TypeError("Hyper-parameter is overwhelming (index={} != [0, {}))"
                            .format(graph_index, self.getNumberOfNodes()))

        return int(graph_index // self.size[1]), int(graph_index % self.size[1])

    def _convertMatrixToGraphWithCache(self, y: int, x: int) -> int:
        if not isinstance(y, (int, np.integer)):
            raise TypeError("Hyper-parameter only accepts positive integer value only (y={y})")
        elif not 0 <= y < self.size[0]:
            raise TypeError("Hyper-parameter is overwhelming (y={} != [0, {}))".format(y, self.size[0]))

        if not isinstance(x, (int, np.integer)):
            raise TypeError("Hyper-parameter only accepts positive integer value only (x={x})")
        elif not 0 <= x < self.size[1]:
            raise TypeError("Hyper-parameter is overwhelming (x={} != [0, {}))".format(x, self.size[1]))

        return self.getReverseLocation()[(y, x)]

    def _convertGraphToMatrixWithCache(self, graph_index: int) -> Tuple[int, int]:
        if not isinstance(graph_index, (int, np.integer)):
            raise TypeError("Hyper-parameter only accepts positive integer value only (index={index})")

        if not (0 <= graph_index < self.getNumberOfNodes()):
            raise TypeError("Hyper-parameter is overwhelming (index={} != [0, {}))"
                            .format(graph_index, self.getNumberOfNodes()))

        return self.getLocation()[graph_index]

    def _updateBombPosition(self, y: int, x: int) -> None:
        self.__bombPosition.append((y, x))

    def resetRandom(self) -> np.ndarray:
        data = np.uint16 if self.getNumberOfNodes() > np.iinfo(np.uint8).max else np.uint8
        return np.random.randint(0, self.getNumberOfNodes(), self.randomMaxSize, dtype=data)

    # ----------------------------------------------------------------------------------------------------------------
    # [0.2]: For Interface Matrix
    def _openNodeAtInterfaceMatrixByGraph(self, graph_index: int) -> bool:
        y, x = self._location[graph_index]
        return self._openNodeAtInterfaceMatrixByMatrix(y=y, x=x)

    def _openNodeAtInterfaceMatrixByMatrix(self, y: int, x: int) -> bool:
        if self._checkInput(y=y, x=x) is True:
            self._setInterfaceNode(y=y, x=x, value=1)
            return True

        warning("No update has been found")
        return False

    def _setInterfaceNode(self, y: int, x: int, value: int) -> None:
        self.interface_matrix[y, x] = value

    def _checkInterfaceNode(self, y: int, x: int, value: int) -> bool:
        return True if self.getInterfaceNode(y=y, x=x) == value else False

    def _checkInterfaceValidity(self) -> bool:
        max_valid_nodes: int = 0
        for value in (0, 1, self.FlagNotation, self.QuestionNotation):
            max_valid_nodes += np.argwhere(self.getInterfaceMatrix() not in value).shape[0]
        return True if max_valid_nodes == self.getNumberOfNodes() else False

    # ----------------------------------------------------------------------------------------------------------------
    # [1]: Building Information for Matrix before Running the Game
    def _buildBombPositions(self) -> None:
        """ Implementation to build the matrix by filling with bomb and other """
        if self.verbose is True:
            print("---------------------------------------------------------------------------------------")
            print("The game core is building the position for the bomb")

        bomb: int = 0
        notation: int = self.BombNotation
        max_y, max_x = self.getNumberOfNodesByAxis()
        visitedNodes: List[bool] = [False] * self.getNumberOfNodes()

        while bomb < self._bombNumber:
            if visitedNodes[self._random_positions[self.randomCounter]] is True:
                self.randomCounter += 1
                if self.randomCounter == self.randomMaxSize:
                    self.randomCounter: int = 0
                    self._random_positions: np.ndarray = self.resetRandom()
                continue
            else:
                visitedNodes[self._random_positions[self.randomCounter]] = True

            y, x = self._location[self._random_positions[self.randomCounter]]

            bomb += 1
            self.__coreMatrix[y, x] = notation
            self.__bombPosition.append((y, x))

            # Check top
            if 0 <= y - 1 < max_y:
                if visitedNodes[self._reversedLocation[(y - 1, x)]] is False:
                    self.__coreMatrix[y - 1, x] += 1

                # Check left
                if 0 <= x - 1 < max_x:
                    if visitedNodes[self._reversedLocation[(y - 1, x - 1)]] is False:
                        self.__coreMatrix[y - 1, x - 1] += 1

                # Check right
                if 0 <= x + 1 < max_x:
                    if visitedNodes[self._reversedLocation[(y - 1, x + 1)]] is False:
                        self.__coreMatrix[y - 1, x + 1] += 1

            if 0 <= x - 1 < max_x:
                if visitedNodes[self._reversedLocation[(y, x - 1)]] is False:
                    self.__coreMatrix[y, x - 1] += 1

            if 0 <= x + 1 < max_x:
                if visitedNodes[self._reversedLocation[(y, x + 1)]] is False:
                    self.__coreMatrix[y, x + 1] += 1

            # Check bottom
            if 0 <= y + 1 < max_y:
                if visitedNodes[self._reversedLocation[(y + 1, x)]] is False:
                    self.__coreMatrix[y + 1, x] += 1

                # Check left
                if 0 <= x - 1 < max_x:
                    if visitedNodes[self._reversedLocation[(y + 1, x - 1)]] is False:
                        self.__coreMatrix[y + 1, x - 1] += 1

                # Check right
                if 0 <= x + 1 < max_x:
                    if visitedNodes[self._reversedLocation[(y + 1, x + 1)]] is False:
                        self.__coreMatrix[y + 1, x + 1] += 1

            self.randomCounter += 1
            if self.randomCounter == self.randomMaxSize:
                self.randomCounter: int = 0
                self._random_positions: np.ndarray = self.resetRandom()

        pass

    def buildAdjacencyMatrix(self) -> None:
        if self.adjacencyMatrixStatus is False:
            self.adjacencyMatrixStatus = True

        if self.adjacencyMatrixStatus is True:
            max_y, max_x = self.getNumberOfNodesInVerticalAxis(), self.getNumberOfNodesInHorizontalAxis()
            for y, sub_matrix in enumerate(self.__coreMatrix):
                for x, node in enumerate(sub_matrix):
                    graph_index = self._reversedLocation[(y, x)]

                    if 0 <= y - 1 < max_y:
                        if 0 <= x - 1 < max_x:
                            new = self._reversedLocation[(y - 1, x - 1)]
                            self.adjacencyMatrixEight[graph_index, new] = 1

                        if 0 <= x + 1 < max_x:
                            new = self._reversedLocation[(y - 1, x + 1)]
                            self.adjacencyMatrixEight[graph_index, new] = 1

                        new = self._reversedLocation[(y - 1, x)]
                        self.adjacencyMatrixFour[graph_index, new] = 1
                        self.adjacencyMatrixEight[graph_index, new] = 1

                    if 0 <= y + 1 < max_y:
                        if 0 <= x - 1 < max_x:
                            new = self._reversedLocation[(y + 1, x - 1)]
                            self.adjacencyMatrixEight[graph_index, new] = 1

                        if 0 <= x + 1 < max_x:
                            new = self._reversedLocation[(y + 1, x + 1)]
                            self.adjacencyMatrixEight[graph_index, new] = 1

                        new = self._reversedLocation[(y + 1, x)]
                        self.adjacencyMatrixFour[graph_index, new] = 1
                        self.adjacencyMatrixEight[graph_index, new] = 1

                    if 0 <= x - 1 < max_x:
                        new = self._reversedLocation[(y, x - 1)]
                        self.adjacencyMatrixFour[graph_index, new] = 1
                        self.adjacencyMatrixEight[graph_index, new] = 1

                    if 0 <= x + 1 < max_x:
                        new = self._reversedLocation[(y, x + 1)]
                        self.adjacencyMatrixFour[graph_index, new] = 1
                        self.adjacencyMatrixEight[graph_index, new] = 1

        return None

    def build(self) -> None:
        self._buildBombPositions()

    # ----------------------------------------------------------------------------------------------------------------
    # [2]: Undo - Redo Function: Functions used to perform core-task and UI-task: Stack for Undo-Redo
    def _setInterfaceMatrix(self, new_matrix: np.ndarray) -> None:
        del self.interface_matrix
        self.interface_matrix = new_matrix
        self.calculateAccomplishedNode()

    def _reset_undoStack(self) -> None:
        del self.__undoStack
        self.__undoStack = []

    def _reset_redoStack(self) -> None:
        del self.__redoStack
        self.__redoStack = []

    def clickUndo(self) -> None:
        if not self.__undoStack:
            warning(" No state of UNDO is saved")
        elif self.checkIfPlayable() is False:
            warning(" You cannot play at current time")
        else:
            warning(" Add to REDO")
            self.__redoStack.append(self.getInterfaceMatrix().copy())

            new_matrix = self.__undoStack.pop()
            self._setInterfaceMatrix(new_matrix=new_matrix)

            if len(self.__redoStack) > self._maxStackSizeForUndoRedo:
                warning("The core: REDO Stack has held too many object. Automatically delete some entity")
                if CONFIG["Clean Time"] == 1:
                    self.__redoStack.pop(0)
                else:
                    self.__redoStack = self.__redoStack[CONFIG["Clean Time"]:].copy()
                    gc.collect()
        pass

    def clickRedo(self) -> None:
        if not self.__redoStack:
            warning(" No state of REDO is saved")
        elif self.checkIfPlayable() is False:
            warning(" You cannot play at current time")
        else:
            warning(" Add to UNDO")
            self.__undoStack.append(self.getInterfaceMatrix().copy())

            new_matrix = self.__redoStack.pop()
            self._setInterfaceMatrix(new_matrix=new_matrix)

            if len(self.__undoStack) > self._maxStackSizeForUndoRedo:
                warning("The core: UNDO Stack has held too many object. Automatically delete some entity")
                if CONFIG["Clean Time"] == 1:
                    self.__undoStack.pop(0)
                else:
                    self.__undoStack = self.__undoStack[CONFIG["Clean Time"]:].copy()
                    gc.collect()
        pass

    def resetStack(self):
        self._reset_undoStack()
        self._reset_redoStack()
        gc.collect()

    def _savePreviousState(self) -> None:
        if len(self.__undoStack) > self._maxStackSizeForUndoRedo:
            warning("The core: UNDO Stack has held too many object. Automatically delete some entity")
            if CONFIG["Clean Time"] == 1:
                self.__undoStack.pop(0)
            else:
                self.__undoStack = self.__undoStack[CONFIG["Clean Time"]:].copy()
                gc.collect()
        self.__undoStack.append(self.getInterfaceMatrix().copy())

    def _saveState(self, interface_matrix: np.ndarray):
        if len(self.__undoStack) > self._maxStackSizeForUndoRedo:
            warning("The core: UNDO Stack has held too many object. Automatically delete some entity")
            if CONFIG["Clean Time"] == 1:
                self.__undoStack.pop(0)
            else:
                self.__undoStack = self.__undoStack[CONFIG["Clean Time"]:].copy()
                gc.collect()

        if interface_matrix.shape != self.interface_matrix.shape:
            print("interface_matrix is not in accurate state")
            raise TypeError("interface_matrix is not in accurate state")

        self.__undoStack.append(interface_matrix.copy())

    # ----------------------------------------------------------------------------------------------------------------
    # [3]: User Interface Function
    def _recursiveDepthFirstFlow(self, index: int, recorded_stack: List[int]):
        # Time Complexity: O(1.5N) - Auxiliary Space: O(N)
        # Condition to check if that value has been pass yet, else discarded
        if recorded_stack[index] is False:
            # [1]: Add into the matrix
            recorded_stack[index] = True

            # [2]: Convert to Matrix Index for Calculation
            y, x = self._location[index]

            # Condition to check whether the core matrix that zero.
            # If self.__core[y, x] = 0: No object found, continue to flow; else, don't flow it
            if self._checkCoreNode(y=y, x=x, value=0) is True:
                # [3]: Flow the graph into four direction: Bottom, Top, Left, Right
                if y + 1 < self.size[0]:  # [3.1]: Flow to Bottom
                    self._recursiveDepthFirstFlow(index=self._convertMatrixToGraphWithCache(y=y + 1, x=x),
                                                  recorded_stack=recorded_stack)
                if y - 1 >= 0:  # [3.2]: Flow to Top
                    self._recursiveDepthFirstFlow(index=self._convertMatrixToGraphWithCache(y=y - 1, x=x),
                                                  recorded_stack=recorded_stack)
                if x - 1 >= 0:  # [3.2]: Flow to Left
                    self._recursiveDepthFirstFlow(index=self._convertMatrixToGraphWithCache(y=y, x=x - 1),
                                                  recorded_stack=recorded_stack)
                if x + 1 < self.size[1]:  # [3.3]: Flow to Right
                    self._recursiveDepthFirstFlow(index=self._convertMatrixToGraphWithCache(y=y, x=x + 1),
                                                  recorded_stack=recorded_stack)

        pass

    def _graphExpansion(self, y_start: int, x_start: int) -> None:
        if self._checkCoreNode(y=y_start, x=x_start, value=0) is True:
            visiting_stack: List[bool] = [False] * int(self.getNumberOfNodes())
            index_start = self._convertMatrixToGraphWithCache(y=y_start, x=x_start)
            self._recursiveDepthFirstFlow(index=index_start, recorded_stack=visiting_stack)

            for graph_index, state in enumerate(visiting_stack):
                if state is True:
                    self._openNodeAtInterfaceMatrixByGraph(graph_index=graph_index)

        pass

    def getNeighbor8Unrevealed(self, y: int, x: int) -> List[Tuple[int, int]]:
        neighborEightLocation: List[Tuple[int, int]] = self._getNeighbors8Axis(y=y, x=x)
        counter: int = len(neighborEightLocation) - 1
        while counter > -1:
            y_, x_ = neighborEightLocation[counter]
            if self._checkInterfaceNode(y=y_, x=x_, value=0) is False:
                neighborEightLocation.pop(counter)
            counter -= 1
        return neighborEightLocation

    def multiClick(self, y: int, x: int) -> None:
        # To activate this function, there are some condition that needs to be validate
        # [1]: Player must be playable (Of course)
        # [2]: The node that you double click must have been previously opened
        # [3]: The node open should not be an empty node
        if self.checkIfPlayable() is False or self._checkInterfaceNode(y=y, x=x, value=1) is False or \
                self._checkCoreNode(y=y, x=x, value=0) is True:
            return None

        # [1]: Get all neighbors' position & Remove all invalid node(s)
        # Valid Node is determined if that node was not revealed. Note that the valid node could be a bomb
        neighborEightLocation = self.getNeighbor8Unrevealed(y=y, x=x)
        print(f"Current State: ({y}, {x}) --> Neighbor: {neighborEightLocation}")
        # [2]: If there are still some node that has been available: Do next move --> Else: No status would be save
        if len(neighborEightLocation) != 0:
            # Search Bomb
            # If there is a bomb, no update would be doing
            contain_bomb: bool = False
            for y_, x_ in neighborEightLocation:
                if self.checkIfBomb(y=y_, x=x_) is True:
                    warning(f" Bomb has been found at ({y_}, {x_})")
                    contain_bomb = True

            if contain_bomb is False:
                # No bomb has been found = Safe; So, we would reveal all the nodes that has been accurately marked.
                # An optimized version is saved all current state first, then reveal all nodes without saving to
                # avoid memory burden.
                self._savePreviousState()
                for y_, x_ in neighborEightLocation:
                    self.click(y=y_, x=x_, message="LeftMouse", enableSaving=False)

        return None

    def click(self, y: int, x: int, message: str, enableSaving: bool = True) -> None:
        # Attach function used when clicking image on the interface nodes
        # Note that self.click() is also responsible for controlling whether playing can continue playing the game
        if message not in MOUSE_MESSAGE.keys():
            raise ValueError("Re-check the source code for data validation. "
                             "Clicked mouse has emit unknown message ({})".format(message))

        if self.checkIfPlayable() is True:
            # [1]: Save the previous state
            if enableSaving is True:
                self._savePreviousState()

            # [2]: Click
            # [2.1]: Click by left-mouse
            if MOUSE_MESSAGE[message] == "L":
                # [2.1.1]: Click by left-mouse only works on deactivated interface node.
                # If the associated core node is empty, do graph_flowing; Else, just open
                # self._graphExpansion guarantee it does not touch the bomb
                if self._checkInterfaceNode(y=y, x=x, value=0) is True:
                    if self._checkCoreNode(y=y, x=x, value=0):
                        self._graphExpansion(y_start=y, x_start=x)
                        self.calculateAccomplishedNode()
                    else:
                        self._openNodeAtInterfaceMatrixByMatrix(y=y, x=x)
                        if self.checkIfBomb(y=y, x=x) is True:
                            self.PlayingStatus = False
                            self.VictoryStatus = False
                        self._accomplishedNode += 1

            # [2.2]: Click by left-mouse
            elif MOUSE_MESSAGE[message] == "R":
                # If that interface node has not been opened. Assign as Flag
                if self._checkInterfaceNode(y=y, x=x, value=0) is True:
                    self._setInterfaceNode(y=y, x=x, value=self.FlagNotation)
                    self._remainingFlags -= 1
                    self._accomplishedNode += 1

                # If that interface node was assigned as Flag. Assign as Question
                elif self._checkInterfaceNode(y=y, x=x, value=self.FlagNotation) is True:
                    self._setInterfaceNode(y=y, x=x, value=self.QuestionNotation)
                    self._remainingFlags += 1
                    self._accomplishedNode -= 1

                # If that interface node was assigned as Question. Unassigned it
                elif self._checkInterfaceNode(y=y, x=x, value=self.QuestionNotation):
                    self._setInterfaceNode(y=y, x=x, value=0)

            if self.getUnaccomplishedNodes() == 0 and self.checkIfVictory() is False:
                self.PlayingStatus = False
                self.VictoryStatus = True

        else:
            warning(" You cannot play at current time.")
        pass

    # ----------------------------------------------------------------------------------------------------------------
    # [4]: Checking Function
    def checkIfClickable(self, y: int, x: int) -> bool:
        if self._checkInput(y=y, x=x) is True and self.getInterfaceNode(y=y, x=x) != 1:
            return True
        return False

    def checkIfBomb(self, y: int, x: int) -> bool:
        if self._checkInput(y=y, x=x) is True and self._checkCoreNode(y=y, x=x, value=self.BombNotation) is True:
            return True
        return False

    def checkGamingStatus(self) -> None:
        # In the game there are ton's of condition to be validate as winning the game
        # [1]: No flags remaining and No Questions Mark
        # [2]: All the flags has been assigned correctly in bomb position
        if self.getQuestionPositions().shape[0] == 0 and self.getRemainingFlags() == 0:
            bomb_position: List[Tuple[int, int]] = self.getBombPositions(descending=False)
            for position in range(len(bomb_position) - 1, -1, -1):
                y, x = bomb_position[position]
                if self._checkInterfaceNode(y=y, x=x, value=self.FlagNotation):
                    bomb_position.pop()
                else:
                    self.VictoryStatus = False
                    break
            if not bomb_position:
                self.PlayingStatus = False
                self.VictoryStatus = True
        elif self.getUnaccomplishedNodes() == 0 and self.PlayingStatus is True and self.VictoryStatus is False:
            self.PlayingStatus = False
            self.VictoryStatus = True

    def checkIfVictory(self) -> bool:
        return self.VictoryStatus

    def checkIfPlayable(self) -> bool:
        return self.PlayingStatus

    def calculateAccomplishedNode(self):
        x: np.ndarray = self.getInterfaceMatrix().view()
        self._accomplishedNode: int = x[(x == 1) | (x == -1)].size

    def resetGame(self, size: Optional[Union[int, Tuple[int, int]]] = 16, difficulty: str = "Medium"):
        # [1]: Validate Hyper-parameters
        if True:
            if size == -1 or size is None:
                pass
            elif isinstance(size, (int, Tuple)):
                if isinstance(size, int):
                    size: Tuple[int, int] = (size, size)
                for value in size[:2]:
                    if not isinstance(value, int):
                        raise ValueError(
                            " False Initialization: The size should be a tuple with 2-positive integers or "
                            "positive integer")

                if self.size[0] != size[0] or self.size[1] != size[1]:
                    self.adjacencyMatrixStatus = False
                    self.size = size[:2]
                    self._random_positions: np.ndarray = self.resetRandom()
                    self._location = {i: self._convertGraphToMatrixWithMath(i) for i in range(self.getNumberOfNodes())}
                    self._reversedLocation = {value: key for key, value in self.getLocation().items()}

            if difficulty is not None:
                difficulty_validation(key=difficulty)
                self.difficulty = difficulty

            self._bombNumber: int = int(DIFFICULTY[self.difficulty][0] * (self.size[0] / 2 + self.size[1] / 2) **
                                        DIFFICULTY[self.difficulty][1])
            pass

        # [2]: Reset everything having
        # [2.1]: Setup Core for Data Implementation
        self.__coreMatrix: np.ndarray = np.zeros(shape=self.size, dtype=np.int8)
        self.__bombPosition.clear()
        self._remainingFlags: int = self._bombNumber

        # [2]: Set Configuration
        self.interface_matrix: np.ndarray = np.zeros(shape=self.size, dtype=np.int8)
        self._accomplishedNode: int = 0

        if self.adjacencyMatrixStatus is False:
            self.adjacencyMatrixFour: np.ndarray = \
                np.zeros(shape=(self.getNumberOfNodes(), self.getNumberOfNodes()), dtype=np.uint8)
            self.adjacencyMatrixEight: np.ndarray = \
                np.zeros(shape=(self.getNumberOfNodes(), self.getNumberOfNodes()), dtype=np.uint8)
            self.buildAdjacencyMatrix()

        # [3]: Set Undo & Redo Features
        self.__undoStack: List[np.ndarray] = []
        self.__redoStack: List[np.ndarray] = []

        # [4]: Gaming Status
        self.VictoryStatus: bool = False
        self.PlayingStatus: bool = True

        # [5]: Running Function
        self.build()
        self.displayInformation()

    def fastReset(self):
        self.__coreMatrix: np.ndarray = np.zeros(shape=self.size, dtype=np.int8)
        self.__bombPosition.clear()
        self._remainingFlags: int = self._bombNumber
        self.build()

    # [x]: Getter and Display Function --------------------------------------------------------
    # [x.1] Getter Function
    def _getNeighbors4Axis(self, y: int, x: int) -> List[Tuple[int, int]]:
        position: List[Tuple[int, int]] = []
        max_y, max_x = self.getNumberOfNodesByAxis()
        if 0 <= x < max_x:
            if 0 <= y - 1 < max_y:
                position.append((y - 1, x))
            if 0 <= y + 1 < max_y:
                position.append((y + 1, x))

        if 0 <= y < max_y:
            if 0 <= x - 1 < max_x:
                position.append((y, x - 1))
            if 0 <= x + 1 < max_x:
                position.append((y, x + 1))

        return position

    def _getNeighbors8Axis(self, y: int, x: int) -> List[Tuple[int, int]]:
        position: List[Tuple[int, int]] = self._getNeighbors4Axis(y=y, x=x)
        max_y, max_x = self.getNumberOfNodesByAxis()
        if 0 <= y - 1 < max_y:
            if 0 <= x - 1 < max_x:
                position.append((y - 1, x - 1))
            if 0 <= x + 1 < max_x:
                position.append((y - 1, x + 1))

        if 0 <= y + 1 < max_y:
            if 0 <= x - 1 < max_x:
                position.append((y + 1, x - 1))
            if 0 <= x + 1 < max_x:
                position.append((y + 1, x + 1))

        return position

    def getCoreMatrix(self) -> np.ndarray:
        return self.__coreMatrix.copy()

    def getHashingCoreMatrix(self, extraHash: bool = False) -> np.ndarray:
        matrix: np.ndarray = self.getCoreMatrix()
        bomb_location: List[Tuple[int, int]] = self.getBombPositions()
        if extraHash is True:
            for y, x in bomb_location:
                respectivePosition = self._getNeighbors8Axis(y=y, x=x)
                matrix[y, x] = max([matrix[y_, x_] for y_, x_ in respectivePosition]) + 1
        else:
            for y, x in bomb_location:
                respectivePosition = self._getNeighbors8Axis(y=y, x=x)
                matrix[y, x] = max([matrix[y_, x_] for y_, x_ in respectivePosition])
        return matrix

    def getCoreNode(self, y: int, x: int) -> np.integer:
        return self.getCoreMatrix()[y, x]

    def getInterfaceMatrix(self) -> np.ndarray:
        return self.interface_matrix

    def getInterfaceNode(self, y: int, x: int):
        return self.getInterfaceMatrix()[y, x]

    def getNumberOfNodes(self) -> int:
        return self.getNumberOfNodesInVerticalAxis() * self.getNumberOfNodesInHorizontalAxis()

    def getNumberOfNodesInVerticalAxis(self) -> int:
        return self.size[0]

    def getNumberOfNodesInHorizontalAxis(self) -> int:
        return self.size[1]

    def getNumberOfNodesByAxis(self) -> Tuple[int, int]:
        return self.size

    def getBombNumber(self) -> int:
        return self._bombNumber

    def getBombPositions(self, descending: bool = False) -> List[Tuple[int, int]]:
        return self.__bombPosition.copy() if descending is False else list(reversed(self.__bombPosition)).copy()

    def getActivationPosition(self) -> np.ndarray:
        return np.argwhere(self.getInterfaceMatrix() != 0)

    def getOpeningPositions(self) -> np.ndarray:
        return np.argwhere(self.getInterfaceMatrix() == 1)

    def getFlagPositions(self) -> np.ndarray:
        return np.argwhere(self.getInterfaceMatrix() == self.FlagNotation)

    def getQuestionPositions(self) -> np.ndarray:
        return np.argwhere(self.getInterfaceMatrix() == self.QuestionNotation)

    def getRemainingFlags(self) -> int:
        return self._remainingFlags

    def getAccomplishedNodes(self) -> int:
        return self._accomplishedNode

    def getUnaccomplishedNodes(self) -> int:
        return self.getNumberOfNodes() - self._accomplishedNode

    def getLocation(self) -> Dict[int, Tuple[int, int]]:
        return self._location

    def getReverseLocation(self) -> Dict[Tuple[int, int], int]:
        return self._reversedLocation

    def identifyBombByTanh(self) -> np.ndarray:
        # If tanhMatrix, convert affection nodes first
        tanhMatrix = self.getCoreMatrix()
        for value in range(1, 9):
            tanhMatrix[tanhMatrix == value] = 1
        tanhMatrix[tanhMatrix == self.BombNotation] = 2

        return tanhMatrix

    def identifyBombBySigmoid(self) -> np.ndarray:
        # If tanhMatrix, convert affection nodes first
        sigmoidMatrix = self.getCoreMatrix()
        for value in range(1, 9):
            sigmoidMatrix[sigmoidMatrix == value] = 0
        sigmoidMatrix[sigmoidMatrix == self.BombNotation] = 1

        return sigmoidMatrix

    def convertTanhToSigmoid(self, tanhMatrix: Optional[np.ndarray]) -> np.ndarray:
        sigmoidMatrix = self.identifyBombByTanh() if tanhMatrix is None else tanhMatrix.copy()
        sigmoidMatrix[sigmoidMatrix == 1] = 0
        sigmoidMatrix[sigmoidMatrix == 2] = 1

        return sigmoidMatrix

    def searchBombWithActivation(self, needRavel: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        tanhMatrix = self.identifyBombByTanh() if needRavel is False else self.identifyBombByTanh().ravel()
        sigmoidMatrix = self.convertTanhToSigmoid(tanhMatrix=tanhMatrix) \
            if needRavel is False else self.convertTanhToSigmoid(tanhMatrix=tanhMatrix).ravel()

        return tanhMatrix, sigmoidMatrix

    # [x.2] Display Function
    def displayCoreMatrix(self) -> None:
        print("=" * 100)
        print("Core Matrix: ")
        print(self.getCoreMatrix())
        print("Matrix Size: {} --> Association Node: {} <---> Bomb Number: {}"
              .format(self.size, self.getNumberOfNodes(), self.getBombNumber()))
        print("=" * 100)
        print()

    def displayBetterCoreMatrix(self) -> None:
        print("=" * 100)
        print("Better Core Matrix: ")
        matrix: np.ndarray = np.array(self.getCoreMatrix(), dtype=np.object_)
        matrix[matrix == self.BombNotation] = "*"
        matrix[matrix == 0] = "_"
        for value in range(1, 9):
            matrix[matrix == value] = str(value)

        for row in range(0, matrix.shape[0]):
            print(matrix[row].tolist())
        print("\nMatrix Size: {} --> Association Node: {} <---> Bomb Number: {}"
              .format(self.size, self.getNumberOfNodes(), self.getBombNumber()))
        print("=" * 100)
        print()

    def displayHashedCoreMatrix(self, extraHash: bool = False) -> None:
        print("=" * 100)
        print("Hashing Core Matrix: ")
        print(self.getHashingCoreMatrix(extraHash=extraHash))
        print("Matrix Size: {} --> Association Node: {} <---> Bomb Number: {}"
              .format(self.size, self.getNumberOfNodes(), self.getBombNumber()))
        print("=" * 100)
        print()

    def displayBetterHashedCoreMatrix(self, extraHash: bool = False) -> None:
        print("=" * 100)
        print("Better Hashing Core Matrix: ")
        matrix: np.ndarray = np.array(self.getHashingCoreMatrix(extraHash=extraHash), dtype=np.object_)
        matrix[matrix == 0] = "_"
        for value in range(1, 9):
            matrix[matrix == value] = str(value)

        for row in range(0, matrix.shape[0]):
            print(matrix[row].tolist())
        print("\nMatrix Size: {} --> Association Node: {} <---> Bomb Number: {}"
              .format(self.size, self.getNumberOfNodes(), self.getBombNumber()))
        print("=" * 100)
        print()

    def displayInterfaceMatrix(self) -> None:
        print("=" * 100)
        print("Interface Matrix: ")
        matrix = self.getInterfaceMatrix()
        for row in range(0, matrix.shape[0]):
            print(matrix[row].tolist())
        print("=" * 100)
        print()

    def displayBetterInterfaceMatrix(self) -> None:
        print("=" * 100)
        print("Better Interface Matrix: ")
        matrix: np.ndarray = np.array(self.getInterfaceMatrix().copy(), dtype=np.object_)
        matrix[matrix == 1] = "O"
        matrix[matrix == 0] = "_"
        matrix[matrix == self.FlagNotation] = "F"
        matrix[matrix == self.QuestionNotation] = "?"
        for row in range(0, matrix.shape[0]):
            print(matrix[row].tolist())
        print("=" * 100)
        print()

    def displayInformation(self) -> None:
        ratio = self.getBombNumber() / self.getNumberOfNodes()
        print(f"(Size: {self.size} --- Difficulty: {self.difficulty}) --> Bomb Number(s): "
              f"{self.getBombNumber()} / {self.getNumberOfNodes()} "
              f"(Ratio: {round(ratio * 100, 2)} % - "
              f"Overwhelming: {9 *self.getBombNumber() >= self.getNumberOfNodes()})")
    # [ ] --------------------------------------------------------
