from logging import warning

import numpy as np
from typing import List, Tuple, Optional, Union, Dict
from core import minesweeper
import config
from time import time
from preprocessing import timing_profiler
from tensorflow.keras.layers import Dense, Concatenate, Add, Average
from tensorflow.keras import Input, Model
from tensorflow.keras.optimizers import Adam


class LearningModel:
    def __init__(self, size: Union[int, Tuple[int, int]] = 16, number_of_samples: Union[int, float] = int(2e6),
                 random_state: int = 42, easy_mode: float = 0.25, medium_mode: float = 0.25, hard_mode: float = 0.25,
                 extreme_mode: float = 0.25):
        # Hyper-parameter Verification
        if True:
            number_of_samples: int = int(number_of_samples)

            temp: List[float] = [easy_mode, medium_mode, hard_mode, extreme_mode]
            total: float = sum(temp)
            if total != 1:
                temp = [int(temp[i] / total * number_of_samples) for i in range(len(temp))]
                total: float = sum(temp)
                while total < number_of_samples:
                    x = np.random.randint(0, 3, size=1)[0]
                    temp[x] += 1
                    total += 1
            else:
                for idx, value in enumerate(temp):
                    temp[idx] = int(value * number_of_samples)
            pass

        self.gameCore: minesweeper = minesweeper(size=size, difficulty="Easy")

        self.adjacencyMatrixFourConnection: Optional[np.ndarray] = self.gameCore.adjacencyMatrixFour
        self.adjacencyMatrixEightConnection: Optional[np.ndarray] = self.gameCore.adjacencyMatrixEight

        self.number_of_samples: int = int(number_of_samples)
        self.random_state: int = random_state
        self.distribution: List[float] = temp
        self.size: Tuple[int, int] = (self.number_of_samples, self.gameCore.getNumberOfNodes())

        self.originalHashedState: np.ndarray = np.zeros(shape=self.size, dtype=np.int8)

        # Combining tanh and sigmoid for prediction
        # In sigmoid: 1: bomb --- 0: no bomb
        # In tanh: 1: bomb --- 0: affected location --- -1: no bomb

        self.tanhResult: np.ndarray = np.zeros(shape=self.size, dtype=np.int8)
        self.sigmoidResult: np.ndarray = np.zeros(shape=self.size, dtype=np.int8)
        self.adjacencyFourState: Optional[np.ndarray] = None
        self.adjacencyEightState: Optional[np.ndarray] = None

    # @timing_profiler
    def build(self, minimum_hashing: bool = False, verbose: int = 10000):
        print("=" * 80)
        print("Data has been extracting")
        key = list(config.DIFFICULTY.keys())
        counting_state: Dict[str, int] = {key[i]: self.distribution[i] for i in range(0, len(self.distribution))}
        current_state, counting = 0, 0
        print("Samples Distribution:", counting_state)

        start: float = time()
        for state in range(0, self.number_of_samples):
            if state % verbose == 0:
                print(f"This is the row #{state}: Executing Time: {round(time() - start, 6)}s")

            if counting >= counting_state[key[current_state]]:
                counting = 0
                current_state += 1
                self.gameCore.resetGame(size=None, difficulty=key[current_state])
            else:
                self.gameCore.fastReset()

            if current_state > len(key):
                warning(f" No matrix can be instantiated. Current: {state} || Maximum: {self.number_of_samples - 1}")
                break

            self.originalHashedState[state]: np.ndarray = \
                self.gameCore.getHashingCoreMatrix(minimum_mode=minimum_hashing).ravel()
            self.tanhResult[state], self.sigmoidResult[state] = self.gameCore.searchBombWithActivation(needRavel=True)
            counting += 1

        print(f"This is the row #{self.number_of_samples}: Executing Time: {round(time() - start, 6)}s")

    def multiply(self):
        print("=" * 80)
        print("The object is now running matrix multiplication")
        start = time()
        self.adjacencyFourState = np.matmul(self.originalHashedState, self.adjacencyMatrixFourConnection)
        self.adjacencyEightState = np.matmul(self.originalHashedState, self.adjacencyMatrixEightConnection)
        print(f"Executing Time: {round(time() - start, 6)}s")

