from PyQt6.QtWidgets import QWidget, QGraphicsScene, QGraphicsObject, QPushButton, QMessageBox
from PyQt6.QtCore import QPropertyAnimation, QPointF, QEasingCurve, QRectF, pyqtProperty, QTimer, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QColor
from .ui.roulette_ui import Ui_RouletteScreen
from .objects.table import Number, Table, Wheel
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TABLE_DIR = os.path.join(BASE_DIR, "../assets/table.jpg")
WHEEL_DIR = os.path.join(BASE_DIR, "../assets/wheel.png")

class RouletteScreen(QWidget):
    switch_to_menu = pyqtSignal()

    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.ui = Ui_RouletteScreen()
        self.ui.setupUi(self)
        self.ui.tableLabel.setPixmap(QPixmap(TABLE_DIR))
        self.ui.wheelLabel.setPixmap(QPixmap(WHEEL_DIR))
        self.state = state
        self.game = Roulette(self.state.chips)

        self.ui.totalLabel.setText(f"Your Total: {self.state.chips}")

        #TEMPLATE FOR BUTTON CONNECTIONS
        #Assumes the user has clicked the 3 space, placing a bet on 3.
        #SINGLE NUMBER betcode should be of the form s_#, where s stands for single, # is the actual betting number.
        #Pairs: p_#_#
        #Triples: tr_#_#_#
        #Quads: q_#_#_#_#
        #Rows: r_# (Row 1 is 1, 2, 3)
        #Row Pair: rp_#_# (# are row numbers)
        #Col: c_# (Col 1 is the one with 1)
        #Twelves: tw_#
        #Halves: h_#
        #Red/black: rd/b
        #Even/Odd: e/o
        #Code to put:
        #self.ui.centerThree.clicked.connect(lambda: self.game.apply_bet("s_3"))

    #Wrapper for adding a bet to the game logic. Simply passes it to the appropriate Roulette method.
    def apply_bet(self, betcode, chipamount=50):
        #Passes the betcode and chipamount to the Roulette class, which will record the bet for a possible payout.
        self.game.add_bet(betcode, chipamount)
        #Removes the chips from the user's balance. Does not immediately kick them out.
        self.state.chips = self.state.chips-chipamount

class Roulette:
    def __init__(self, chips):
        self.chips = chips
        self.table = Table()
        self.wheel = Wheel()
        self.bets = []
        self.result = 0


    def add_bet(bet_code, chips_bet):
        #Don't worry about this. Just send me your bets and I'll be implemented later.
        return

    def insideBet(self):
        # Input with error handling for roulette number.
        i = 0
        while i == 0:
            try:
                num = int(input("\nPick a number to bet on: "))
                if num < 0 or num > 36:
                    raise
                num = Number(num)
                i = 1
            except:
                i = 0

        # Input with error handling for bet amount.
        i = 0
        while i == 0:
            try:
                print("\nChip total:", self.chips)
                bet = int(input("How much will you bet?: "))
                if bet > self.chips or bet < 0:
                    print("\nInvalid bet amount. Try again.")
                    raise
                self.chips -= bet
                i = 1
            except:
                i = 0
        
        result = self.wheel.spin()
        print("Result is:", result)
        if result == num:
            print("\nBet won! Congratulations!")
            self.chips += 36 * bet
        else:
            print("\nBet lost...")

    def play(self):
        print("\nWelcome to Roulette.")
        print("\n1) Inside Bet\n2) Outside Bet")

        # Get valid bet type input.
        i = 0
        while i == 0:
            bet_type = input("\nPick a bet type: ")
            bet_type = bet_type.lower()
            valid_bet_types =  ['1', '2', 'inside', 'outside', 'i', 'o']
            if bet_type in valid_bet_types:
                # Collapse valid bet type options into single options.
                if bet_type == '1' or bet_type == 'inside' or bet_type == 'i':
                    bet_type = 'inside'
                else:
                    bet_type = 'outside'
                i = 1
            else:
                print("Invalid option. Choose again.")
        
        # Get valid bet from bet type.
        if bet_type == 'inside':
            self.insideBet()
        else:
            pass
            # Give outside bet options.

        return self.chips
