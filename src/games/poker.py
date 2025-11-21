import random

from PyQt6.QtWidgets import QWidget, QGraphicsScene, QMessageBox
from PyQt6.QtCore import QPropertyAnimation, QRect, QPointF, QEasingCurve, QTimer, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QPixmap
from .ui.poker_ui import Ui_PokerScreen
from .objects.opponent import Opponent
from .objects.deck import Deck, AnimatedCard
from .objects.hand import Hand
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARDS_DIR = os.path.join(BASE_DIR, "../assets/cards")
ASSET_DIR = os.path.join(BASE_DIR, "../assets")

#=================================================#
#================POKER SCREEN GUI=================#
#=================================================#

class PokerScreen(QWidget):
    switch_to_menu = pyqtSignal()

    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.ui = Ui_PokerScreen()
        self.ui.setupUi(self)
        self.ui.rulesButton.clicked.connect(self.rules)
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

    # Cycles through different neon colors for the allinButton
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

#=================== FOR MY FELLOW DEVS ===================#
# I don't know how the GUI looks for you guys, but play with these values until the screen looks semi normal
#==========================================================#

    def fontControl(self):
        # Font Size Control (Adjust this until the fonts work work for you guys)
        font = self.ui.label.font()
        font.setPointSize(24) # <<< Adjust me!
        self.ui.label.setFont(font)

        font = self.ui.oppCount.font()
        font.setPointSize(24) # <<< Adjsut me!
        self.ui.oppCount.setFont(font)

        font = self.ui.playerHandLabel.font()
        font.setPointSize(36) # <<< Adjust me!
        self.ui.playerHandLabel.setFont(font)

        font = self.ui.totalLabel.font()
        font.setPointSize(24) # <<< Adjust me!
        self.ui.totalLabel.setFont(font)

        for i in range(self.game.oppNo):
            font = self.oppWidgets[i+3].font()
            font.setPointSize(14) # <<< Adjust me!
            self.oppWidgets[i+3].setFont(font)

#=================== UPDATE PLAYERS ===================#
#===When oppCount value changes, update visible opps===#
#======================================================#

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

    def rules(self):
        rules_text = (
            "Poker Rules:\n\n"
            "1. Each player is dealt two private cards.\n"
            "2. Five community cards are dealt in stages: Flop (3), Turn (1), River (1).\n"
            "3. Players take turns to Check, Bet/Raise, Call, or Fold.\n"
            "4. Betting rounds occur before and after the flop, turn, and river.\n"
            "5. The best five-card hand using any combination of private and community cards wins the pot.\n"
            "6. Folding forfeits your hand and any chips you have bet.\n"
            "7. Checking passes the turn without betting.\n"
            "8. Players with 0 chips are out and returned to the main menu."
        )
        msg = QMessageBox()
        msg.setWindowTitle("Poker Rules")
        msg.setText(rules_text)
        msg.exec()

    #=================== POKER GUI START SEQUENCE ===================#

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

#=================== POKER GUI HELPER FUNCTION ===================#

    def enablePlayerActions(self, enable):
        self.ui.checkcallButton.setEnabled(enable)
        self.ui.betraiseButton.setEnabled(enable)
        self.ui.foldButton.setEnabled(enable)
        self.ui.allinButton.setEnabled(enable)

