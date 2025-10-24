from PyQt6.QtWidgets import QWidget, QGraphicsScene, QGraphicsObject, QPushButton, QMessageBox
from PyQt6.QtCore import QPropertyAnimation, QPointF, QEasingCurve, QRectF, pyqtProperty
from PyQt6.QtGui import QPixmap, QPainter
from .ui.blackjack_ui import Ui_BlackJackScreen
from .objects.deck import Deck
import time
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARDS_DIR = os.path.join(BASE_DIR, "../assets/cards")
CHIPS_DIR = os.path.join(BASE_DIR, "../assets")

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


class BlackJackScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_BlackJackScreen()
        self.ui.setupUi(self)

        self.scene = QGraphicsScene(0, 0, 600, 590, self)
        self.ui.cardGraphicsView.setScene(self.scene)

        self.deck_pos = QPointF(0, 240)
        self.player_pos = QPointF(300, 400)
        self.dealer_pos = QPointF(300, 70)

        self.game = BlackJack(1000)
        self.ui.dealButton.clicked.connect(self.deal)

        # Rules button
        self.rulesButton = QPushButton("Rules", self)
        self.rulesButton.move(20, 20)
        self.rulesButton.clicked.connect(self.showRules)



        
        self.chipsButton = QPushButton("Summon Chips", self)
        self.chipsButton.move(20, 500)
        self.chipsButton.clicked.connect(self.create_chip)
        
        

    def showRules(self):
        rules_text = (
            "Blackjack Rules:\n"
            "- Goal: Get as close to 21 without going over.\n"
            "- Number cards = face value, J/Q/K = 10, Ace = 1 or 11.\n"
            "- Player can Hit (draw) or Stand (end turn).\n"
            "- Dealer hits until reaching at least the player's score or bust.\n"
            "- Highest score ≤ 21 wins."
        )
        QMessageBox.information(self, "Blackjack Rules", rules_text)

    def deal(self):
        print("Dealing cards...")
        self.game.deal(self.game.playerHand)
        for i, card in enumerate(self.game.playerHand):
            card_sprite = self.createCard(card)
            end = self.player_pos + QPointF(i * 80, 0)
            self.animateCard(self.deck_pos, end, card_sprite)

        self.game.deal(self.game.dealerHand)
        for i, card in enumerate(self.game.dealerHand):
            if i == 0:
                card_sprite = self.createCard(card, True)
            else:
                card_sprite = self.createCard(card)
            end = self.dealer_pos + QPointF(i * 80, 0)
            self.animateCard(self.deck_pos, end, card_sprite)

        print(self.game.dealerHand)
        print(self.game.playerHand)
        self.ui.dealButton.setEnabled(False)

    def createCard(self, card, hidden=False):
        print("Creating cards...")
        if hidden:
            path = os.path.join(CARDS_DIR, "card_back.jpg")
        else:
            path = os.path.join(CARDS_DIR, "ace_of_spade.png")
        print(path)
        pixmap = QPixmap(path).scaled(100, 145)
        return pixmap
    


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


    def create_chip(self):
        print("Creating chip...")
        path = os.path.join(CHIPS_DIR, "chips.png")
        print(path)
        pixmap = QPixmap(path)

        chip_size = 48
        index = 2
        x = index * chip_size
        y = 0

        # Extract it as a sub-image
        chip_pixmap = pixmap.copy(x, y, 48, 50).scaled(75, 100)

        # Now you can display or use chip_pixmap
        chip_item = self.scene.addPixmap(chip_pixmap)
        chip_item.setPos(500, 500)
        return chip_pixmap


