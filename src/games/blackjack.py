'''
File: blackjack.py

Authors: Joshua Welicky, Gavin Billinger, Mark Kitchin, Max Biundo, Bisshoy Bhattacharjee

Description:
Stores the BlackJack class, which handles game logic related to Blackjack, and BlackJackScreen class,
which renders the GUI and effects the moves ordained by the BlackJack class.

Inputs: player_chips, the number of initial player chips.

Outputs: Functional GUI for Blackjack.
'''



from PyQt6.QtWidgets import QWidget, QGraphicsScene, QGraphicsObject, QPushButton, QMessageBox
from PyQt6.QtCore import QPropertyAnimation, QPointF, QEasingCurve, QRectF, pyqtProperty, QTimer, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter
from .ui.blackjack_ui import Ui_BlackJackScreen
from .objects.deck import Deck
import time
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARDS_DIR = os.path.join(BASE_DIR, "../assets/cards")
CHIPS_DIR = os.path.join(BASE_DIR, "../assets")


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



'''
Main class for managing GUI and effecting changes based on game logic.
'''
class BlackJackScreen(QWidget):
    #Connects to main window.
    switch_to_menu = pyqtSignal()

    '''
    Renders the initial state of the GUI, connecting buttons to helper functions.
    '''
    def __init__(self, parent=None, chips = 10):
        super().__init__(parent)
        self.ui = Ui_BlackJackScreen()
        self.ui.setupUi(self)

        self.scene = QGraphicsScene(0, 0, 600, 590, self)
        self.ui.cardGraphicsView.setScene(self.scene)

        self.deck_pos = QPointF(0, 240)
        self.player_pos = QPointF(300, 350)
        self.dealer_pos = QPointF(300, 80)

        self.game = BlackJack()
        self.ui.dealButton.clicked.connect(self.start)

        # Rules button
        self.rulesButton = QPushButton("Rules", self)
        self.rulesButton.move(20, 20)
        self.rulesButton.clicked.connect(self.showRules)

        self.player_chips = chips
        self.ui.chipsNum.setText(f"Available chips: {chips}")
        self.ui.betButton.clicked.connect(self.betMore)        


        self.ui.hitButton.clicked.connect(self.hit)
        self.ui.hitButton.setEnabled(False)
        self.ui.standButton.clicked.connect(self.dealerGo)
        self.ui.standButton.setEnabled(False)
        self.ui.leaveButton.clicked.connect(self.leave)
        self.addDeckBack()


    '''Adds the card deck icon to the GUI.'''
    def addDeckBack(self):
        deck_back_path = os.path.join(CARDS_DIR, "card_back.jpg")
        deck_back_pixmap = QPixmap(deck_back_path).scaled(100, 145)
        self.deck_item = self.scene.addPixmap(deck_back_pixmap)
        self.deck_item.setPos(self.deck_pos)
        
    '''Opens a window explaining the game rules.'''
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


    '''
    Initiates the dealing process and animates the player's and dealer's hands.
    The dealer's first card is hidden.
    '''
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
            keep = self.animateCard(self.deck_pos, end, card_sprite)

            if i == 0:
                self.hidden_card = keep

        print(self.game.dealerHand)
        print(self.game.playerHand)
        self.ui.dealButton.setEnabled(False)


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
        pixmap = QPixmap(path).scaled(100, 145)
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

    '''
    Similar function for animating the dealer's cards after the player stands.
    '''
    def animateDealerCard(self, card, idx):
        card_sprite = self.createCard(card, hidden=False)
        end = self.dealer_pos + QPointF(idx * 80, 0)
        self.animateCard(self.deck_pos, end, card_sprite)
    
    '''
    Adds a player's chip to the current gamble.
    '''
    def betMore(self):
        if self.game.chips == self.player_chips:
            QMessageBox.information(self, "Maximum Bet", "You've already bet all your chips! Good luck!")
        else:
            self.game.chips += 1
            self.ui.chipsNum.setText(f"Available chips: {self.player_chips - self.game.chips}")
        return 

    '''
    Takes over after the user stands. Generates the dealer's final hand, reveals the hidden card, animates each new
    card. Calls game_over based on the winner of the game.
    '''
    def dealerGo(self):
        self.ui.hitButton.setEnabled(False)
        self.ui.standButton.setEnabled(False)
        reveal = self.createCard(self.game.dealerHand[0], hidden=False)
        self.hidden_card._pixmap = reveal
        self.hidden_card.update()
        self.game.dealerTurn()
        
        wait = 0
        for i, card in enumerate(self.game.dealerHand):
            if i > 1:
                QTimer.singleShot(wait, lambda c=card, idx=i: self.animateDealerCard(c,idx))
                wait += 1000
        if self.game.dealerScore > 21:
            QTimer.singleShot(1000, Qt.TimerType.PreciseTimer, lambda: self.game_over("player"))
        elif self.game.dealerScore > self.game.playerScore:
            QTimer.singleShot(1000, Qt.TimerType.PreciseTimer, lambda: self.game_over("dealer"))
        elif self.game.dealerScore == self.game.playerScore:
            QTimer.singleShot(1000, Qt.TimerType.PreciseTimer, lambda: self.game_over("Tie"))
        else:
            QTimer.singleShot(1000, Qt.TimerType.PreciseTimer, lambda: self.game_over("player"))
        print(f"Player's score: {self.game.playerScore}")
        print(f"Dealer's score: {self.game.dealerScore}")


    '''
    Handles end game chip allocations/deallocations, and game resetting.
    Also handles forceful removal if you lose all chips.
    '''
    def game_over(self, winner):
        for card in self.scene.items():
            self.scene.removeItem(card)
        for i, card in enumerate(self.game.playerHand):
            
            card_sprite = self.createCard(card)
            end = self.player_pos + QPointF(i * 80, 0)
            self.animateCard(end, self.deck_pos, card_sprite)

        for i, card in enumerate(self.game.dealerHand):
            
            card_sprite = self.createCard(card)
            end = self.dealer_pos + QPointF(i * 80, 0)
            self.animateCard(end, self.deck_pos, card_sprite)

        QTimer.singleShot(1000, Qt.TimerType.PreciseTimer, lambda: self.scene.clear())

        self.game.playerHand = []
        self.game.dealerHand = []
        self.game.bust = False
        self.game.dealerScore = 0
        self.game.playerScore = 0

        self.ui.dealButton.setEnabled(True)
        self.ui.betButton.setEnabled(True)
        self.ui.hitButton.setEnabled(False)
        self.ui.standButton.setEnabled(False)
        if winner == "dealer":
            self.player_chips = self.player_chips- self.game.chips
            self.game.chips = 0
            QMessageBox.information(self, "Dealer Wins", "Dealer Wins")
            print("dealer wins!")
            if self.player_chips == 0:
                QMessageBox.information(self, "Get out.", "Get outta here!")
                self.leave()
            return 0
        elif winner == "player":
            QMessageBox.information(self, "You Win", "You Win")
            self.player_chips += self.game.chips*2
            self.game.chips = 0
            self.addDeckBack()
        return



    '''
    Calls for a new card to be added to the player's hand. 
    Animates the new card being added to the hand. 
    Checks for a bust, and ends the game accordingly.
    '''
    def hit(self):
        cur_total, card, busted = self.game.hit("human")
        print(self.game.playerHand)
        end = self.player_pos + QPointF((len(self.game.playerHand)-1)*80, 0)
        card = self.createCard(card)
        self.animateCard(self.deck_pos, end, card)
        if busted:
            self.ui.hitButton.setEnabled(False)
            self.ui.standButton.setEnabled(False)
            QTimer.singleShot(1000, Qt.TimerType.PreciseTimer, lambda: self.game_over("dealer"))
            
        return
    

    '''
    Starts the game, closing off unnecessary buttons and starting the deal.
    '''
    def start(self):
        if self.game.chips > 0:
            self.ui.betButton.setEnabled(False)
            self.ui.hitButton.setEnabled(True)
            self.ui.standButton.setEnabled(True)
            self.deal()
        else:
            QMessageBox.information(self, "No Bet", "We're not running a charity! Place your bet!")

    '''
    Handles game state resetting, including forfeited chips.
    '''
    def leave(self):
        self.scene.clear()
        self.player_chips = self.player_chips - self.game.chips
        self.game = BlackJack()
        self.ui.dealButton.setEnabled(True)
        self.ui.betButton.setEnabled(True)
        self.ui.hitButton.setEnabled(False)
        self.ui.standButton.setEnabled(False)
        self.addDeckBack()
        self.switch_to_menu.emit()