#=================== POKER GUI GAME STATE TRACKING ===================#

    def nextTurn(self):
        if self.game.checked == len(self.game.players):
            self.endRound()
            return

        current_turn = self.game.turn_index
        self.game.turn_index = (self.game.turn_index + 1) % (self.game.oppNo + 1)
        if current_turn == 0: # Player turn
            if self.game.folded:
                self.nextTurn()
            else:
                self.enablePlayerActions(True)
        else:
            self.enablePlayerActions(False)
            if self.game.opps[current_turn-1].folded:
                self.nextTurn()
            else:
                QTimer.singleShot(1500, Qt.TimerType.PreciseTimer, lambda: self.opponentTurn(current_turn))

    def opponentTurn(self, index):
        self.game.opps[index-1].decision(index)
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

    def sync_opponents_to_ui(self):
        self.ui.oppCount.blockSignals(True)
        self.ui.oppCount.setValue(self.game.oppNo)
        self.ui.oppCount.blockSignals(False)
        for i in range(3):
            self.oppWidgets[i].hide()
            self.oppWidgets[i+3].hide()
            self.oppWidgets[i+3].setText("Chips:")
        for i, opp in enumerate(self.game.opps):
            self.oppWidgets[i].show()
            self.oppWidgets[i+3].show()
            remaining_chips = opp.chipTotal - opp.stake
            self.oppWidgets[i+3].setText(f'Chips: {remaining_chips}')


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
        
        self.game.removeOpponents()
        if self.game.oppNo == 0:
            QMessageBox.information(self, "You Win!", "No Other Opponents have Chips. Congrats!")
            self.leave()

        if self.state.chips <= 0:
            QMessageBox.information(self, "Game Over", "You're out of chips! Returning to main menu.")
            self.switch_to_menu.emit()
            return

        self.reset()
        self.sync_opponents_to_ui()

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

#=================== POKER GUI BUTTON ACTIONS ===================#

    def checkorcall(self):
        if self.game.activeBet:
            # There’s a bet, so the player should call instead
            self.game.call(0)  # 0 = human player
        else:
            # No bet, player can just check
            self.game.check(0)
        self.nextTurn()

    def betorraise(self):
        if self.game.activeBet:
            self.game._raise()
        else:
            self.ui.checkcallButton.setText("Call")
            self.ui.betraiseButton.setText("Raise")
            self.game.bet()
            self.pot += 50
            self.ui.potLabel.setText(f'Pot: {self.pot}')

        self.nextTurn()

    def fold(self):
        self.game.fold(0)  # 0 = human player
        self.enablePlayerActions(False)  # Disable buttons after fold
        self.nextTurn()

    def allIn(self):
        self.game.allIn()

        self.nextTurn()

#=================== POKER GAME FLOW ANIMATIONS ===================#

    def flop(self):
        self.game.flop()
        for i, card in enumerate(self.game.board):
            card_sprite = self.createCard(card)
            end = self.board_pos[i]
            self.animateCard(self.deck_pos, end, card_sprite)

        self.ui.checkcallButton.setText("Check")
        self.ui.betraiseButton.setText("Bet")
        self.game.start_round()
        self.nextTurn()

    def turn(self):
        self.game.turn()
        card_sprite = self.createCard(self.game.board[3])
        end = self.board_pos[3]
        self.animateCard(self.deck_pos, end, card_sprite)

        self.ui.checkcallButton.setText("Check")
        self.ui.betraiseButton.setText("Bet")
        self.game.start_round()
        self.nextTurn()

        print(self.game.board)

    def river(self):
        self.game.river()
        card_sprite = self.createCard(self.game.board[4])
        end = self.board_pos[4]
        self.animateCard(self.deck_pos, end, card_sprite)

        self.ui.checkcallButton.setText("Check")
        self.ui.betraiseButton.setText("Bet")
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

#=================================================#
#===============POKER LOGIC CLASS=================#
#=================================================#

