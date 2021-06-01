import numpy as np
from typing import List, Tuple, Optional, Union, Dict

import pandas as pd
from sklearn.model_selection import train_test_split
from core import minesweeper
import config
from time import time
from preprocessing import ReadFile, ExportFile

from tensorflow.keras.layers import Dense, Average
from tensorflow.keras import Input, Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import (CSVLogger, EarlyStopping, ModelCheckpoint, TerminateOnNaN)


class LearningModel:
    def __init__(self, matrixSize: Union[int, Tuple[int, int]] = 16, numberOfSamples: Union[int, float] = int(2e6),
                 sigmoidLearning: bool = True, tanhLearning: bool = False,
                 randomState: int = 42, easyRatio: float = 0.25, mediumRatio: float = 0.25, hardRatio: float = 0.25,
                 extremeRatio: float = 0.25):
        # Hyper-parameter Verification
        if True:
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

            if sigmoidLearning is False and tanhLearning is False:
                raise TypeError("We only allows one learning mode at the time, please choose again")

            pass

        # [1]: Initialize Core Game
        self.gameCore: minesweeper = minesweeper(size=matrixSize, difficulty="Easy")

        # [2]: Building attribute
        self._adjacencyMatrixFourConnection: Optional[np.ndarray] = self.gameCore.adjacencyMatrixFour
        self._adjacencyMatrixEightConnection: Optional[np.ndarray] = self.gameCore.adjacencyMatrixEight

        self.number_of_samples: int = int(numberOfSamples)
        self.random_state: int = randomState
        self.distribution: Dict[int, List] = {i: [key, temp[i], 0] for i, key in enumerate(config.DIFFICULTY.keys())}
        for idx, key in enumerate(self.distribution.keys()):
            if 1 <= idx < len(temp):
                self.distribution[idx][2] = sum(self.distribution[idx - 1][1:])

        self.size: Tuple[int, int] = (self.number_of_samples, self.gameCore.getNumberOfNodes())

        # [3]: Setup object's attribute
        # In sigmoid: 1: bomb --- 0: no bomb
        # In tanh: 1: bomb --- 0: affected location --- -1: no bomb
        self.originalHashedTrainState: np.ndarray = np.zeros(shape=self.size, dtype=np.int8)
        self.adjacencyTrainFourState: Optional[np.ndarray] = None
        self.adjacencyTrainEightState: Optional[np.ndarray] = None
        self.sigmoidTrainResult: np.ndarray = np.zeros(shape=self.size, dtype=np.int8)
        self.tanhTrainResult: np.ndarray = np.zeros(shape=self.size, dtype=np.int8)

        self.originalHashedTestState: Optional[np.ndarray] = None
        self.adjacencyTestFourState: Optional[np.ndarray] = None
        self.adjacencyTestEightState: Optional[np.ndarray] = None
        self.sigmoidTestResult: Optional[np.ndarray] = None
        self.tanhTestResult: Optional[np.ndarray] = None

        # Model State
        self._sigmoidLearning: bool = sigmoidLearning
        self._tanhLearning: bool = tanhLearning
        if sigmoidLearning is True and tanhLearning is True:
            activation: str = input("Choose your learning mode (sigmoid/tanh): ")
            while activation not in ["sigmoid", "tanh"]:
                activation: str = input("Choose your learning mode (sigmoid/tanh): ")
            self._finalActivation: str = activation
        else:
            self._finalActivation: str = "sigmoid" if sigmoidLearning is True else "tanh"
        self._model: Model = self._buildModel()

        self.y_train_pred: Optional[np.ndarray] = None
        self.y_test_pred: Optional[np.ndarray] = None

    def _multiply(self):
        print("=" * 80)
        print("The object is now running matrix multiplication")
        start = time()
        self.adjacencyTrainFourState = np.matmul(self.originalHashedTrainState, self._adjacencyMatrixFourConnection)
        self.adjacencyTrainEightState = np.matmul(self.originalHashedTrainState, self._adjacencyMatrixEightConnection)
        print(f"Executing Time: {round(time() - start, 6)}s")

    def _build(self, minimum_hashing: bool, value: List, verbose: int = 10000, start: float = 0) -> None:
        for i in range(value[2], value[2] + value[1]):
            if i % verbose == 0:
                print("This is the row #{} ---> Executing Time: {:.6f}s".format(i, time() - start))

            self.gameCore.fastReset()
            self.originalHashedTrainState[i] = self.gameCore.getHashingCoreMatrix(minimum_mode=minimum_hashing).ravel()
            self.tanhTrainResult[i], self.sigmoidTrainResult[i] = self.gameCore.searchBombWithActivation(needRavel=True)
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
            print("Executing (Total) Time: {:.6f}s".format(time() - start))

        # [3]: Matrix Multiplication
        print("End Loop: Executing Time: {:.6f}s".format(time() - running_time))
        self._multiply()

    def _buildModel(self) -> Model:
        data_type, activation = np.float32, self._finalActivation

        originalState = Input(shape=(self.size[1],), dtype=np.int8)
        originalTrainState = Dense(units=self.size[1], activation="relu", dtype=data_type)(originalState)
        originalTrainState = Dense(units=self.size[1], activation="relu", dtype=data_type)(originalTrainState)
        originalTrainState = Dense(units=self.size[1], activation=activation, dtype=data_type)(originalTrainState)

        eightState = Input(shape=(self.size[1],), dtype=np.int8)
        eightTrainState = Dense(units=int(8 * self.size[1]), activation="relu", dtype=data_type)(eightState)
        eightTrainState = Dense(units=int(4 * self.size[1]), activation="relu", dtype=data_type)(eightTrainState)
        eightTrainState = Dense(units=self.size[1], activation=activation, dtype=data_type)(eightTrainState)

        fourState = Input(shape=(self.size[1],), dtype=np.int8)
        fourTrainState = Dense(units=int(4 * self.size[1]), activation="relu", dtype=data_type)(fourState)
        fourTrainState = Dense(units=self.size[1], activation="relu", dtype=data_type)(fourTrainState)
        fourTrainState = Dense(units=self.size[1], activation=activation, dtype=data_type)(fourTrainState)

        return Model(inputs=[originalState, fourState, eightState],
                     outputs=Average(dtype=data_type)([originalTrainState, fourTrainState, eightTrainState]))

    def prepare(self, test_size: float = 0.05) -> None:
        fakeState = np.zeros(shape=self.originalHashedTrainState, dtype=np.uint8)

        self.adjacencyTrainFourState, self.adjacencyTestFourState, self.adjacencyTrainEightState, \
        self.adjacencyTestEightState = train_test_split(self.adjacencyTrainFourState, self.adjacencyTrainEightState,
                                                        test_size=test_size, random_state=self.random_state)

        self.sigmoidTrainResult, self.sigmoidTestResult, self.tanhTrainResult, self.tanhTestResult = \
            train_test_split(self.sigmoidTrainResult, self.tanhTrainResult,
                             test_size=test_size, random_state=self.random_state)

        self.originalHashedTrainState, self.originalHashedTestState, fakeState, temp = \
            train_test_split(self.originalHashedTrainState, fakeState,
                             test_size=test_size, random_state=self.random_state)
        del fakeState, temp

    def _pushCallback(self):
        if self.adjacencyTrainEightState.shape != self.adjacencyTrainFourState:
            pass

        callbacks = [EarlyStopping(monitor="val_loss", mode="min", verbose=0, min_delta=0.0025, patience=15),
                     ModelCheckpoint(filepath="model/Best TensorFlow Model for Prediction.h5",
                                     monitor="val_loss", mode="min", verbose=0, save_best_only=True),
                     TerminateOnNaN(), CSVLogger(filename="model/Histogram Profile.h5")]
        return callbacks

    def train(self, trainPath: Optional[str] = None, testPath: Optional[str] = None):
        self._model.compile(optimizer=Adam(learning_rate=0.005), loss="sparse_categorical_crossentropy",
                            metrics="accuracy")
        callbacks = self._pushCallback()
        x_train = [self.originalHashedTrainState, self.adjacencyTrainFourState, self.adjacencyTrainEightState]
        x_test = [self.originalHashedTestState, self.adjacencyTestFourState, self.adjacencyTestEightState]
        if self._finalActivation == "sigmoid":
            y_train, y_test = self.sigmoidTrainResult.view(), self.sigmoidTestResult.view()
        else:
            y_train, y_test = self.tanhTrainResult.view(), self.tanhTestResult.view()

        hist = self._model.fit(x=x_train, y=y_train, batch_size=256, epochs=100, callbacks=callbacks, shuffle=False,
                               validation_data=(x_test, y_test), use_multiprocessing=True, workers=6)

        self.y_train_pred = np.array(self._model.predict(x=x_train, batch_size=256, use_multiprocessing=True,
                                                         workers=6), dtype=np.float32)

        self.y_test_pred = np.array(self._model.predict(x=x_test, batch_size=256, use_multiprocessing=True, workers=6),
                                    dtype=np.float32)

        if self._finalActivation == "sigmoid":
            self.y_train_pred[self.y_train_pred < 0.5] = 0
            self.y_train_pred[self.y_train_pred > 0.5] = 1
            self.y_train_pred = self.y_train_pred.astype(np.int8)

            self.y_test_pred[self.y_test_pred < 0.5] = 0
            self.y_test_pred[self.y_test_pred > 0.5] = 1
            self.y_test_pred = self.y_test_pred.astype(np.int8)
        else:
            self.y_train_pred[(self.y_train_pred < 1 / 3) & (self.y_train_pred > -1 / 3)] = 0
            self.y_train_pred[self.y_train_pred < -1 / 3] = -1
            self.y_train_pred[self.y_train_pred < 1 / 3] = 1
            self.y_train_pred = self.y_train_pred.astype(np.int8)

            self.y_test_pred[(self.y_test_pred < 1 / 3) & (self.y_test_pred > -1 / 3)] = 0
            self.y_test_pred[self.y_test_pred < -1 / 3] = -1
            self.y_test_pred[self.y_test_pred < 1 / 3] = 1
            self.y_test_pred = self.y_test_pred.astype(np.int8)

        if trainPath is not None:
            ExportFile(DataFrame=pd.DataFrame(data=self.y_train_pred, index=None, columns=None),
                       FilePath=trainPath, index=False, index_label=None)

        if testPath is not None:
            ExportFile(DataFrame=pd.DataFrame(data=self.y_test_pred, index=None, columns=None),
                       FilePath=testPath, index=False, index_label=None)

    def saveTest(self, originalFilePath: Optional[str] = None, fourStateFilePath: Optional[str] = None,
                 eightStateFilePath: Optional[str] = None, tanhFilePath: Optional[str] = None,
                 sigmoidFilePath: Optional[str] = None) -> None:

        if originalFilePath is not None:
            ExportFile(DataFrame=pd.DataFrame(data=self.originalHashedTestState, index=None, columns=None),
                       FilePath=originalFilePath, index=False, index_label=None)

        if fourStateFilePath is not None:
            ExportFile(DataFrame=pd.DataFrame(data=self.adjacencyTestFourState, index=None, columns=None),
                       FilePath=fourStateFilePath, index=False, index_label=None)

        if eightStateFilePath is not None:
            ExportFile(DataFrame=pd.DataFrame(data=self.adjacencyTestEightState, index=None, columns=None),
                       FilePath=eightStateFilePath, index=False, index_label=None)

        if tanhFilePath is not None:
            ExportFile(DataFrame=pd.DataFrame(data=self.tanhTestResult, index=None, columns=None),
                       FilePath=tanhFilePath, index=False, index_label=None)

        if sigmoidFilePath is not None:
            ExportFile(DataFrame=pd.DataFrame(data=self.sigmoidTestResult, index=None, columns=None),
                       FilePath=sigmoidFilePath, index=False, index_label=None)
        return None

    def loadTest(self, originalFilePath: Optional[str] = None, fourStateFilePath: Optional[str] = None,
                 eightStateFilePath: Optional[str] = None, tanhFilePath: Optional[str] = None,
                 sigmoidFilePath: Optional[str] = None) -> None:

        if originalFilePath is not None:
            self.originalHashedTestState = ReadFile(FilePath=originalFilePath, header=None, get_values=True,
                                                     dtype=np.int8)

        if fourStateFilePath is not None:
            self.adjacencyTestFourState = ReadFile(FilePath=fourStateFilePath, header=None, get_values=True,
                                                    dtype=np.int8)

        if eightStateFilePath is not None:
            self.adjacencyTestEightState = ReadFile(FilePath=eightStateFilePath, header=None, get_values=True,
                                                     dtype=np.int8)

        if tanhFilePath is not None:
            self.tanhTestResult = ReadFile(FilePath=tanhFilePath, header=None, get_values=True, dtype=np.int8)

        if sigmoidFilePath is not None:
            self.sigmoidTestResult = ReadFile(FilePath=sigmoidFilePath, header=None, get_values=True, dtype=np.int8)

        return None

    def saveTrain(self, originalFilePath: Optional[str] = None, fourStateFilePath: Optional[str] = None,
                  eightStateFilePath: Optional[str] = None, tanhFilePath: Optional[str] = None,
                  sigmoidFilePath: Optional[str] = None) -> None:

        if originalFilePath is not None:
            ExportFile(DataFrame=pd.DataFrame(data=self.originalHashedTrainState, index=None, columns=None),
                       FilePath=originalFilePath, index=False, index_label=None)

        if fourStateFilePath is not None:
            ExportFile(DataFrame=pd.DataFrame(data=self.adjacencyTrainFourState, index=None, columns=None),
                       FilePath=fourStateFilePath, index=False, index_label=None)

        if eightStateFilePath is not None:
            ExportFile(DataFrame=pd.DataFrame(data=self.adjacencyTrainEightState, index=None, columns=None),
                       FilePath=eightStateFilePath, index=False, index_label=None)

        if tanhFilePath is not None:
            ExportFile(DataFrame=pd.DataFrame(data=self.tanhTrainResult, index=None, columns=None),
                       FilePath=tanhFilePath, index=False, index_label=None)

        if sigmoidFilePath is not None:
            ExportFile(DataFrame=pd.DataFrame(data=self.sigmoidTrainResult, index=None, columns=None),
                       FilePath=sigmoidFilePath, index=False, index_label=None)
        return None

    def loadTrain(self, originalFilePath: Optional[str] = None, fourStateFilePath: Optional[str] = None,
                  eightStateFilePath: Optional[str] = None, tanhFilePath: Optional[str] = None,
                  sigmoidFilePath: Optional[str] = None) -> None:

        if originalFilePath is not None:
            self.originalHashedTrainState = ReadFile(FilePath=originalFilePath, header=0, get_values=True,
                                                     dtype=np.int8)

        if fourStateFilePath is not None:
            self.adjacencyTrainFourState = ReadFile(FilePath=fourStateFilePath, header=0, get_values=True,
                                                    dtype=np.int8)

        if eightStateFilePath is not None:
            self.adjacencyTrainEightState = ReadFile(FilePath=eightStateFilePath, header=0, get_values=True,
                                                     dtype=np.int8)

        if tanhFilePath is not None:
            self.tanhTrainResult = ReadFile(FilePath=tanhFilePath, header=None, get_values=0, dtype=np.int8)

        if sigmoidFilePath is not None:
            self.sigmoidTrainResult = ReadFile(FilePath=sigmoidFilePath, header=None, get_values=0, dtype=np.int8)

        return None