class BlackJack:
    def __init__(self, chips):
        self.deck = Deck()
        self.playerHand = []
        self.dealerHand = []
        self.playerScore = 0
        self.dealerScore = 0
        self.chips = chips
        self.bust = False

    def deal(self, hand):
        hand.append(self.deck.draw())
        hand.append(self.deck.draw())

    def printHand(self, hand, hide=False):
        for card in hand:
            if hide and hand.index(card) == 0:
                print('*')
            else:
                print(card)
        return

    def getTotal(self, hand):
        total = [0]
        for card in hand:
            if card.rank == 'ace':
                if total[0] + 11 > 21:
                    total[0] = total[0] + 1
                else:
                    total.append('ace')
            elif card.rank in ['jack', 'queen', 'king']:
                total[0] = total[0] + 10
            else:
                total[0] = total[0] + card.rank
        return total

    def verifyTotal(self, total):
        for i in range(1, len(total)):
            if total[0] + 11 <= 21:
                continue
            else:
                total[0] += 1
                total[i] = ''
        while '' in total:
            index = total.index('')
            total.pop(index)

    def getBestSum(self, total):
        final = total[0]
        for i in range(1, len(total)):
            if final + 11 <= 21:
                final += 11
            else:
                final += 1
        return final

    def playerTurn(self):
        while True:
            print("\nDealer's hand:")
            self.printHand(self.dealerHand, True)
            print("\nPlayer's hand:")
            self.printHand(self.playerHand)

            choice = input('\nHit or Stand?: ')
            choices = ['hit', 'h', 'stand', 's']
            while choice.lower() not in choices:
                print("Invalid choice. Please 'hit' or 'stand'.")
                choice = input('Hit or Stand: ')

            if choice.lower() in ['hit', 'h']:
                self.playerHand.append(self.deck.draw())
                total = self.getTotal(self.playerHand)

                if len(total) > 1:
                    self.verifyTotal(total)
                if total[0] > 21:
                    total = self.getBestSum(total)
                    return total
            else:
                total = self.getTotal(self.playerHand)
                if len(total) > 1:
                    self.verifyTotal(total)
                total = self.getBestSum(total)
                return total

    def dealerTurn(self):
        while True:
            print("\nDealer\'s hand:")
            self.printHand(self.dealerHand)
            print('\nPlayer\'s hand:')
            self.printHand(self.playerHand)

            time.sleep(2)

            total = self.getTotal(self.dealerHand)
            if len(total) > 1:
                self.verifyTotal(total)
            if self.getBestSum(total) < self.playerScore:
                print('\nDealer hits.')
                self.dealerHand.append(self.deck.draw())
                total = self.getTotal(self.dealerHand)
                if len(total) > 1:
                    self.verifyTotal(total)
                if total[0] > 21:
                    total = self.getBestSum(total)
                    return total
            else:
                print('\nDealer stands.')
                total = self.getBestSum(total)
                return total

    def play(self):
        self.deal(self.dealerHand)
        self.deal(self.playerHand)

        print('\nChip total:', self.chips)
        i = 0
        while i == 0:
            try:
                bet = int(input('How much would you like to bet?: '))
                if bet < 1 or bet > self.chips:
                    print('\nInvalid bet. Try again.')
                    raise
                i = 1
            except:
                i = 0

        self.chips -= bet
        self.playerScore = self.playerTurn()

        print('\nDealer\'s hand:')
        self.printHand(self.dealerHand, True)
        print('\nPlayer\'s hand:')
        self.printHand(self.playerHand)

        if self.playerScore > 21:
            print('\nTotal:', self.playerScore)
            print("BUST!!! Game Over!")
            self.bust = True
        else:
            print('\nTotal:', self.playerScore)
            print('\nDealer\'s Turn...')

        if not self.bust:
            time.sleep(5)
            self.dealerScore = self.dealerTurn()

            print('\nDealer\'s hand:')
            self.printHand(self.dealerHand)
            print('\nPlayer\'s hand:')
            self.printHand(self.playerHand)

            if self.dealerScore > 21:
                print('\nPlayer Total:', self.playerScore)
                print('Dealer Total:', self.dealerScore)
                print("\nDealer busts! You win!")
                self.chips += bet * 2

            elif self.playerScore > self.dealerScore:
                print('\nPlayer Total:', self.playerScore)
                print('Dealer Total:', self.dealerScore)
                print("\nYou win!")
                self.chips += bet * 2

            elif self.playerScore == self.dealerScore:
                print('\nPlayer Total:', self.playerScore)
                print('Dealer Total:', self.dealerScore)
                print("\nA tie. You get your bet back.")
                self.chips += bet

            else:
                print('\nPlayer Total:', self.playerScore)
                print('Dealer Total:', self.dealerScore)
                print("\nDealer wins.")
                print(f"\nYour current chip total: {self.chips}")

                if self.chips <= 0:
                    print("\nYou’ve lost all your chips! Returning to main menu...")
                    time.sleep(2)
                    return "out_of_chips"



