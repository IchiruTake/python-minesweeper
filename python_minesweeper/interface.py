from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import time
import ctypes
import config
import numpy as np
import keyboard

class EnableClickLabel(QLabel):
    isClicked = pyqtSignal()
    def mouseReleaseEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            self.isClicked.emit()

class MainWindow(QMainWindow, QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()
        text = ""
        self.arr = np.array([], dtype=np.object_)
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
        self.background.setPixmap(QPixmap(config.mainscreen_image_address["welcome_screen_background"]))
        self.background.setGeometry(0, 0, config.mainscreen_image_address["size"][0], config.mainscreen_image_address["size"][1])
        
        self.game_name = QLabel(self)
        self.game_name.setScaledContents(True)
        self.game_name.setPixmap(QPixmap(config.mainscreen_image_address["game_name"]))
        self.game_name.setGeometry(0, 50, config.mainscreen_image_address["size"][0], 240)

        self.input_box = QLineEdit(self)
        self.input_box.setGeometry(920, 600, 80, 40)

        self.start_button = QPushButton(self)
        self.start_button.setText("~ Click to start ~")
        self.start_button.setStyleSheet("background-color : rgb(255,255,255);")
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

    def makeTranslucent(self):
        #display background ingame
        self.overlay = QLabel(self)
        self.overlay.setScaledContents(True)
        self.overlay.setPixmap(QPixmap(config.mainscreen_image_address["translucent"]))
        self.overlay.setGeometry(0, 0, config.mainscreen_image_address["size"][0], config.mainscreen_image_address["size"][1])
        self.overlay.show()

    def showBoard(self, number_of_tile: int):
        #tính toán các biến để display các ô
        tile_size: int = config.getTileSize((number_of_tile))

        for i in range(0, number_of_tile):
            for j in range(0, number_of_tile):
                toa_do_x, toa_do_y =config.getTilePos(i, j, tile_size)
                self.addPicture(round(toa_do_x), round(toa_do_y), tile_size)

        if keyboard.is_pressed("Esc"):
            self.initUI()
    
    def addPicture(self, x: int, y: int, tile_size: int): #x&y is position on the screen
        #display các ô (clickable)
        self.tile = EnableClickLabel(self)
        self.tile.setScaledContents(True)
        self.tile.setPixmap(QPixmap(config.element_address["background_unbordered"]))
        self.tile.setGeometry(x, y, tile_size, tile_size)
        self.tile.isClicked.connect(lambda: self.afterClicked(x, y, tile_size))
        self.tile.show()
        np.append([self.tile], int((x-30)/tile_size + int(self.number_of_tile)*(y-30)/tile_size)) #convert to index using in-array index formula

    def afterClicked(self, x, y, tile_size):
        self.changeTileColor(x, y, tile_size)
        print("index: ", self.getIndex(x, y))
        return self.getIndex(x, y)

    def changeTileColor(self, x, y, tile_size):
        self.tile = QLabel(self)
        self.tile.setPixmap(QPixmap(config.element_address["clicked_unbordered"]))
        self.tile.setGeometry(x, y, tile_size, tile_size)
        self.tile.show()

    def getIndex(self, x=0, y=0) -> str: #theo yêu cầu của záo xư
        return str(abs(int((x-30)/68 +15*(y-30)/68)))

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
sys.exit(app.exec_())