class Poker:
    def __init__(self):
        self.deck = Deck() # We need the deck of course.
        self.name = "Player" # ID for Player essentially
        self.playerHand = Hand() # We need the player hand of course.
        self.bestHand = [] # Keeps track of player's best hand.
        self.handRank = 0 # Holds hand rank in comparison to other players.
        self.stake = 0 # Holds chips the player has bet for a given round.
        self.board = [] # Keeps track of cards in center.
        self.oppNo = 0 # We need to know how many opponents we have in order to make that many later.
        self.opps = [] # Holds Opponent instances.
        self.turn_index = 0 # Keeps track of who's turn in Poker it is.
        self.players = [] # Full list of players, user and opponents.
        self.checked = 0 # Keeps track of how many people have passed without betting/raising.
        self.started = False # Keeps track of whether the Poker instance is fresh.
        self.activeBet = False # We need to know if a bet is currently occurring.
        self.folded = False # This will likely be valuable in interrupting gameflow.

    # Method creates opponents at the start of a fresh instance of Poker.
    def createOpponents(self, game):
        names = ["Super Macho Man", "King Hippo", "Glass Joe"]
        for i in range(self.oppNo):
            self.opps.append(Opponent(names[i], game, i))
            self.opps[i].chipTotal = random.randint(15, 25) * 50
        self.players = ['Player'] + self.opps

    def removeOpponents(self):
        for opp in self.opps:
            if opp.chipTotal <=0:
                opp.deactivate()
                self.opps.remove(opp)
                self.oppNo -= 1
        self.players = ['Player'] + self.opps

    # Method to deal initial two cards to a given player.
    def deal(self):
        self.started = True
        self.stake += 50 # Ante
        self.playerHand.add(self.deck.draw())
        self.playerHand.add(self.deck.draw())

        for i in range(len(self.opps)):
            if self.opps[i].active == True:
                print(f"{self.opps[i].name} gets dealt.")
                self.opps[i].stake += 50
                self.opps[i].oppHand.add(self.deck.draw())
                self.opps[i].oppHand.add(self.deck.draw())

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
        print(f"Player {index} is checking...")
        self.checked += 1
        # TO DO: ???
            # THIS METHOD MAY BE COMPLETE I'M NOT SURE.

    def call(self, index=0):
        print("Calling...")
        self.check(index)
        
        # TO DO: IMPLEMENT CALL METHOD FURTHER.
        # BIG IDEA: FIND LARGEST STAKE OF PLAYERS AND MATCH IT.

    def bet(self, index=0):
        print("Betting...")
        self.activeBet = True
        if index == 0:
            self.stake += 50
        else:
            if self.opps[index-1].chipTotal > 0:
                self.opps[index-1].stake += 50
            else:
                self.check(index)
        
        
        # TO DO: IMPLEMENT BET METHOD FURTHER.
        # BIG IDEA: INCREASE STAKE OF CALLER BY 50 AND SET self.activeBet TO TRUE
            # THIS MEANS CHANGING SOME UI ELEMENTS TO REFLECT A BET IS OCCURRING

    def _raise(self, index=0):
        print("Raising...")
        self.check(index)

        # TO DO: IMPLEMENT RAISE METHOD
        # BIG IDEA: FIND LARGEST STAKE OF PLAEYRS AND INCREASE IT BY 50.
            # MIGHT NEED TO KEEP BETACTIVE? NOT CONFIDENT THOUGH.

    def fold(self, index=0):
        print(f"Player {index} is folding...")
        self.checked += 1

        # Deduct the stake from player chips if player is human (index 0)
        if index == 0:
            self.folded = True
            self.playerHand = Hand()  # clear player's hand
            self.stake = 0
        else:
            # Clear opponent hand and stake
            self.players[index].folded = True
            self.players[index].oppHand = Hand()
            self.players[index].stake = 0

    def allIn(self):
        print("GOING ALL IN!!!")
        # TO DO: IMPLEMENT ALL IN METHOD
        # BIG IDEA: RAISE OR BET WITH FULL CHIP TOTAL AS THE AMOUNT.
            # RAISE OR BET WILL DEPEND ON IF A BET IS ACTIVE.

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
        self.removeOpponents()
        for i in range(1, len(self.players)):
            self.players[i].stake = 0
            self.players[i].oppHand = Hand()

    def analyzeHand(self):
        hand_type, best_hand = self.playerHand.getBestHand(self.board)
        return hand_type, best_hand