from PyQt6.QtWidgets import QWidget, QGraphicsScene, QGraphicsObject, QPushButton, QMessageBox
from PyQt6.QtCore import QPropertyAnimation, QPointF, QEasingCurve, QRectF, pyqtProperty, QTimer, pyqtSignal
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
    switch_to_menu = pyqtSignal()

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

        '''
        self.chipsButton = QPushButton("Summon Chips", self)
        self.chipsButton.move(20, 500)
        self.chipsButton.clicked.connect(self.create_chip)
        '''
        

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
            keep = self.animateCard(self.deck_pos, end, card_sprite)

            if i == 0:
                self.hidden_card = keep

        print(self.game.dealerHand)
        print(self.game.playerHand)
        self.ui.dealButton.setEnabled(False)






    def createCard(self, card, hidden=False):
        print("Creating cards...")
        if hidden:
            path = os.path.join(CARDS_DIR, "card_back.jpg")
        else:
            path = os.path.join(CARDS_DIR, "" + str(card.rank) + "_of_" + card.suit + ".png")
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

        return card_sprite


    def animateDealerCard(self, card, idx):
        card_sprite = self.createCard(card, hidden=False)
        end = self.dealer_pos + QPointF(idx * 80, 0)
        self.animateCard(self.deck_pos, end, card_sprite)

    def create_chip(self, num):
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
        #chip_item = self.scene.addPixmap(chip_pixmap)
        #chip_item.setPos(500, 500)
        return chip_pixmap
    

    def betMore(self):
        if self.game.chips == self.player_chips:
            QMessageBox.information(self, "Maximum Bet", "You've already bet all your chips! Good luck!")
        else:
            self.game.chips += 1
            self.ui.chipsNum.setText(f"Available chips: {self.player_chips - self.game.chips}")
        return 

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

        print(f"Dealer's score: {self.game.dealerScore}")


    def game_over(self, winner):
        if winner == "dealer":
            '''
            BISSHOY: The player loses the chips they bet "stored in self.game.chips". You'll have to subtract those from
            the player_chips attribute. This would be the time to potentially remove them from the game. Also, might want to include
            in here the option to replay(reset the GUI to initial state).
            '''
            return
        return




    def hit(self):
        cur_total, card, busted = self.game.hit("human")
        print(self.game.playerHand)
        end = self.player_pos + QPointF((len(self.game.playerHand)-1)*80, 0)
        card = self.createCard(card)
        self.animateCard(self.deck_pos, end, card)
        '''
        TODO: Use the BlackJack class (.game attribute) to add a card to the player's hand.
        DON'T do the random selection here. It should do that in the BlackJack class and simply
        return the card here. (also might want to return whether or not a bust has occurred.)

        This function should ONLY handle the animation for adding the card to the DEALER's OR PLAYER's hand.
        It could also trigger the loss function if bust returns true.

        Could also show current score.
        '''
	
        if busted:
            self.ui.hitButton.setEnabled(False)
            self.ui.standButton.setEnabled(False)
            self.game_over("dealer")
        return
    
    def start(self):

        if self.game.chips > 0:
            self.ui.betButton.setEnabled(False)
            self.ui.hitButton.setEnabled(True)
            self.ui.standButton.setEnabled(True)
            self.deal()
        else:
            QMessageBox.information(self, "No Bet", "We're not running a charity! Place your bet!")

    def leave(self):
        self.scene.clear()
        self.game = BlackJack()
        self.ui.dealButton.setEnabled(True)
        self.ui.betButton.setEnabled(True)
        self.ui.hitButton.setEnabled(False)
        self.ui.standButton.setEnabled(False)
        self.switch_to_menu.emit()


class BlackJack:
    def __init__(self):
        self.deck = Deck()
        self.playerHand = []
        self.dealerHand = []
        self.playerScore = 0
        self.dealerScore = 0
        self.chips = 0
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
        '''
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
        '''



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



