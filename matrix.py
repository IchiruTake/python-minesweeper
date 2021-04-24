import numpy as np
from typing import Tuple, Union
from time import time
from sys import maxsize
from copy import deepcopy
from logging import warning


class minesweeper:
    def __init__(self, size: Union[int, Tuple[int]], bomb_number: int):
        np.set_printoptions(threshold=maxsize)
        if not isinstance(size, (int, Tuple[int])):
            raise ValueError(" False Initialization. The size should be an integer.")
        if not isinstance(bomb_number, (int, Tuple[int])):
            raise ValueError(" False Initialization. The number of bombs should be an integer.")

        if size <= 0:
            raise ValueError(" False Initialization. The size should be larger than zero")
        if bomb_number <= 0:
            raise ValueError(" False Initialization. The number of bombs should be larger than zero")

        if isinstance(size, int):
            if bomb_number >= size*size:
                raise ValueError("The number of bomb is exceeded")
            self.__matrix__ = np.zeros(shape=(size, size), dtype=np.int16)
            self.size = (size, size)
        else:
            if bomb_number >= size[0]*size[1]:
                raise ValueError("The number of bomb is exceeded")
            self.__matrix__ = np.zeros(shape=size, dtype=np.int16)
            self.size = size

        self.interface_matrix: np.ndarray = np.full(self.size, "-", dtype=np.object_)
        self.clickable_matrix: np.ndarray = np.zeros(self.size, dtype=np.uint8)
        self.__bombNumber__: int = bomb_number

        # [2]: Set Configuration
        self.__bomb_notation = -20
        self.__flag = 50

        # [3]: Set Undo & Redo Features
        self.__max_size_for_UndoRedo = 24
        self.__undo_stack__ = []
        self.__redo_stack__ = []

    # ----------------------------------------------------------------------------------------------------------------
    def __set_matrix(self, matrix: np.ndarray):
        if matrix.shape != self.get_matrix().shape:
            warning(" The new matrix is not fit with the original matrix")
        else:
            self.__matrix__ = matrix

    def get_matrix(self) -> np.ndarray:
        return self.__matrix__

    def get_document(self) -> None:
        pass

    # ----------------------------------------------------------------------------------------------------------------
    def click_undo(self):
        if not self.__undo_stack__:
            raise ValueError("No state is saved")
        else:
            new_matrix = self.__undo_stack__.pop()
            self.__set_matrix(matrix=new_matrix)
            self.__redo_stack__.append(new_matrix)

    def click_redo(self):
        if not self.__redo_stack__:
            raise ValueError("No state is saved")
        else:
            new_matrix = self.__redo_stack__.pop()
            self.__set_matrix(matrix=new_matrix)
            self.__undo_stack__.append(new_matrix)

    def update_state(self):
        msg = None
        if len(self.__undo_stack__) > self.__max_size_for_UndoRedo:
            msg = " WARNING: The game has held too many object. Automatically delete some entity"
            warning(msg)
            self.__undo_stack__.pop(0)
        self.__undo_stack__.append(deepcopy(self.get_matrix()))
        return msg

    def reset_undoStack(self):
        del self.__undo_stack__
        self.__undo_stack__ = []

    def reset_redoStack(self):
        del self.__redo_stack__
        self.__redo_stack__ = []

    def save_state(self):
        self.reset_undoStack()
        self.reset_redoStack()

    # ----------------------------------------------------------------------------------------------------------------
    def build_bombs_position(self):
        bomb = 0
        while bomb < self.__bombNumber__:
            x, y = np.random.randint(0, self.get_matrix().shape[1], size=2, dtype=np.int16)
            if self.get_matrix()[y][x] == self.__bomb_notation:
                continue

            if 0 <= y - 1 < self.size[0] and 0 <= x - 1 < self.size[1] and \
                    self.get_matrix()[y - 1, x - 1] != self.__bomb_notation:
                self.get_matrix()[y - 1, x - 1] += 1  # Check top-left

            if 0 <= y - 1 < self.size[0] and 0 <= x < self.size[1] and \
                    self.get_matrix()[y - 1, x] != self.__bomb_notation:
                self.get_matrix()[y - 1, x] += 1  # Check top-mid

            if 0 <= y - 1 < self.size[0] and 0 <= x + 1 < self.size[1] and \
                    self.get_matrix()[y - 1, x + 1] != self.__bomb_notation:
                self.get_matrix()[y - 1, x + 1] += 1  # Check top-right

            if 0 <= y < self.size[0] and 0 <= x - 1 < self.size[1] and \
                    self.get_matrix()[y, x - 1] != self.__bomb_notation:
                self.get_matrix()[y, x - 1] += 1  # Check mid-left

            if 0 <= y < self.size[0] and 0 <= x + 1 < self.size[1] and \
                    self.get_matrix()[y, x + 1] != self.__bomb_notation:
                self.get_matrix()[y, x + 1] += 1  # Check mid-right

            if 0 <= y + 1 < self.size[0] and 0 <= x - 1 < self.size[1] and \
                    self.get_matrix()[y + 1, x - 1] != self.__bomb_notation:
                self.get_matrix()[y + 1, x - 1] += 1  # Check bottom-left

            if 0 <= y + 1 < self.size[0] and 0 <= x < self.size[1] and \
                    self.get_matrix()[y + 1, x] != self.__bomb_notation:
                self.get_matrix()[y + 1, x] += 1  # Check bottom-mid

            if 0 <= y + 1 < self.size[0] and 0 <= x + 1 < self.size[1] and \
                    self.get_matrix()[y + 1, x + 1] != self.__bomb_notation:
                self.get_matrix()[y + 1, x + 1] += 1  # Check bottom-right

    def build(self):
        self.build_bombs_position()
        self.clickable_matrix[self.get_matrix() != 0] = 1

    def __check_input(self, y: int, x: int):
        if not isinstance(y, int) or not isinstance(x, int):
            warning(" Hyper-parameter only accepts integer value only")
            return False

        if y < 0 or y >= self.get_matrix().shape[0]:
            warning(" y={} does not fit into matrix".format(y))
            return False

        if x < 0 or x >= self.get_matrix().shape[1]:
            warning(" x={} does not fit into matrix".format(x))
            return False
        return True

    def check_if_clickable(self, y: int, x: int):
        if self.__check_input(y=y, x=x) is True and self.clickable_matrix[y, x] == 1:
            return True
        return False

    def check_if_bomb(self, y: int, x: int):
        if self.__check_input(y=y, x=x) is True and self.get_matrix()[y, x] == self.__bomb_notation:
            return True
        return False

    # ----------------------------------------------------------------------------------------------------------------
    def display_modified(self):
        new_matrix = np.array(self.get_matrix(), dtype=np.object_)
        new_matrix[new_matrix == 0] = "-"
        print(new_matrix)

    def display_original(self):
        print(self.get_matrix())

    def display_interface(self):
        print(self.interface_matrix)

    def display_clickable_matrix(self):
        print(self.clickable_matrix)


game = minesweeper(size=15, bomb_number=20)
game.build()
game.display_original()
game.display_clickable_matrix()






