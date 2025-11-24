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
        self.roundText = ''
        self.actionBox = QMessageBox()
        self.actionBox.setWindowTitle("Round Summary")
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
        if hidden:
            path = os.path.join(CARDS_DIR, "card_back.jpg")
        else:
            path = os.path.join(CARDS_DIR, "" + str(card.rank) + "_of_" + card.suit + ".png")
        #print(path)
        pixmap = QPixmap(path).scaled(71, 111)
        return pixmap

    '''
    Handles animation of a card. Takes in starting postiion, ending poisition, and pixmap.
    '''
    def animateCard(self, start, end, pixmap):
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
            #print(f"Animating to {self.game.opps[i].name}")
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
    """
    Enables buttons once the game begins
    """
    def enablePlayerActions(self, enable):
        self.ui.leaveButton.setEnabled(enable)
        self.ui.checkcallButton.setEnabled(enable)
        self.ui.betraiseButton.setEnabled(enable)
        self.ui.foldButton.setEnabled(enable)
        self.ui.allinButton.setEnabled(enable)

#=================== POKER GUI GAME STATE TRACKING ===================#
    """
    Updates the game pot to be the total of everyone's bets
    """
    def updatePot(self):
        self.pot = self.game.stake
        for i in range(self.game.oppNo):
            self.pot += self.game.opps[i].stake
        self.ui.potLabel.setText(f'Pot: {self.pot}')

    """
    Updates the pot, checks the correct buttons to display, checks to see if the 
    game is still going, and then performs actions based on the player state
    """
    def nextTurn(self):
        # Update pot.
        self.pot = self.game.stake
        for i in range(len(self.game.opps)):
            self.pot += self.game.opps[i].stake
        self.ui.potLabel.setText(f'Pot: {self.pot}')

        if self.game.activeBet:
            self.ui.checkcallButton.setText("Call")
            self.ui.betraiseButton.setText("Raise")
        else:
            self.ui.checkcallButton.setText("Check")
            self.ui.betraiseButton.setText("Bet")

        if len(self.game.activePlayers) == 1:
            self.actionBox.setText(self.roundText)
            self.actionBox.exec()
            self.roundText = ''
            self.gameOver()
            return

        if self.game.checked == len(self.game.activePlayers):
            self.endRound()
            return

        current_turn = self.game.turn_index
        self.game.turn_index = (self.game.turn_index + 1) % (self.game.oppNo + 1)
        if current_turn == 0: # Player turn
            if self.game.folded:
                self.actionBox.setText(self.roundText)
                if len(self.game.board) == 3:
                    self.actionBox.exec()
                self.roundText = ''
                self.nextTurn()
            elif self.game.skip:
                self.actionBox.setText(self.roundText)
                if len(self.game.board) == 3:
                    self.actionBox.exec()
                self.roundText = ''
                self.game.checked += 1
                self.nextTurn()
            else:
                self.actionBox.setText(self.roundText)
                if len(self.game.board) != 3:
                    self.actionBox.exec()
                self.roundText = ''
                self.enablePlayerActions(True)
        else:
            self.enablePlayerActions(False)
            if self.game.opps[current_turn-1].folded or not self.game.opps[current_turn-1].active:
                self.nextTurn()
            else:
                #QTimer.singleShot(1500, Qt.TimerType.PreciseTimer, lambda: self.opponentTurn(current_turn))
                self.opponentTurn(current_turn)

        self.updatePot()

    """
    When an Opponent's turn happens, make a decision and re-evaluate how many chips
    the opponent has
    """
    def opponentTurn(self, index):
        action = self.game.opps[index-1].decision(index)
        self.roundText += f"{self.game.opps[index-1]} {action}.\n"
        self.oppWidgets[index+2].setText(f'Chip: {self.game.opps[index-1].chipTotal - self.game.opps[index-1].stake}')
        self.nextTurn()

    """
    Progress the game to the next round or finish the game, reset who checked and 
    if there was a bet placed
    """
    def endRound(self):
        if self.game.folded or self.game.skip:
            self.actionBox.setText(self.roundText)
            self.actionBox.exec()
            self.roundText = ''
        self.enablePlayerActions(False)
        self.game.checked = 0
        self.game.activeBet = False

        if len(self.game.board) == 3:
            self.turn()
        elif len(self.game.board) == 4:
            self.river()
        else:
            self.gameOver()

    """
    Syncs the current chips of the non-player opponents to their current amount
    """
    def sync_opponents_to_ui(self):
        self.ui.oppCount.blockSignals(True)
        self.ui.oppCount.setValue(self.game.oppNo)
        self.ui.oppCount.blockSignals(False)
        for i in range(3):
            self.oppWidgets[i].hide()
            self.oppWidgets[i+3].hide()
            self.oppWidgets[i+3].setText("Chips:")
        for i, opp in enumerate(self.game.opps):
            if opp.active:
                self.oppWidgets[i].show()
                self.oppWidgets[i+3].show()
            remaining_chips = opp.chipTotal - opp.stake
            self.oppWidgets[i+3].setText(f'Chips: {remaining_chips}')

    """
    Checks who won the game, awards chips to the winner and sends a message
    """
    def gameOver(self):
        winner, handRank = self.game.get_results()
        #print("Winning index is", winner)
        for i in range(len(self.game.players)):
            if winner == i and i == 0:
                winner = "Player"
                self.state.chips -= self.game.stake
                self.state.chips += self.pot
                self.ui.totalLabel.setText(f'Chip Total: {self.state.chips}')
            elif winner == i:
                winner = self.game.players[winner]
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

        if winner == "Player":
            QMessageBox.information(self, "Winner", f"{winner} wins with a {handRank}.")
        else:
            for card in winner.oppHand.hand:
                if card.rank == 11:
                    card.rank = "J"
                elif card.rank == 12:
                    card.rank = "Q"
                elif card.rank == 13:
                    card.rank = "K"
                elif card.rank == 14:
                    card.rank = "A"
            QMessageBox.information(self, "Winner", f"{winner} wins with a {handRank}.\nHand: {winner.oppHand.hand}")

        if self.state.chips <= 0:
            QMessageBox.information(self, "Game Over", "You're out of chips! Returning to main menu.")
            self.switch_to_menu.emit()
            return

        self.game.removeOpponents()
        for i in range(len(self.game.opps)):
            if not self.game.opps[i].active:
                index = self.game.opps[i].id - 1
                print(f"Removing {self.game.opps[i].name}")
                self.oppWidgets[index].hide()
                self.oppWidgets[index+3].hide()

        self.reset()
        self.sync_opponents_to_ui()

        inactive_ct = 0
        for opp in self.game.opps:
            if not opp.active:
                inactive_ct += 1
        if self.game.oppNo == inactive_ct:
            QMessageBox.information(self, "You Win!", "No Other Opponents have Chips. Congrats!")
            self.leave()

    """
    resets game board UI and state to the beginning of another game
    """
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
        QTimer.singleShot(1000, Qt.TimerType.PreciseTimer, lambda: self.ui.dealButton.setEnabled(True))
        self.enablePlayerActions(False)
        self.ui.leaveButton.setEnabled(True)

