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

'''
Helper class. Required for animated sprites, which need to be
recreated repeatedly during animation.
'''
class AnimatedCard(QGraphicsObject):
    def __init__(self, pixmap):
        super().__init__()
        self._pixmap = pixmap
        self._pos = QPointF(0, 0)

    def boundingRect(self):
        return QRectF(0, 0, self._pixmap.width(), self._pixmap.height())

    def paint(self, painter, option, widget=None):
        painter.drawPixmap(0, 0, self._pixmap)

    def getPos(self):
        return super().pos()

    def setPos(self, pos):
        super().setPos(pos)

    pos = pyqtProperty(QPointF, fget=getPos, fset=setPos)

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
        self.ui.deckLabel.setPixmap(QPixmap(CARDS_DIR + "/card_back.jpg"))
        
        self.scene = QGraphicsScene(0, 0, 600, 590, self)
        self.ui.graphicsView.setScene(self.scene)

        self.state = state
        self.pot = 0
        self.ui.totalLabel.setText(f"Chip Total: {self.state.chips}")
        self.ui.potLabel.setText(f"Pot: {self.pot}")
        self.game = Poker()

        self.player_pos = QPointF(224, 400)
        self.deck_pos = QPointF(-20, 345)
        self.board_pos = [QPointF(90, 205), QPointF(180, 205), QPointF(270, 205), QPointF(360, 205), QPointF(450, 205)]

        self.ui.dealButton.clicked.connect(self.deal)
        self.ui.leaveButton.clicked.connect(self.leave)

    '''
    Helpful function for obtaining the proper pixmap for a Card instance, based
    on rank, suit, and if its hidden.
    '''
    def createCard(self, card, hidden=False):
        print("Creating cards...")
        if hidden:
            path = os.path.join(CARDS_DIR, "card_back.jpg")
        else:
            path = os.path.join(CARDS_DIR, "" + str(card.rank) + "_of_" + card.suit + ".png")
        print(path)
        pixmap = QPixmap(path).scaled(71, 111)
        return pixmap
    

    '''
    Handles animation of a card. Takes in starting postiion, ending poisition, and pixmap.
    '''
    def animateCard(self, start, end, pixmap):
        print("Animating cards...")
        card_sprite = AnimatedCard(pixmap)
        self.scene.addItem(card_sprite)

        anim = QPropertyAnimation(card_sprite, b'pos')
        anim.setDuration(700)
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()

        if not hasattr(self, '_anims'):
            self._anims = []
        self._anims.append(anim)

        return card_sprite

    def deal(self):
        print("Dealing cards...")
        self.ui.leaveButton.setEnabled(False)
        self.pot += 50
        self.state.chips -= 50
        self.ui.totalLabel.setText(f'Chip Total: {self.state.chips}')
        self.ui.potLabel.setText(f'Pot: {self.pot}')

        self.game.deal(self.game.playerHand)
        for i, card in enumerate(self.game.playerHand.hand):
            card_sprite = self.createCard(card)
            end = self.player_pos + QPointF(i * 80, 0)
            self.animateCard(self.deck_pos, end, card_sprite)

        print(self.game.playerHand)

        QTimer.singleShot(1500, Qt.TimerType.PreciseTimer, lambda: self.flop())
        QTimer.singleShot(1500, Qt.TimerType.PreciseTimer, lambda: self.ui.leaveButton.setEnabled(True))

        self.ui.dealButton.setEnabled(False)

    def flop(self):
        self.game.flop()
        for i, card in enumerate(self.game.board):
            card_sprite = self.createCard(card)
            end = self.board_pos[i]
            self.animateCard(self.deck_pos, end, card_sprite)

        print(self.game.board)


    def leave(self):
        self.scene.clear()
        self.pot = 0
        self.ui.potLabel.setText(f"Pot: {self.pot}")
        self.game = Poker()
        self.ui.dealButton.setEnabled(True)
        self.switch_to_menu.emit()


class Poker:
    def __init__(self):
        self.deck = Deck() # We need the deck of course.
        self.playerHand = Hand() # We need the player hand of course.
        self.board = [] # Keeps track of cards in center.
        self.oppNo = 0 # We need to know how many opponents we have in order to make that many later.
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