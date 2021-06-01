from deep_learning import LearningModel

if __name__ == "__main__":
    Learn = LearningModel(folder="model/", matrixSize=8, numberOfSamples=int(2e6), sigmoidLearning=True,
                          tanhLearning=False, easyRatio=0.7, mediumRatio=0.15, hardRatio=0.1, extremeRatio=0.05)
    Learn.build(minimum_hashing=False, verbose=10000)
    Learn.prepare(test_size=0.05)
    Learn.train(trainPath="model/Train Prediction.csv", testPath="model/Test Prediction.csv")
