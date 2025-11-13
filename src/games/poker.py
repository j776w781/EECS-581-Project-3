from PyQt6.QtWidgets import QWidget, QGraphicsScene, QGraphicsObject, QPushButton, QMessageBox
from PyQt6.QtCore import QPropertyAnimation, QRect, QPointF, QEasingCurve, QRectF, pyqtProperty, QTimer, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter
from .ui.poker_ui import Ui_PokerScreen
from .objects.opponent import Opponent
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
        self.ui.opp3.setPixmap(QPixmap(ASSET_DIR + "/glass_joe.png"))
        self.ui.opp1.setPixmap(QPixmap(ASSET_DIR + "/super_macho_man.png"))
        self.ui.opp2.setPixmap(QPixmap(ASSET_DIR + "/king_hippo.png"))
        self.ui.deckLabel.setPixmap(QPixmap(CARDS_DIR + "/card_back.jpg"))
        
        self.scene = QGraphicsScene(0, 0, 600, 590, self)
        self.ui.graphicsView.setScene(self.scene)

        self.state = state
        self.pot = 0
        self.ui.totalLabel.setText(f"Chip Total: {self.state.chips}")
        self.ui.potLabel.setText(f"Pot: {self.pot}")
        self.game = Poker()

        # Opponent widgets (the icons and such)
        self.oppWidgets = [self.ui.opp1, self.ui.opp2, self.ui.opp3, self.ui.oppTotal1, self.ui.oppTotal2, self.ui.oppTotal3]
        self.updatePlayers(3)

        # Track positions
        self.player_pos = QPointF(224, 380)
        self.opps_pos = [QPointF(360, 5), QPointF(540, 50), QPointF(-90, 50)]
        self.deck_pos = QPointF(-20, 345)
        self.board_pos = [QPointF(90, 185), QPointF(180, 185), QPointF(270, 185), QPointF(360, 185), QPointF(450, 185)]

        # Handle buttons (except all in defined below)
        self.ui.oppCount.valueChanged.connect(self.updatePlayers)
        self.ui.dealButton.clicked.connect(self.deal)
        self.ui.checkcallButton.clicked.connect(self.checkorcall)
        self.ui.checkcallButton.setEnabled(False)
        self.ui.betraiseButton.clicked.connect(self.betorraise)
        self.ui.betraiseButton.setEnabled(False)
        self.ui.foldButton.clicked.connect(self.fold)
        self.ui.foldButton.setEnabled(False)
        self.ui.leaveButton.clicked.connect(self.leave)

        # All in button goes crazy
        self.ui.allinButton.clicked.connect(self.allIn)
        self.ui.allinButton.setEnabled(False)
        self.colors = [
                "#39ff14",
                "#ff073a",
                "#00ffff",
                "#ff6ec7",
                "#ffff33",
                "#00ffcc"
        ]
        self.color_index = 0
        # Create timer that runs flash function every 75ms
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.flash)
        self.timer.start(75)

        self.fontControl()

    # Cycles through different neon colors.
    def flash(self):
        color = self.colors[self.color_index]
        self.ui.allinButton.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: black;
                border: 3px solid white;
                border-radius: 15px;
                font-weight: bold;
            }}
        """)
        self.color_index = (self.color_index + 1) % len(self.colors)
        if self.color_index > 1000000: # This is so we don't overload the program with some kind of overflow.
            self.color_index = 0

    def fontControl(self):
        # Font Size Control (Adjust this until the fonts work work for you guys)
        font = self.ui.label.font()
        font.setPointSize(24)
        self.ui.label.setFont(font)

        font = self.ui.oppCount.font()
        font.setPointSize(24)
        self.ui.oppCount.setFont(font)

        font = self.ui.playerHandLabel.font()
        font.setPointSize(36)
        self.ui.playerHandLabel.setFont(font)

        font = self.ui.totalLabel.font()
        font.setPointSize(24)
        self.ui.totalLabel.setFont(font)

        for i in range(self.game.oppNo):
            font = self.oppWidgets[i+3].font()
            font.setPointSize(14)
            self.oppWidgets[i+3].setFont(font)

    def updatePlayers(self, value):
        for i in range(3):
            if i < value:
                self.oppWidgets[i].show()
                self.oppWidgets[i+3].show()
            if i >= value:
                self.oppWidgets[i].hide()
                self.oppWidgets[i+3].hide()
        self.game.oppNo = value

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
        # First we hide insignificant details.
        self.ui.leaveButton.setEnabled(False)
        self.ui.oppCount.setEnabled(False)
        self.ui.label.hide()
        self.ui.oppCount.hide()

        # Game makes opponents
        if self.game.started == False:
            self.game.createOpponents(self.game)
        
        # Displays the opponent chip totals.
        for i in range(self.game.oppNo):
            self.oppWidgets[i+3].setText(f'Chips: {self.game.opps[i].chipTotal}')

        # Game deals cards.
        self.game.deal()

        # Game updates pot.
        self.pot += self.game.stake
        for i in range(len(self.game.opps)):
            self.pot += self.game.opps[i].stake
            self.oppWidgets[i+3].setText(f'Chip: {self.game.opps[i].chipTotal - self.game.opps[i].stake}')
        self.ui.totalLabel.setText(f'Chip Total: {self.state.chips - self.game.stake}')
        self.ui.potLabel.setText(f'Pot: {self.pot}')

        # UI animates cards to player hand.
        for i, card in enumerate(self.game.playerHand.hand):
            card_sprite = self.createCard(card)
            end = self.player_pos + QPointF(i * 80, 0)
            self.animateCard(self.deck_pos, end, card_sprite)

        # UI animates cards for each opponent
        for i in range(len(self.game.opps)):
            print(f"Animating to {self.game.opps[i].name}")
            for j, card in enumerate(self.game.opps[i].oppHand.hand):
                card_sprite = self.createCard(card, True)
                end = self.opps_pos[i] + QPointF(j * 80, 0)
                self.animateCard(self.deck_pos, end, card_sprite)
        
        print(self.game.playerHand)

        QTimer.singleShot(1500, Qt.TimerType.PreciseTimer, lambda: self.flop())
        QTimer.singleShot(1500, Qt.TimerType.PreciseTimer, lambda: self.ui.leaveButton.setEnabled(True))
        QTimer.singleShot(1500, Qt.TimerType.PreciseTimer, lambda: self.enablePlayerActions(True))

        self.ui.dealButton.setEnabled(False)

    def enablePlayerActions(self, enable):
        self.ui.checkcallButton.setEnabled(enable)
        self.ui.betraiseButton.setEnabled(enable)
        self.ui.foldButton.setEnabled(enable)
        self.ui.allinButton.setEnabled(enable)

    def nextTurn(self):
        if self.game.checked == len(self.game.players):
            self.endRound()
            return

        current_turn = self.game.turn_index
        self.game.turn_index = (self.game.turn_index + 1) % (self.game.oppNo + 1)
        if current_turn == 0: # Player turn
            self.enablePlayerActions(True)
        else:
            self.enablePlayerActions(False)
            QTimer.singleShot(1500, Qt.TimerType.PreciseTimer, lambda: self.opponentTurn(current_turn))

    def opponentTurn(self, index):
        self.game.opps[index-1].decision(index)
        #self.game.next_turn
        self.nextTurn()

    def endRound(self):
        self.enablePlayerActions(False)
        self.game.checked = 0

        if len(self.game.board) == 3:
            self.turn()
        elif len(self.game.board) == 4:
            self.river()
        else:
            self.gameOver()

    def gameOver(self):
        winner = self.game.get_results()
        for i in range(len(self.game.players)):
            if winner == i and i == 0:
                self.state.chips -= self.game.stake
                self.state.chips += self.pot
                self.ui.totalLabel.setText(f'Chip Total: {self.state.chips}')
            elif winner == i:
                self.game.players[i].chipTotal -= self.game.players[i].stake
                self.game.players[i].chipTotal += self.pot
                self.oppWidgets[self.game.players[i].id + 3].setText(f'Chips: {self.game.players[i].chipTotal}')
            else:
                if i == 0:
                    self.state.chips -= self.game.stake
                    self.ui.totalLabel.setText(f'Chip Total: {self.state.chips}')
                else:
                    self.game.players[i].chipTotal -= self.game.players[i].stake
                    self.oppWidgets[self.game.players[i].id + 3].setText(f'Chip: {self.game.players[i].chipTotal}')
        self.reset()

    def reset(self):
        for card in self.scene.items():
            self.scene.removeItem(card)

        for i, card in enumerate(self.game.playerHand.hand):
            card_sprite = self.createCard(card)
            end = self.player_pos + QPointF(i * 80, 0)
            self.animateCard(end, self.deck_pos, card_sprite)

        for i in range(len(self.game.opps)):
            for j, card in enumerate(self.game.opps[i].oppHand.hand):
                card_sprite = self.createCard(card)
                end = self.opps_pos[i] + QPointF(j * 80, 0)
                self.animateCard(end, self.deck_pos, card_sprite)
        
        QTimer.singleShot(1000, Qt.TimerType.PreciseTimer, lambda: self.scene.clear())

        self.game.reset()
        self.pot = 0
        self.ui.potLabel.setText(f"Pot: {self.pot}")
        self.ui.checkcallButton.setText("Check")
        self.ui.betraiseButton.setText("Bet")
        self.ui.dealButton.setEnabled(True)
        self.ui.checkcallButton.setEnabled(False)
        self.ui.betraiseButton.setEnabled(False)
        self.ui.foldButton.setEnabled(False)
        self.ui.allinButton.setEnabled(False)

    def checkorcall(self):
        if self.game.activeBet:
            # Game logic of a check happens here.
            self.game.call()

            self.ui.checkcallButton.setText("Check")
            self.ui.betraiseButton.setText("Bet")
        else:
            # Game logic of a check happens here.
            self.game.check()

        self.nextTurn()

    def betorraise(self):
        if self.game.activeBet:
            self.game._raise()
        else:
            if len(self.game.board) < 5:
                self.ui.checkcallButton.setText("Call")
                self.ui.betraiseButton.setText("Raise")
                self.game.bet()

        self.nextTurn()

    def fold(self):
        self.game.fold()

        self.nextTurn()
        pass

    def allIn(self):
        self.game.allIn()

        self.nextTurn()
        pass

    def flop(self):
        self.game.flop()
        for i, card in enumerate(self.game.board):
            card_sprite = self.createCard(card)
            end = self.board_pos[i]
            self.animateCard(self.deck_pos, end, card_sprite)

        self.game.start_round()
        self.nextTurn()

    def turn(self):
        self.game.turn()
        card_sprite = self.createCard(self.game.board[3])
        end = self.board_pos[3]
        self.animateCard(self.deck_pos, end, card_sprite)

        self.game.start_round()
        self.nextTurn()

        print(self.game.board)

    def river(self):
        self.game.river()
        card_sprite = self.createCard(self.game.board[4])
        end = self.board_pos[4]
        self.animateCard(self.deck_pos, end, card_sprite)

        self.game.start_round()
        self.nextTurn()

        print(self.game.board)

    def leave(self):
        self.scene.clear()
        self.state.chips -= self.game.stake
        self.pot = 0
        self.ui.potLabel.setText(f"Pot: {self.pot}")
        self.ui.checkcallButton.setText("Check")
        self.ui.betraiseButton.setText("Bet")
        self.game = Poker()
        self.ui.dealButton.setEnabled(True)
        self.ui.checkcallButton.setEnabled(False)
        self.ui.betraiseButton.setEnabled(False)
        self.ui.foldButton.setEnabled(False)
        self.ui.allinButton.setEnabled(False)
        self.ui.oppCount.setEnabled(True)
        self.ui.label.show()
        self.ui.oppCount.show()
        self.ui.oppCount.setValue(3)
        self.updatePlayers(3)
        self.ui.oppTotal1.setText("Chips:")
        self.ui.oppTotal2.setText("Chips:")
        self.ui.oppTotal3.setText("Chips:")
        self.switch_to_menu.emit()


class Poker:
    def __init__(self):
        self.deck = Deck() # We need the deck of course.
        self.name = "Player"
        self.playerHand = Hand() # We need the player hand of course.
        self.bestHand = []
        self.handRank = 0
        self.stake = 0
        self.board = [] # Keeps track of cards in center.
        self.oppNo = 0 # We need to know how many opponents we have in order to make that many later.
        self.opps = []
        self.turn_index = 0
        self.players = []
        self.checked = 0
        self.started = False
        self.activeBet = False # We need to know if a bet is currently occurring.
        self.folded = False # This will likely be valuable in interrupting gameflow.

    def createOpponents(self, game):
        names = ["Super Macho Man", "King Hippo", "Glass Joe"]
        for i in range(self.oppNo):
            self.opps.append(Opponent(names[i], game, i))
            self.opps[i].chipTotal = 1000
        self.players = ['Player'] + self.opps

    # Method to deal initial two cards to a given player.
    def deal(self):
        self.started = True
        self.stake += 50 # Ante
        self.playerHand.add(self.deck.draw())
        self.playerHand.add(self.deck.draw())

        for i in range(len(self.opps)):
            print(f"{self.opps[i].name} gets dealt.")
            self.opps[i].stake += 50
            self.opps[i].oppHand.add(self.deck.draw())
            self.opps[i].oppHand.add(self.deck.draw())


    '''
    At the beginning, we will deal and post ante (50 chips). Then the cards will be dealt
    and Flop will start. People go around checking until someone bets. This will create an active bet.
    
    During an active bet, you can't check. You either call (match the bet), raise (increase the bet), 
    or fold (give up the hand). Once everybody calls/checks. The bet is inactive and the next round can start
    assuming there is more than one player remaining.

    Then Turn starts. The fourth card is revealed and players go around doing the previous actions of Flop.
    Once Turn ends, River starts. River progresses the same as Flop and Turn.

    When River ends, all hands are revealed. The greatest hand will have the pot added to their Chip Total.
    '''
    def start_round(self):
        self.turn_index = 0

    def next_turn(self):
        self.turn_index = (self.turn_index + 1) % len(self.players)

    def flop(self):
        self.board.append(self.deck.draw())
        self.board.append(self.deck.draw())
        self.board.append(self.deck.draw())

    def turn(self):
        self.board.append(self.deck.draw())

    def river(self):
        self.board.append(self.deck.draw())

    def check(self, index=0):
        print("Checking...")
        self.checked += 1
        # Otherwise the end we'll keep these in mind.
        self.handRank, self.bestHand = self.analyzeHand()
        print(self.handRank)
        print(self.bestHand)

    def call(self, index=0):
        print("Calling...")
        self.checked += 1
        # Otherwise the end might be...
        #self.activeBet = False
        self.handRank, self.bestHand = self.analyzeHand()
        print(self.handRank)
        print(self.bestHand)

    def bet(self, index=0):
        print("Betting...")
        self.checked = 1
        self.activeBet = True
        self.players[index].stake += 50

    def _raise(self, index=0):
        print("Raising...")
        self.checked = 1
        self.players[index].stake += 50

    def fold(self):
        print("Folding...")

    def allIn(self):
        print("GOING ALL IN!!!")

    def get_results(self):
        print("Ending game...")
        self.handRank, self.bestHand = self.analyzeHand()

        handRanks = [
                "High Card", "Pair", "Two Pair", "Three of a Kind", "Straight",
                 "Flush", "Full House", "Four of a Kind", "Straight Flush", "Royal Flush"
        ]

        bestRank = handRanks.index(self.handRank)
        bestCombo = self.bestHand
        bestPlayerIndex = 0

        for i in range(1, len(self.players)):
            # Compare poker hands by higher index.
            if handRanks.index(self.players[i].handRank) > bestRank:
                bestRank = handRanks.index(self.players[i].handRank)
                bestCombo = self.players[i].bestHand
                bestPlayerIndex = i
            elif handRanks.index(self.players[i].handRank) == bestRank: # In tie breaker case, we go by highest value card.
                if sorted([card.rank for card in self.players[i].bestHand], reverse=True) > sorted([card.rank for card in bestCombo], reverse=True):
                    bestCombo = self.players[i].bestHand
                    bestPlayerIndex = i
        print('Best player is:', self.players[bestPlayerIndex])
        print('Best hand is:', bestCombo)
        return bestPlayerIndex

    def reset(self):
        self.deck.shuffle()
        self.playerHand = Hand()

        self.bestHand = []
        self.bestRank = 0
        self.stake = 0
        self.board = []
        self.turn_index = 0
        self.checked = 0
        self.activeBet = False
        self.folded = False

        for i in range(1, len(self.players)):
            self.players[i].stake = 0
            self.players[i].oppHand = Hand()

    def analyzeHand(self):
        hand_type, best_hand = self.playerHand.getBestHand(self.board)
        return hand_type, best_hand