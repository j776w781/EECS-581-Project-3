'''
Name: main.py

Authors: Joshua Welicky, Gavin Billinger, Mark Kitchin, Bisshoy Bhattacharjee, Max Biundo

Description: Menu GUI for the program. Calls on switching between all game GUIS.

Inputs: none
Outputs: Menu GUI.
'''
from PyQt6.QtCore import pyqtSignal, QTimer
from PyQt6.QtWidgets import QWidget, QMessageBox
from .ui.menu_ui import Ui_MenuScreen

class MenuScreen(QWidget):
	# SIGNALS
	app_exit = pyqtSignal()
	switch_to_blackjack = pyqtSignal()
	switch_to_roulette = pyqtSignal()
	switch_to_poker = pyqtSignal()
	switch_to_sabacc = pyqtSignal()

	def __init__(self, state, parent=None):
		super().__init__(parent)
		self.ui = Ui_MenuScreen()
		self.ui.setupUi(self)
		self.state = state
		self.ui.bankLabel.setText(f"Chip Total: {self.state.chips}")

		self.ui.blackjackButton.clicked.connect(self.blackjack)
		self.ui.rouletteButton.clicked.connect(self.roulette)
		self.ui.pokerButton.clicked.connect(self.poker)
		self.ui.sabaccButton.clicked.connect(self.sabacc)
		self.ui.exitButton.clicked.connect(self.exit)

		QTimer.singleShot(0, self.showWelcomeMessage)
	
	#Displays introductory message.
	def showWelcomeMessage(self):
		QMessageBox.information(
            self,
            "Welcome to the StakeFree Casino!",
			f"Welcome to the StakeFree Casino!\nAs a gift, you've been given {self.state.chips} chips!\nTry not to spend them all in one place ;)"
        )

	#Switches to blackjack
	def blackjack(self):
		print("Blackjack clicked!")
		if self.state.chips == 0:
			QMessageBox.information(self, "Out", "You don't have any chips!\nCome back when you have more!")
		else:
			self.switch_to_blackjack.emit()

	#Switches to roulette.
	def roulette(self):
		print("Roulette clicked!")
		if self.state.chips == 0:
			QMessageBox.information(self, "Out", "You don't have any chips!\nCome back when you have more!")
		else:
			self.switch_to_roulette.emit()

	#Switches to poker
	def poker(self):
		print("Poker clicked!")
		if self.state.chips == 0:
			QMessageBox.information(self, "Out", "You don't have any chips!\nCome back when you have more!")
		else:
			self.switch_to_poker.emit()

	#switches to sabacc
	def sabacc(self):
		print("Sabacc clicked!")
		if self.state.chips == 0:
			QMessageBox.information(self, "Out", "You don't have any chips!\nCome back when you have more!")
		else:
			self.switch_to_sabacc.emit()

	#exits the program.
	def exit(self):
		self.app_exit.emit()
