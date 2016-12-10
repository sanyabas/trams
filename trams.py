from PyQt5.QtWidgets import QApplication
from gui import *


def main():
    app = QApplication([])
    widget = MainWidget()
    widget.show()
    app.exec_()


if __name__ == '__main__':
    main()
