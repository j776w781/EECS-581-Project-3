import sys
import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontDatabase, QPalette, QBrush, QPixmap
from PySide6 import QtWidgets


class MyGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Digital Casino!")
        self.resize(400, 600)
        self.layout = QtWidgets.QVBoxLayout()

        script_dir = os.path.dirname(os.path.abspath(__file__))
        texture = QPixmap(os.path.join(script_dir, "assets", "casino-texture.jpg"))
        chip = os.path.join(script_dir, "assets", "chip.png")

        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

		# Draw background texture.
        palette = QPalette()
        texture = QPixmap(texture)
        palette.setBrush(QPalette.Window, QBrush(texture))
        self.setPalette(palette)

        self.createTitle()
        
        self.chip = QtWidgets.QLabel(self)
        pixmap = QPixmap(chip)
        self.chip.setPixmap(pixmap)
        self.chip.setAttribute(Qt.WA_TranslucentBackground)
        self.chip.resize(400, 400)
        self.chip.move(250, 150)
        self.chip.show()

    def createTitle(self):
        label = QtWidgets.QLabel("Welcome to the Digital Casino!!!")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(script_dir, "assets", "BroadwayGradient3D.ttf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        family = QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QFont(family, 32)
        label.setFont(font)
        label.setStyleSheet("color: gold; font-size: 60px;")

        self.layout.addWidget(label)
        self.layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.central_widget.setLayout(self.layout)

if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	window = MyGUI()
	window.show()
	sys.exit(app.exec())