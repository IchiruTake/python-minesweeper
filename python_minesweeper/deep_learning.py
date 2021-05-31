import numpy as np
from typing import List, Tuple, Optional, Union, Dict

import pandas as pd

from core import minesweeper
import config
from time import time
from preprocessing import ReadFile, ExportFile

# from tensorflow.keras.layers import Dense, Concatenate, Add, Average
# from tensorflow.keras import Input, Model
# from tensorflow.keras.optimizers import Adam


class LearningModel:
    def __init__(self, size: Union[int, Tuple[int, int]] = 16, numberOfSamples: Union[int, float] = int(2e6),
                 randomState: int = 42, easyRatio: float = 0.25, mediumRatio: float = 0.25, hardRatio: float = 0.25,
                 extremeRatio: float = 0.25):
        # Hyper-parameter Verification
        if True:
            numberOfSamples: int = int(numberOfSamples)

            temp: List[float] = [easyRatio, mediumRatio, hardRatio, extremeRatio]
            total: float = sum(temp)
            if total != 1:
                temp = [int(temp[i] / total * numberOfSamples) for i in range(len(temp))]
                total: float = sum(temp)
                while total < numberOfSamples:
                    x = np.random.randint(0, 3, size=1)[0]
                    temp[x] += 1
                    total += 1
            else:
                for idx, value in enumerate(temp):
                    temp[idx] = int(value * numberOfSamples)
            pass

        self.gameCore: minesweeper = minesweeper(size=size, difficulty="Easy")

        self._adjacencyMatrixFourConnection: Optional[np.ndarray] = self.gameCore.adjacencyMatrixFour
        self._adjacencyMatrixEightConnection: Optional[np.ndarray] = self.gameCore.adjacencyMatrixEight

        self.number_of_samples: int = int(numberOfSamples)
        self.random_state: int = randomState
        self.distribution: Dict[int, List] = {i: [key, temp[i], 0] for i, key in enumerate(config.DIFFICULTY.keys())}
        for idx, key in enumerate(self.distribution.keys()):
            if 1 <= idx < len(temp):
                self.distribution[idx][2] = sum(self.distribution[idx - 1][1:])
        print(self.distribution)
        self.size: Tuple[int, int] = (self.number_of_samples, self.gameCore.getNumberOfNodes())

        self.originalHashedState: np.ndarray = np.zeros(shape=self.size, dtype=np.int8)

        # Combining tanh and sigmoid for prediction
        # In sigmoid: 1: bomb --- 0: no bomb
        # In tanh: 1: bomb --- 0: affected location --- -1: no bomb

        self.tanhResult: np.ndarray = np.zeros(shape=self.size, dtype=np.int8)
        self.sigmoidResult: np.ndarray = np.zeros(shape=self.size, dtype=np.int8)
        self.adjacencyFourState: Optional[np.ndarray] = None
        self.adjacencyEightState: Optional[np.ndarray] = None

    def _multiply(self):
        print("=" * 80)
        print("The object is now running matrix multiplication")
        start = time()
        self.adjacencyFourState = np.matmul(self.originalHashedState, self._adjacencyMatrixFourConnection)
        self.adjacencyEightState = np.matmul(self.originalHashedState, self._adjacencyMatrixEightConnection)
        print(f"Executing Time: {round(time() - start, 6)}s")

    def _build(self, minimum_hashing: bool, value: List, verbose: int = 10000, start: float = 0) -> None:
        for i in range(value[2], value[2] + value[1]):
            if i % verbose == 0:
                print("This is the row #{} ---> Executing Time: {:.6f}s".format(i, time() - start))

            self.gameCore.fastReset()
            self.originalHashedState[i] = self.gameCore.getHashingCoreMatrix(minimum_mode=minimum_hashing).ravel()
            self.tanhResult[i], self.sigmoidResult[i] = self.gameCore.searchBombWithActivation(needRavel=True)
        return None

    def build(self, minimum_hashing: bool = False, verbose: int = 10000):
        # [1]: Initialization
        print("=" * 80)
        print("Data has been extracting:")
        self.gameCore.displayInformation()
        running_time = time()
        # [2]: Run the core
        for idx, item in enumerate(self.distribution.items()):
            start: float = time()
            if idx != 0:
                self.gameCore.resetGame(size=None, difficulty=item[1][0])
            self._build(minimum_hashing=minimum_hashing, value=item[1], verbose=verbose, start=start)
            print("Executing Time: {:.6f}s".format(time() - start))

        # [3]: Matrix Multiplication
        print("ENDING LOOP: Executing Time: {:.6f}s".format(time() - running_time))
        self._multiply()

    def save(self, originalFilePath: Optional[str] = None, fourStateFilePath: Optional[str] = None,
             eightStateFilePath: Optional[str] = None, tanhFilePath: Optional[str] = None,
             sigmoidFilePath: Optional[str] = None):

        if originalFilePath is not None:
            ExportFile(DataFrame=pd.DataFrame(data=self.originalHashedState, index=None, columns=None),
                       FilePath=originalFilePath, index=False, index_label=None)

        if fourStateFilePath is not None:
            ExportFile(DataFrame=pd.DataFrame(data=self.adjacencyFourState, index=None, columns=None),
                       FilePath=fourStateFilePath, index=False, index_label=None)

        if eightStateFilePath is not None:
            ExportFile(DataFrame=pd.DataFrame(data=self.adjacencyEightState, index=None, columns=None),
                       FilePath=eightStateFilePath, index=False, index_label=None)

        if tanhFilePath is not None:
            ExportFile(DataFrame=pd.DataFrame(data=self.tanhResult, index=None, columns=None),
                       FilePath=tanhFilePath, index=False, index_label=None)

        if sigmoidFilePath is not None:
            ExportFile(DataFrame=pd.DataFrame(data=self.sigmoidResult, index=None, columns=None),
                       FilePath=sigmoidFilePath, index=False, index_label=None)

    def load(self, originalFilePath: Optional[str] = None, fourStateFilePath: Optional[str] = None,
             eightStateFilePath: Optional[str] = None, tanhFilePath: Optional[str] = None,
             sigmoidFilePath: Optional[str] = None):

        if originalFilePath is not None:
            self.originalHashedState = ReadFile(FilePath=originalFilePath, header=None, get_values=True, dtype=np.int8)

        if fourStateFilePath is not None:
            self.adjacencyFourState = ReadFile(FilePath=fourStateFilePath, header=None, get_values=True, dtype=np.int8)

        if eightStateFilePath is not None:
            self.adjacencyEightState = ReadFile(FilePath=eightStateFilePath, header=None, get_values=True, dtype=np.int8)

        if tanhFilePath is not None:
            self.tanhResult = ReadFile(FilePath=tanhFilePath, header=None, get_values=True, dtype=np.int8)

        if sigmoidFilePath is not None:
            self.sigmoidResult = ReadFile(FilePath=sigmoidFilePath, header=None, get_values=True, dtype=np.int8)
