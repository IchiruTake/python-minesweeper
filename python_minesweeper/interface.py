import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyautogui
import time
import keyboard
import ctypes
import config

class EnableClickLabel(QLabel):
    clicked = pyqtSignal()
    def mouseReleaseEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            self.clicked.emit()

class MainWindow(QMainWindow, QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()
    
    def addPicture(self, x, y):
        self.tile = QLabel(self)
        self.tile.setScaledContents(True)
        self.tile.setPixmap(QPixmap(config.element_address["background_unbordered"]))
        self.tile.setGeometry(x, y, self.imageSize, self.imageSize)
        self.tile.show()

    def getIndex(self):
        print("Clicked")

    def showWelcomeScreen(self):
        self.background = QLabel(self)
        self.background.setScaledContents(True)
        self.background.setPixmap(QPixmap(config.mainscreen_image_address["welcome_screen_background"]))
        self.background.setGeometry(0, 0, config.mainscreen_image_address["size"][0], config.mainscreen_image_address["size"][1])
        
        self.game_name = QLabel(self)
        self.game_name.setScaledContents(True)
        self.game_name.setText("Minesweeper")
        self.game_name.setGeometry(860, 100, 140, 40)
        self.game_name.setStyleSheet("background-color : rgb(255,255,255);")

        self.start_button = QPushButton(self)
        self.start_button.setText("~ Click to start ~")
        self.start_button.setStyleSheet("background-color : rgb(255,255,255);")
        self.start_button.setGeometry(860, 800, 250, 60)
        self.start_button.clicked.connect(self.startGame)

    def makeTranslucent(self):
        self.overlay = QLabel(self)
        self.overlay.setScaledContents(True)
        self.overlay.setPixmap(QPixmap(config.mainscreen_image_address["translucent"]))
        self.overlay.setGeometry(0, 0, config.mainscreen_image_address["size"][0], config.mainscreen_image_address["size"][1])
        self.overlay.show()

    def showBoard(self):
        for i in range(0, 15):
            for j in range(0, 15):
                toa_do_x, toa_do_y =config.getTilePos(i, j)
                self.addPicture(toa_do_x, toa_do_y)

    def detectClick(self, button, watchtime = 20): #functional, but not using QLabel
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
        self.imageSize = config.number["size"]
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowTitle("Minesweeper")
        self.setWindowFlags(Qt.FramelessWindowHint) #to hide title bar for full screen ratio
        self.showWelcomeScreen()
        self.showMaximized()
    
    def startGame(self):
        self.background.hide()
        self.game_name.hide()
        self.start_button.hide()
        self.makeTranslucent()
        self.showBoard()
        

app=QApplication(sys.argv)
window=MainWindow()
window.show()
sys.exit(app.exec_())