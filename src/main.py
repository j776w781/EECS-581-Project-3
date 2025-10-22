from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from games.menu import MenuScreen
from games.blackjack import BlackJackScreen

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()

		self.setFixedSize(800, 600)
		self.setStyleSheet("background-color: qlineargradient(\n"
"    x1:0, y1:0, x2:0, y2:1,\n"
"    stop:0 #009f00,\n"
"    stop:1 #004d00\n"
");\n"
"")
	
		self.stack = QStackedWidget()
		self.setCentralWidget(self.stack)
		
		self.menu = MenuScreen(parent=self)
		self.blackjack = BlackJackScreen(parent=self)
	
		self.stack.addWidget(self.menu)
		self.stack.addWidget(self.blackjack)

		self.menu.switch_to_blackjack.connect(self.show_blackjack_screen)
		self.menu.app_exit.connect(self.close)

	def show_blackjack_screen(self):
		self.stack.setCurrentWidget(self.blackjack)

	def show_menu_screen(self):
		self.stack.setCurrentWidget(self.menu)

if __name__ == "__main__":
	app = QApplication([])
	window = MainWindow()
	window.show()
	app.exec()
