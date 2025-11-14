'''
Name: main.py

Authors: Joshua Welicky, Gavin Billinger, Mark Kitchin, Bisshoy Bhattacharjee, Max Biundo

Description: Main skeleton for the program. Facilitates switching between all GUI elements.
'''

from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt6.QtGui import QFontDatabase, QFont
import os
import sys
sys.dont_write_bytecode = True

from games.menu import MenuScreen
from games.state.gamestate import GameState
from games.blackjack import BlackJackScreen
from games.roulette import RouletteScreen
from games.poker import PokerScreen
from games.sabaac import SabaccScreen

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setFixedSize(800, 600)
        self.setStyleSheet("""
            background-color: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #009f00,
                stop:1 #004d00
            );
        """)

        self.state = GameState()
        
        #Stores the GUI screens.
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.menu = MenuScreen(self.state, parent=self)
        self.blackjack = BlackJackScreen(self.state, parent=self)
        self.roulette = RouletteScreen(self.state, parent=self)
        self.poker = PokerScreen(self.state, parent=self)
        self.sabacc = SabaccScreen(self.state, parent=self)

        self.stack.addWidget(self.menu)
        self.stack.addWidget(self.blackjack)
        self.stack.addWidget(self.roulette)
        self.stack.addWidget(self.poker)
        self.stack.addWidget(self.sabacc)

        self.menu.switch_to_blackjack.connect(self.show_blackjack_screen)
        self.menu.switch_to_roulette.connect(self.show_roulette_screen)
        self.menu.switch_to_poker.connect(self.show_poker_screen)
        self.menu.switch_to_sabacc.connect(self.show_sabacc_screen)
        self.menu.app_exit.connect(self.close)

        self.blackjack.switch_to_menu.connect(self.show_menu_screen)
        self.roulette.switch_to_menu.connect(self.show_menu_screen)
        self.poker.switch_to_menu.connect(self.show_menu_screen)
        self.sabacc.switch_to_menu.connect(self.show_menu_screen)

    # Switch to blackjack
    def show_blackjack_screen(self):
        self.blackjack.ui.chipsNum.setText(f"Chip Total: {self.state.chips}")
        self.stack.setCurrentWidget(self.blackjack)
    
    # Switch to roulette
    def show_roulette_screen(self):
        self.roulette.ui.totalLabel.setText(f"Chip Total: {self.state.chips}")
        self.stack.setCurrentWidget(self.roulette)

    # Switch to poker
    def show_poker_screen(self):
        self.poker.ui.totalLabel.setText(f"Chip Total: {self.state.chips}")
        self.stack.setCurrentWidget(self.poker)

    # Switch to sabacc
    def show_sabacc_screen(self):
        self.poker.ui.totalLabel.setText(f"Chip Total: {self.state.chips}")
        self.stack.setCurrentWidget(self.sabacc)

    # Switch to menu
    def show_menu_screen(self):
        self.menu.ui.bankLabel.setText(f"Chip Total: {self.state.chips}")
        self.stack.setCurrentWidget(self.menu)
        if self.state.chips == 0:
            QMessageBox.information(
            self,
            "Game Over",
			"Seriously? You're out? Then you're out!"
            )
            app.exit()


if __name__ == "__main__":
    app = QApplication([])
    fonts = ["BROADW", "HARLOWSI", "MAGNETOB", "BROADWFILLED"]
    # --- FONT LOADING SECTION ---
    for f in fonts:
        base_dir = os.path.dirname(__file__)
        font_path = os.path.join(base_dir, "assets", "fonts", f"{f}.TTF")
        font_id = QFontDatabase.addApplicationFont(font_path)
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        if font_families:
            #app.setFont(QFont(font_families[0]))
            print(f"Loaded custom font: {font_families[0]}")
        else:
            print("Font loaded but no families found.")
    window = MainWindow()
    window.show()
    app.exec()
