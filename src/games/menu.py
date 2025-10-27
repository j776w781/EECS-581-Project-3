'''
Name: main.py

Authors: Joshua Welicky, Gavin Billinger, Mark Kitchin, Bisshoy Bhattacharjee, Max Biundo

Description: Menu GUI for the program. Calls on switching between all game GUIS.

Inputs: none
Outputs: Menu GUI.
'''
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

	#Switches to blackjack
	def blackjack(self):
		print("Blackjack clicked!")
		self.switch_to_blackjack.emit()

	#Switches to roulette.
	def roulette(self):
		print("Roulette clicked!")

	#Switches to poker
	def poker(self):
		print("Poker clicked!")

	#switches to sabacc
	def sabacc(self):
		print("Sabacc clicked!")

	#exits the program.
	def exit(self):
		self.app_exit.emit()
