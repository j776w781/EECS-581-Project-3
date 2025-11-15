'''
File: sabaac.py

Authors: Joshua Welicky, Gavin Billinger, Mark Kitchin, Max Biundo, Bisshoy Bhattacharjee

Description:
Stores the Sabaac class, which handles game logic related to Sabaac, and SabaacScreen class,
which renders the GUI and effects the moves ordained by the Sabaac class.

Inputs: player_chips, the number of initial player chips.

Outputs: Functional GUI for Sabaac.
'''
from .objects.sabaac_deck import Sabaac_Deck
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

        self.state = state
        self.game = Sabaac()


    def leave(self):
        self.switch_to_menu.emit()


class SabaacAI:
    '''
    Class: SabaacAI

    Description:
    Handles the AI logic for Sabaac.

    Methods:
    make_move: Determines the AI's move based on its hand and the game state.
    '''

    def __init__(self, name, position, difficulty):
        self.name = name
        self.position = position
        self.difficulty = difficulty
        self.hand = []
        self.numchips = random.randint(50, 2000)

    def calc_hand_value(self):
        total_value = 0
        for card in self.hand:
            total_value += card.rank
        return total_value
    
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

    def make_move(self, num_round):
        '''
        Method: make_move

        Description:
        Determines the AI's move based on its hand.

        Inputs:
        round_num: The current round number.

        Outputs:
        None
        '''
        checkHand = self.calc_hand_value()
        checkDiscardValue = Sabaac.discard_pile[len(Sabaac.discard_pile)-1].rank if len(Sabaac.discard_pile) > 0 else None
        optimalSwap = self.checkSwapOptions(self.hand, checkDiscardValue)
        if self.difficulty == "medium":
            if checkHand == 0:
                # AI decides to stand with a perfect hand
                Sabaac.stand(self)
                return
            if optimalSwap != None:
                if num_round == 1 or abs(optimalSwap[1]) < 2:
                    Sabaac.swap(self, optimalSwap)
                    return
            if abs(checkHand) < 3:
                # AI decides to try and win with the current hand
                Sabaac.stand(self)
                return
            Sabaac.draw(self)
            


class Sabaac:
    '''
    Class: Sabaac

    Description:
    Handles the game logic for Sabaac.
    '''

    def __init__(self, num_players):
        self.pot = random.randint(100, 500)
        self.deck = Sabaac_Deck()
        self.discard_pile = []
        """Give position coordinates here once the GUI is set up"""
        positions = []
        self.players = [SabaacAI(f"AI Player {i+1}", positions[i], "medium") for i in range(num_players)]
        """Add user at base position when GUI is set up
        user = SabaacAI("User", (x/2, 2*y/3), "user")
        self.players.append(user)
        """

    def deal(self, player, num_cards=1):
        '''
        Method: deal

        Description:
        Deals a specified number of cards to a player.

        Inputs:
        player: The player to deal cards to.
        num_cards: The number of cards to deal (default is 1).

        Outputs:
        None
        '''
        for _ in range(num_cards):
            card = self.deck.draw_card()
            if card == None:
                self.deck.shuffle(self.discard_pile)
                self.discard_pile = []
                card = self.deck.draw_card()
            player.hand.append(card)
    
    def discard(self, player, card):
        '''
        Method: discard

        Description:
        Discards a specified card from a player's hand to the discard pile.

        Inputs:
        player: The player discarding the card.
        card: The card to be discarded.

        Outputs:
        None
        '''
        player.hand.remove(card)
        self.discard_pile.append(card)

    def game_setup(self):
        '''
        Method: game_setup

        Description:
        Sets up the game by dealing initial cards to players.

        Inputs:
        None

        Outputs:
        None
        '''
        for player in self.players:
            self.deal(player, 2)
    
    def round(self, num_round):
        '''
        Method: round

        Description:
        Executes a round of Sabaac, where each player makes a move.

        Inputs:
        None

        Outputs:
        None
        '''
        for player in self.players:
            if player.difficulty == "user":
                # Handle user input for move
                pass
            else:
                player.make_move(num_round)

    
