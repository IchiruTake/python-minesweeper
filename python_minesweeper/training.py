from deep_learning import LearningModel


def train(samples: int = int(2e6), verbose: int = 10000):
    Learn = LearningModel(folder="model/", matrixSize=8, numberOfSamples=samples, sigmoidLearning=True,
                          tanhLearning=False, easyRatio=0.7, mediumRatio=0.15, hardRatio=0.1, extremeRatio=0.05)
    Learn.build(minimum_hashing=False, verbose=verbose)
    Learn.prepare(test_size=0.05)
    Learn.train(trainPath="model/Train Prediction.csv", testPath="model/Test Prediction.csv")


if __name__ == "__main__":
    train(samples=100000, verbose=5000)