#=================== POKER GUI BUTTON ACTIONS ===================#

    """
    Controls the player's ability to check to call on a bet
    """
    def checkorcall(self):
        if self.game.activeBet:
            # There’s a bet, so the player should call instead
            if self.state.chips < self.game.stake + self.game.minbet:
                QMessageBox.information(self, "Out of Chips", "You are out of chips")
                self.game.check(0)
            else:
                self.game.call(0)
                self.ui.totalLabel.setText(f"Chip Total: {self.state.chips - self.game.stake}")

        else:
            # No bet, player can just check
            self.game.check(0)
        self.nextTurn()

    """
    Controls the bet/raise button allowing player to place and raise bets
    """
    def betorraise(self):
        if self.game.activeBet:
            if self.state.chips < self.game.stake + self.game.minbet + 50:
                QMessageBox.information(self, "Out of Chips", "You are out of chips")
                self.game.check(0)
            else:
                self.game._raise(0)
                self.ui.totalLabel.setText(f"Chip Total: {self.state.chips - self.game.stake}")

        else:
            if self.state.chips < self.game.stake + 50:
                QMessageBox.information(self, "Out of Chips", "You are out of chips")
                self.game.check(0)
            else:
                self.game.bet()
                self.ui.totalLabel.setText(f"Chip Total: {self.state.chips - self.game.stake}")

        self.nextTurn()
    
    """
    Controls the player ability to fold forfeiting the game
    """
    def fold(self):
        #self.state.chips -= self.game.stake
        self.game.fold(0)  # 0 = human player
        self.nextTurn()

    """
    Allows player to go all in, betting their remaining chips
    """
    def allIn(self):
        self.game.allIn(self.state.chips)
        self.ui.totalLabel.setText(f"Chip Total: {self.state.chips - self.game.stake}")

        self.nextTurn()

