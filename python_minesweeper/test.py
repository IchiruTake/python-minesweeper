from interface import GameWindow
from PyQt5.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = GameWindow()
    demo.update()
    demo.showMaximized()
    sys.exit(app.exec_())
