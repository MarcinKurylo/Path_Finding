import sys
from src.gui import MyWindow
from PyQt5.QtWidgets import QApplication


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    w = MyWindow()
    w.show()
    app.exit(app.exec_())