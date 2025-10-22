from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget
from .ui.menu_ui import Ui_MenuScreen

class MenuScreen(QWidget):
	# SIGNALS
	app_exit = pyqtSignal()
	switch_to_blackjack = pyqtSignal()

	def __init__(self, parent=None):
		super().__init__(parent)
		self.ui = Ui_MenuScreen()
		self.ui.setupUi(self)

		self.ui.blackjackButton.clicked.connect(self.blackjack)
		self.ui.rouletteButton.clicked.connect(self.roulette)
		self.ui.pokerButton.clicked.connect(self.poker)
		self.ui.sabaccButton.clicked.connect(self.sabacc)

		self.ui.exitButton.clicked.connect(self.exit)

	def blackjack(self):
		print("Blackjack clicked!")
		self.switch_to_blackjack.emit()

	def roulette(self):
		print("Roulette clicked!")

	def poker(self):
		print("Poker clicked!")

	def sabacc(self):
		print("Sabacc clicked!")

	def exit(self):
		self.app_exit.emit()
