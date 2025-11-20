'''
File: sabaac.py

Authors: Joshua Welicky, Gavin Billinger, Mark Kitchin, Max Biundo, Bisshoy Bhattacharjee

Description:
Stores the Sabaac class, which handles game logic related to Sabaac, and SabaacScreen class,
which renders the GUI and effects the moves ordained by the Sabaac class.

Inputs: player_chips, the number of initial player chips.

Outputs: Functional GUI for Sabaac.
'''
from .objects.sabacc_deck import Sabacc_Deck
from PyQt6.QtWidgets import QWidget, QGraphicsScene, QGraphicsObject, QPushButton, QMessageBox
from PyQt6.QtCore import QPropertyAnimation, QRect, QPointF, QEasingCurve, QRectF, pyqtProperty, QTimer, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter
from .objects.opponent import Opponent
from .ui.sabacc_ui import Ui_SabaccScreen
import os
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARDS_DIR = os.path.join(BASE_DIR, "../assets/sabaac_cards")
CHIPS_DIR = os.path.join(BASE_DIR, "../assets")




class SabaccScreen(QWidget):
    switch_to_menu = pyqtSignal()

    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.ui = Ui_SabaccScreen()
        self.ui.setupUi(self)


        self.scene = QGraphicsScene(0,0,600,590, self)
        self.ui.graphicsView.setScene(self.scene)

        self.ui.leaveButton.clicked.connect(self.leave)
        self.ui.StartButton.clicked.connect(self.roll_dice)

        self.state = state
        self.game = SabaccManager()


    def leave(self):
        self.switch_to_menu.emit()

    def roll_dice(self):
        self.ui.dice1.display(str(random.randint(1,6)))
        self.ui.dice2.display(str(random.randint(1,6)))
        print("Rolled Dice")
        print("Dice 1:", self.ui.dice1.value())
        print("Dice 2:", self.ui.dice2.value())

    

class SabaccManager:
    """Manages the overall Sabacc game control flow."""

class SabaccAI:
    """Represents an AI player in Sabacc.
    Input: name, position for GUI, difficulty level."""
    def __init__(self, name, position, difficulty):
        self.name = name
        self.position = position
        self.difficulty = difficulty
        self.hand = []
        self.numchips = random.randint(50, 2000)
        self.numchips_bet = 0
        self.out_of_game = False

    """Calculates the total value of the AI's hand."""
    def calc_hand_value(self):
        total_value = 0
        for card in self.hand:
            total_value += card.rank
        return total_value
    
    """Checks possible swap options with the discard pile.
    Inputs: AI's hand, value of the top discard card.
    Outputs: The best swap option (card to swap, new hand value) or None if no beneficial swap exists."""
    def checkSwapOptions(self, hand, discard_value):
        possible_swaps = []
        for card in hand:
            new_hand_value = sum(c.rank for c in hand if c != card) + discard_value
            possible_swaps.append((card, new_hand_value))
        track_best = (None, 1000)
        for i in range(len(possible_swaps)):
            if abs(possible_swaps[i][1]) < abs(track_best):
                track_best = possible_swaps[i]
        if track_best[1] < abs(self.calc_hand_value(hand)):
            return track_best
        else:
            return None

    """Determines and executes the AI's move based on its difficulty level and hand value.
    Inputs: current round number."""
    def make_move(self, num_round):
        checkHand = self.calc_hand_value()
        checkDiscardValue = Sabacc.discard_pile[len(Sabacc.discard_pile)-1].rank if len(Sabacc.discard_pile) > 0 else None
        optimalSwap = self.checkSwapOptions(self.hand, checkDiscardValue)
        if self.difficulty == "medium":
            if checkHand == 0:
                # AI decides to stand with a perfect hand
                Sabacc.stand(self)
                return
            if optimalSwap != None:
                if num_round == 1 or abs(optimalSwap[1]) < 2:
                    Sabacc.swap(self, optimalSwap)
                    return
            if abs(checkHand) < 3:
                # AI decides to try and win with the current hand
                Sabacc.stand(self)
                return
            if num_round < 3:
                Sabacc.junk(self)
                return
            Sabacc.draw(self)
            return
            
class Sabacc:
    """Represents a Sabacc game.
    Input: number of players."""
    def __init__(self, num_players):
        self.pot = random.randint(100, 500)
        self.deck = Sabacc_Deck()
        self.discard_pile = []
        """Give position coordinates here once the GUI is set up"""
        positions = []
        self.players = [SabaccAI(f"AI Player {i+1}", positions[i], "medium") for i in range(num_players)]
        """Add user at base position when GUI is set up
        user = SabaccAI("User", (x/2, 2*y/3), "user")
        self.players.append(user)
        """

    """Deals a specified number of cards to a player.
    Inputs: player object, number of cards to deal (default is 1)."""
    def deal(self, player, num_cards=1):
        for _ in range(num_cards):
            card = self.deck.draw_card()
            if card == None:
                self.deck.shuffle(self.discard_pile)
                self.discard_pile = []
                card = self.deck.draw_card()
            player.hand.append(card)
    
    """Handles the discard action for a player.
    Inputs: player object, card to discard."""
    def discard(self, player, card):
        player.hand.remove(card)
        self.discard_pile.append(card)

    """Handles the draw action for a player.
    Inputs: player object."""
    def draw(self, player):
        self.deal(player, 1)
        choose_discard = False  # Placeholder for AI decision logic
        if choose_discard:
            card_to_discard = player.hand[0]  # Placeholder for AI decision logic
            self.discard(player, card_to_discard)

    """Handles the swap action for a player.
    Inputs: player object, swap option (card to swap)."""
    def swap(self, player, swap_option):
        card_to_swap = swap_option[0]
        player.hand.remove(card_to_swap)
        self.discard_pile.append(card_to_swap)
        new_card = self.discard_pile.pop()
        player.hand.append(new_card)

    """Handles the stand action for a player.
    Inputs: player object. Strictly for the format. No logic needed."""
    def stand(self, player):
        pass  # Implement stand logic
    
    """Handles the junk action for a player.
    Inputs: player object."""
    def junk(self, player):
        player.hand = []
        player.numchips_bet = 0
        player.out_of_game = True

    """Sets up the game by dealing initial hands to all players."""
    def game_setup(self):
        for player in self.players:
            self.deal(player, 2)
    
    """Executes a round of moves and bets for all players.
    Inputs: current round number."""
    def round(self, num_round):
        for player in self.players:
            if player.difficulty == "user":
                # Handle user input for move
                pass
            else:
                if not player.out_of_game:
                    player.make_move(num_round)

    
