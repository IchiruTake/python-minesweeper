import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyautogui
import time
import keyboard
import ctypes


#board-border=30 for each side
#each tile is a square of 68*68
#need to resize image to 66

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()
    
    def addPicture(self, x, y):
        self.tile = QLabel(self)
        self.tile.setScaledContents(True)
        self.tile.setPixmap(QPixmap("E:\minesweeper project/python_minesweeper/python_minesweeper/resources/images/background_unbordered.png"))
        self.tile.setGeometry(x, y, self.imageSize, self.imageSize)
        self.tile.show()

    def showWelcomeScreen(self):
        self.background = QLabel(self)
        self.background.setScaledContents(True)
        self.background.setPixmap(QPixmap("E:\minesweeper project/python_minesweeper/python_minesweeper/resources/images/welcome_screen_background.png"))
        self.background.setGeometry(0, 0, 1920, 1080)
        
        self.start_button = QPushButton(self)
        self.start_button.setText("~ Click to start ~")
        self.start_button.setStyleSheet("background-color : rgb(255,255,255);")
        self.start_button.setGeometry(860, 800, 250, 60)
        self.start_button.clicked.connect(self.startGame)

    def makeTranslucent(self):
        self.overlay = QLabel(self)
        self.overlay.setScaledContents(True)
        self.overlay.setPixmap(QPixmap("E:\minesweeper project/python_minesweeper/python_minesweeper/resources/images/translucent.png"))
        self.overlay.setGeometry(0, 0, 1920, 1080)
        self.overlay.show()

    def showBoard(self):
        for i in range(0, 15):
            for j in range(0, 15):
                self.addPicture(30+68*i, 30+68*j)

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
        self.imageSize = 65
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowTitle("Minesweeper")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showWelcomeScreen()
        self.showMaximized()
    
    def startGame(self):
        self.makeTranslucent()
        self.showBoard()
        

app=QApplication(sys.argv)
window=MainWindow()
window.show()
sys.exit(app.exec_())