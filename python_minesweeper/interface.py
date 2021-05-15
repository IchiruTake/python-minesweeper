from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import time
import ctypes
import config
import numpy as np
import keyboard
import random
import ray

#ray.init()

class EnableClickLabel(QLabel):
    isClicked = pyqtSignal()
    def mouseReleaseEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            self.isClicked.emit()

class MainWindow(QMainWindow, QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()
        self.arr = np.ndarray((254,), dtype=np.object_)
        self.array = []
        self.IClick = 0
        isClicked = pyqtSignal()

    def initUI(self):
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowTitle("Minesweeper") #omittable
        self.setWindowFlags(Qt.FramelessWindowHint) #to hide title bar for full screen ratio
        self.showWelcomeScreen()
        self.showMaximized()

    def showWelcomeScreen(self):
        self.background = QLabel(self)
        self.background.setScaledContents(True)
        self.background.setPixmap(QPixmap(config.MAINSCREEN_IMAGE_ADDRESS["welcome_screen_background"]))
        self.background.setGeometry(0, 0, config.MAINSCREEN_IMAGE_ADDRESS["size"][0], config.MAINSCREEN_IMAGE_ADDRESS["size"][1])
        
        self.game_name = QLabel(self)
        self.game_name.setScaledContents(True)
        self.game_name.setPixmap(QPixmap(config.MAINSCREEN_IMAGE_ADDRESS["game_name"]))
        self.game_name.setGeometry(0, 50, config.MAINSCREEN_IMAGE_ADDRESS["size"][0], 240)

        self.input_box = QLineEdit(self)
        self.input_box.setFont(QFont('Times', 16))
        self.input_box.setGeometry(920, 600, 80, 40)

        self.start_button = QPushButton(self)
        self.start_button.setFont(QFont('Times', 16))
        self.start_button.setText("~ Click to start ~")
        self.start_button.setStyleSheet("background-color : #A9A9A9;")
        self.start_button.setGeometry(840, 800, 250, 60)
        self.start_button.clicked.connect(self.startGame)

    def startGame(self):
        #Khi nhấn nút start thì thực hiện các hàm sau
        self.number_of_tile = self.input_box.text() or "15"
        if int(self.number_of_tile) < 4:
            self.temp = QMessageBox(self, text="Minimum size is 4\nAuto set size=4")
            self.temp.show()
            self.number_of_tile = "3"
        self.number_of_tile = int(self.number_of_tile)
        self.background.hide()
        self.game_name.hide()
        self.start_button.hide()
        self.makeTranslucent()
        self.showBoard(self.number_of_tile)
        #ray.get([self.showClock.remote(self), self.showBoard.remote(self.number_of_tile)]) #run parallel
        #ray.close()

    def makeTranslucent(self):
        #display background ingame
        self.overlay = QLabel(self)
        self.overlay.setScaledContents(True)
        self.overlay.setPixmap(QPixmap(config.MAINSCREEN_IMAGE_ADDRESS["translucent"]))
        self.overlay.setGeometry(0, 0, config.MAINSCREEN_IMAGE_ADDRESS["size"][0], config.MAINSCREEN_IMAGE_ADDRESS["size"][1])
        self.overlay.show()

    #@ray.remote
    def showBoard(self, number_of_tile: int):
        #tính toán các biến để display các ô
        tile_size: int = config.getTileSize((number_of_tile))

        for i in range(0, number_of_tile):
            for j in range(0, number_of_tile):
                index = i * number_of_tile + j
                toa_do_y, toa_do_x =config.getTilePos(i, j, tile_size)
                self.addPicture(round(toa_do_x), round(toa_do_y), tile_size, index)
    
    def addPicture(self, x: int, y: int, tile_size: int, index: int): #x&y is position on the screen
        #display các ô (clickable)
        self.tile = EnableClickLabel(self)
        self.tile.setScaledContents(True)
        self.tile.setPixmap(QPixmap(config.ELEMENT_ADDRESS["background_unbordered"]))
        self.tile.setGeometry(x, y, tile_size, tile_size)
        self.tile.isClicked.connect(lambda: self.afterClicked(index, x, y, tile_size))
        self.tile.show()
        np.append(self.arr, self.tile)
        self.array.append(self.tile)

    def afterClicked(self, index, x=0, y=0, tile_size=65): #x, y, tile_size are not needed
        self.changeTileColor(index, tile_size)
        self.IClick += 1
        return index

    def changeTileColor(self, index, tile_size):
        x, y = config.getXYfromIndex(index, tile_size, self.number_of_tile) #don't need this line
        self.array[index].setPixmap(QPixmap(config.ELEMENT_ADDRESS["clicked_unbordered"]))
        self.array[index].show()

    #sửa hàm này để lấy value thực. 0<>1 hoặc true<>false hoặc "win"<>"lose". Nhớ sửa lại cho tương ứng trong hàm endGame
    def getResult(self):
        if random.randint(0, 5) > 3:
            return True
        return False

    #Gọi hàm endGame khi đã mở/flag tất cả các ô, hoặc click trúng bomb
    def endGame(self):
        self.result:bool = self.getResult()

        self.result_background=QLabel(self)
        self.result_background.setScaledContents(True)
        self.result_background.setPixmap(QPixmap(config.MAINSCREEN_IMAGE_ADDRESS["translucent_overlay"]))
        self.result_background.setGeometry(0, 0, 1920, 1080)
        self.result_background.show()

        self.result_text=QLabel(self)
        self.result_text.setScaledContents(True)
        self.result_text.setFont(QFont("Times", 57))
        self.result_text.setStyleSheet("background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #DEB887, stop: 1 #A9A9A9);")
        self.result_text.setAlignment(Qt.AlignCenter)
        self.result_text.setGeometry(745, 300, 450, 140)

        if self.result == True:
            self.result_text.setText("You win")
        else:
            self.result_text.setText("You lose")

        self.result_text.show()

    #@ray.remote
    def showClock(self):
        self.second=0
        self.minute=0
        self.clock=QLabel(self)
        self.clock.setFont(QFont('Times', 14))
        self.clock.setScaledContents(True)
        self.clock.setText("00:00")
        self.clock.setGeometry(1600, 200, 80, 50)
        self.clock.show()

        while self.minute < 60:
            time.sleep(1)
            self.second+=1
            if self.second >= 60:
                self.minute+=1
                self.second=0
            self.temp = str(self.minute)+":"+str(self.second)
            self.clock.setText(self.temp)
            self.clock.show()

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


app=QApplication(sys.argv)
window=MainWindow()
window.show()
if keyboard.is_pressed("Esc"):
    window=MainWindow()
    window.show()
sys.exit(app.exec_())