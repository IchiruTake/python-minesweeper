from core import minesweeper
from deep_learning import LearningModel
from preprocessing import object_memory_profiler

if __name__ == "__main__":
    # game = minesweeper(16, "Medium")
    # print(game.displayCoreMatrix())
    # print(game.displayBetterHashedCoreMatrix(minimum_mode=False))
    # print(game.searchBombWithActivation(needRavel=True))
    Learn = LearningModel(numberOfSamples=int(5e4), easyRatio=0.55, mediumRatio=0.2, hardRatio=0.15, extremeRatio=0.1)
    Learn.build(minimum_hashing=False, verbose=5000)