#=================== POKER GAME FLOW ANIMATIONS ===================#

    """
    Carries out the flop, the first round of poker
    """
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

    """
    responsible for executing the second part of a game of poker
    """
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

    """
    Responsible for carrying out the third part of a poker game
    """
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

    """
    Leave the game to the main menu
    """
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
        self.activePlayers = []
        self.checked = 0 # Keeps track of how many people have passed without betting/raising.
        self.started = False # Keeps track of whether the Poker instance is fresh.
        self.activeBet = False # We need to know if a bet is currently occurring.
        self.folded = False # This will likely be valuable in interrupting gameflow.
        self.minbet = 50 # Keeps track of largest bet that players must match.
        self.skip = False # Keeps track of when player can be skipped (e.g. during an All-In)
    """
    Method creates opponents at the start of a fresh instance of Poker.
    """
    def createOpponents(self, game):
        names = ["Super Macho Man", "King Hippo", "Glass Joe"]
        for i in range(self.oppNo):
            self.opps.append(Opponent(names[i], game, i))
            self.opps[i].chipTotal = random.randint(15, 25) * 50
        self.players = ['Player'] + self.opps
        for player in self.players:
            self.activePlayers.append(player)
    """
    Checks to see if opponents still have chips and removes them if not
    """
    def removeOpponents(self):
        for opp in self.opps:
            if opp.chipTotal <=0:
                opp.active = False

    """
    Method to deal initial two cards to a given player.
    """
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

    """
    Starts round with player's turn
    """
    def start_round(self):
        self.turn_index = 0

    """
    Moves the turn index forward to the next player
    """
    def next_turn(self):
        self.turn_index = (self.turn_index + 1) % len(self.players)

    """
    Starts the game by drawing three cards to the table
    """
    def flop(self):
        self.board.append(self.deck.draw())
        self.board.append(self.deck.draw())
        self.board.append(self.deck.draw())

    """
    Moves to the next round by adding one more card to the table
    """
    def turn(self):
        self.board.append(self.deck.draw())

    """
    Adds one final card to the table
    """
    def river(self):
        self.board.append(self.deck.draw())

    """
    Game method moves turn to next player without betting any chips. ends round if everyone
    checks
    """
    def check(self, index=0):
        print(f"Player {index} is checking...")
        self.checked += 1

    """
    Game method matches the highest bet
    """
    def call(self, index=0):
        print("Calling...")
        self.checked += 1
        if index == 0:
            self.stake = self.minbet
        else:
            if self.opps[index-1].chipTotal > self.minbet:
                self.opps[index-1].stake = self.minbet
            else:
                self.opps[index-1].stake = self.opps[index-1].chipTotal

    """
    Game method to bet chips, forcing the rest of the players to call or raise
    """
    def bet(self, index=0):
        print("Betting...")
        self.checked = 1
        self.activeBet = True
        self.minbet += 50
        if index == 0:
            self.stake = self.minbet
        else:
            if self.opps[index-1].chipTotal > self.minbet:
                self.opps[index-1].stake = self.minbet
            else:
                self.opps[index-1].stake = self.opps[index-1].chipTotal
        
    """
    Game method to raise the minimum bet and bet that amount
    """
    def _raise(self, index=0):
        print("Raising...")
        self.checked = 1
        self.activeBet = True
        self.minbet += 50
        if index == 0:
            self.stake = self.minbet
        else:
            if self.opps[index-1].chipTotal > self.minbet:
                self.opps[index-1].stake = self.minbet
            else:
                self.opps[index-1].stake = self.opps[index-1].chipTotal

    """
    Game method to remove the person from the round 
    """
    def fold(self, index=0):
        print(f"Player {index} is folding...")

        # Deduct the stake from player chips if player is human (index 0)
        if index == 0:
            self.folded = True
            self.playerHand = Hand()  # clear player's hand
            self.activePlayers.remove('Player')
        else:
            # Clear opponent hand and stake
            self.players[index].folded = True
            self.players[index].oppHand = Hand()
            #self.players[index].chipTotal -= self.players[index].stake
            self.activePlayers.remove(self.players[index])

    """
    Game methond to bet all the remaining chips a player has
    """
    def allIn(self,chips):
        print("GOING ALL IN!!!")
        self.checked = 1
        self.minbet = chips
        self.stake = self.minbet
        self.activeBet = True
        self.skip = True
        # TO DO: IMPLEMENT ALL IN METHOD
        # BIG IDEA: RAISE OR BET WITH FULL CHIP TOTAL AS THE AMOUNT.
            # RAISE OR BET WILL DEPEND ON IF A BET IS ACTIVE.

    """
    Game method to calculate who has the best hand and find the winner
    """
    def get_results(self):
        print("Ending game...")

        handRanks = [
                "High Card", "Pair", "Two Pair", "Three of a Kind", "Straight",
                 "Flush", "Full House", "Four of a Kind", "Straight Flush", "Royal Flush"
        ]

        if len(self.activePlayers) == 1:
            if self.activePlayers[0] == "Player":
                self.handRank, self.bestHand = self.analyzeHand()
                return self.players.index(self.activePlayers[0], self.handRank)
            else:
                hand_rank, best_hand = self.activePlayers[0].oppHand.getBestHand(self.board)
                return self.players.index(self.activePlayers[0]), hand_rank
        
        self.handRank, self.bestHand = self.analyzeHand()

        bestRank = handRanks.index(self.handRank)
        bestCombo = self.bestHand
        bestPlayerIndex = 0

        for i in range(1, len(self.players)):
            # Compare poker hands by higher index.
            if self.players[i] not in self.activePlayers:
                continue
            if handRanks.index(self.players[i].handRank) > bestRank:
                bestRank = handRanks.index(self.players[i].handRank)
                bestCombo = self.players[i].bestHand
                bestPlayerIndex = i
            elif handRanks.index(self.players[i].handRank) == bestRank: # In tie breaker case, we go by highest value card.
                if sorted([card.rank for card in self.players[i].bestHand], reverse=True) > sorted([card.rank for card in bestCombo], reverse=True):
                    bestCombo = self.players[i].bestHand
                    bestPlayerIndex = i
        return bestPlayerIndex, handRanks[bestRank]

    """
    Resets game state to new round
    """
    def reset(self):
        self.deck.shuffle()
        self.playerHand = Hand()

        self.bestHand = []
        self.bestRank = 0
        self.stake = 0
        self.minbet = 50
        self.board = []
        self.turn_index = 0
        self.checked = 0
        self.activeBet = False
        self.folded = False
        self.skip = False
        self.removeOpponents()
        self.activePlayers = []
        for i in range(len(self.players)):
            if i == 0:
                self.activePlayers.append(self.players[i])
            else:
                if self.players[i].active:
                    self.activePlayers.append(self.players[i])
        for i in range(1, len(self.players)):
            self.players[i].folded = False
            self.players[i].stake = 0
            self.players[i].oppHand = Hand()

    """
    Game method looks at hand and finds the best combination of cards with the cards on 
    the table
    """
    def analyzeHand(self):
        hand_type, best_hand = self.playerHand.getBestHand(self.board)
        return hand_type, best_hand