'''
Main game logic class for Black Jack.
'''
class BlackJack:
    def __init__(self):
        self.deck = Deck()
        self.playerHand = []
        self.dealerHand = []
        self.playerScore = 0
        self.dealerScore = 0
        self.chips = 0
        self.bust = False

    '''Adds card to a hand''' 
    def deal(self, hand):
        hand.append(self.deck.draw())
        hand.append(self.deck.draw())

    '''
    Prints a hand for debugging.
    '''
    def printHand(self, hand, hide=False):
        for card in hand:
            if hide and hand.index(card) == 0:
                print('*')
            else:
                print(card)
        return

    '''
    Returns a minimum total, and a list of aces.
    '''
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

    '''
    Removes any aces that must evaluate to one to preserve the score.
    '''
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

    '''
    Synthesizes a final sum, fully processing aces.
    '''
    def getBestSum(self, total):
        final = total[0]
        for i in range(1, len(total)):
            if final + 11 <= 21:
                final += 11
            else:
                final += 1
        return final


    '''
    Adds a card to the player's hand, returning the best sum, card, and 
    whether they busted.
    '''
    def hit(self, player):
        if player == 'human':
            self.playerHand.append(self.deck.draw())
            card = self.playerHand[len(self.playerHand)-1]
            total = self.getTotal(self.playerHand)

            if len(total) > 1:
                self.verifyTotal(total)
            total = self.getBestSum(total)
            if total > 21:
                return total, card, True
            return total, card, False


    '''
    Builds out the dealer's hand until they reach 17 or bust.
    '''
    def dealerTurn(self):
        print("\nDealer\'s hand:")
        self.printHand(self.dealerHand)
        print('\nPlayer\'s hand:')
        self.printHand(self.playerHand)


        while True:
            print("\nDealer\'s hand:")
            self.printHand(self.dealerHand)
            print('\nPlayer\'s hand:')
            self.printHand(self.playerHand)

            total = self.getTotal(self.dealerHand)
            if len(total) > 1:
                self.verifyTotal(total)
            #if self.getBestSum(total) < self.playerScore:
            #Casino rules I guess
            if self.getBestSum(total) < 17:
                print('\nDealer hits.')
                self.dealerHand.append(self.deck.draw())
                total = self.getTotal(self.dealerHand)
                if len(total) > 1:
                    self.verifyTotal(total)
                if total[0] > 21:
                    self.dealerScore = self.getBestSum(total)
            else:
                print('\nDealer stands.')
                self.dealerScore = self.getBestSum(total)
                return
