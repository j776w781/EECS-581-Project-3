from PyQt6.QtWidgets import QWidget, QGraphicsScene, QGraphicsObject, QPushButton, QMessageBox
from PyQt6.QtCore import QPropertyAnimation, QRect, QPointF, QEasingCurve, QRectF, pyqtProperty, QTimer, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter
from .ui.poker_ui import Ui_PokerScreen
from .objects.deck import Deck
from .objects.hand import Hand
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARDS_DIR = os.path.join(BASE_DIR, "../assets/cards")
ASSET_DIR = os.path.join(BASE_DIR, "../assets")

class PokerScreen(QWidget):
    switch_to_menu = pyqtSignal()

    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.ui = Ui_PokerScreen()
        self.ui.setupUi(self)
        self.ui.playerHandLabel.setGeometry(QRect(280, 520, 240, 61))
        self.ui.opp1.setPixmap(QPixmap(ASSET_DIR + "/glass_joe.png"))
        self.ui.opp2.setPixmap(QPixmap(ASSET_DIR + "/super_macho_man.png"))
        self.ui.opp3.setPixmap(QPixmap(ASSET_DIR + "/king_hippo.png"))

        self.state = state
        self.game = Poker()

        self.ui.leaveButton.clicked.connect(self.leave)

    def leave(self):
        self.switch_to_menu.emit()


class Poker:
    def __init__(self):
        self.deck = Deck() # We need the deck of course.
        self.playerHand = Hand() # We need the player hand of course.
        self.board = [] # Keeps track of cards in center.
        self.oppNo = 0 # We need to know how many opponents we have in order to make that many later.
        self.pot = 0
        self.fold = False # This will likely be valuable in interrupting gameflow.

    # Method to deal initial two cards to a given player.
    def deal(self, hand):
        hand.add(self.deck.draw())
        hand.add(self.deck.draw())

    '''
    Game flow occurs in three stages: flop, turn, and river.
    We are going to abstract each stage into methods.
    So while the methods are quite elementary, (and two are exactly the same for that matter)
    the abstraction will make later coding easier (at least for me it will).
    '''

    def flop(self):
        self.board.append(self.deck.draw())
        self.board.append(self.deck.draw())
        self.board.append(self.deck.draw())

    def turn(self):
        self.board.append(self.deck.draw())

    def river(self):
        self.board.append(self.deck.draw())

    def analyzeHand(self, hand):
        hand_type, best_hand = self.playerHand.getBestHand(self.board)
        print(hand_type)
        print(best_hand)