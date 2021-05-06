from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyautogui
import ctypes
import time
import keyboard
import sys

#board-border=30 for each side
#each tile is a square of 68*68
#need to resize image to 66

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.boardArrayX=[]
        self.boardArrayY=[]
        self.boardSize=15 #15*15 tiles
        self.start=30 #đường viền cho mỗi cạnh của board (board hình vuông) là 30px
        self.imageSize=65
        self.windowSize=[1920, 1080]
        self.initUI()

    def initPositionArray(self):
        for i in range(0, 15):
            self.boardArrayX.append(self.start+68*i)
        for j in range(0, 15):
            self.boardArrayY.append(self.start+68*j)
    
    def addPicture(self, x, y):
        self.tile = QLabel(self)
        self.tile.setScaledContents(True)
        self.tile.setPixmap(QPixmap(".../resources/images/background_unbordered.png"))
        self.tile.setGeometry(x, y, self.imageSize, self.imageSize)

    def showWelcomeScreen(self):
        self.background = QLabel(self)
        self.background.setScaledContents(True)
        self.background.setPixmap(QPixmap(".../resources/images/welcome_screen_background.png"))
        self.background.setGeometry(0, 0, self.windowSize[0], self.windowSize[1])
        
        self.text = QLabel(self)
        self.text.setScaledContents(True)
        self.text.setText("- Click to start -")
        self.text.setGeometry(660, 800, 100, 20)

    def makeTranslucent(self):
        self.overlay = QLabel(self)
        self.overlay.setScaledContents(True)
        self.overlay.setPixmap(QPixmap(".../resources/images/translucent_overlay.png"))
        self.overlay.setGeometry(0, 0, self.windowSize[0], self.windowSize[1])

    def showBoard(self):
        for i in range(0, 15):
            for j in range(0, 15):
                self.addPicture(self.boardArrayX[i], self.boardArrayY[j])

    def detectClick(self, button, watchtime = 20):
        if button in (1, '1', 'l', 'L', 'left', 'Left', 'LEFT'):
            self.bnum = 0x01
        elif button in (2, '2', 'r', 'R', 'right', 'Right', 'RIGHT'):
            self.bnum = 0x02
        start = time.time()
        while 1:
            if ctypes.windll.user32.GetKeyState(self.bnum) not in [0, 1]:
                return True
            elif time.time() - start >= watchtime:
                break
            time.sleep(0.001)
        return False
    
    def initUI(self):
        self.setWindowTitle("Minesweeper")
        self.setGeometry(0, 0, self.windowSize[0], self.windowSize[1])
        self.initPositionArray()
        self.showWelcomeScreen()
        if(self.detectClick("L") == True):
            self.makeTranslucent()
            self.showBoard()
        

if __name__ == "main":
    app=QApplication(sys.argv)
    window=MainWindow()
    window.show()
    app.exec_()