'''
File: sabaac.py

Authors: Joshua Welicky, Gavin Billinger, Mark Kitchin, Max Biundo, Bisshoy Bhattacharjee

Description:
Stores the Sabaac class, which handles game logic related to Sabaac, and SabaacScreen class,
which renders the GUI and effects the moves ordained by the Sabaac class.

Inputs: player_chips, the number of initial player chips.

Outputs: Functional GUI for Sabaac.
'''
from time import sleep
from .objects.sabacc_deck import Sabacc_Deck
from .objects.deck import AnimatedCard
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
OPPS_DIR = os.path.join(BASE_DIR, "../assets/sabacc_ops/")




class SabaccScreen(QWidget):
    switch_to_menu = pyqtSignal()

    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.ui = Ui_SabaccScreen()
        self.ui.setupUi(self)

        self.scene = QGraphicsScene(0,0,600,590, self)
        self.ui.graphicsView.setScene(self.scene)

        self.ui.deckback.setPixmap(QPixmap(os.path.join(CARDS_DIR, "sabacc_deck_back.png")))
        self.ui.han.setPixmap(QPixmap(OPPS_DIR + "han.png"))
        self.ui.chewie.setPixmap(QPixmap(OPPS_DIR + "chewbacca.jpg"))
        self.ui.lando.setPixmap(QPixmap(OPPS_DIR + "lando.png"))

        #Disable all buttons except leave and rules until game starts
        self.ui.drawButton.setEnabled(False)
        self.ui.swapButton.setEnabled(False)
        self.ui.standButton.setEnabled(False)
        self.ui.junkButton.setEnabled(False)
        self.ui.bet5.setEnabled(False)
        self.ui.bet50.setEnabled(False)
        self.ui.bet100.setEnabled(False)
        self.ui.card1.setEnabled(False)
        self.ui.card2.setEnabled(False)
        self.ui.card3.setEnabled(False)
        self.ui.card4.setEnabled(False)
        self.ui.card5.setEnabled(False)
        self.ui.StartButton.setEnabled(False)
        self.ui.opponents1.setEnabled(False)
        self.ui.opponents2.setEnabled(False)
        self.ui.opponents3.setEnabled(False)
        self.ui.dice1.display("-")
        self.ui.dice2.display("-")
        self.ui.leaveButton.clicked.connect(self.leave)
        self.ui.rules.clicked.connect(self.show_rules)


        self.state = state
        self.deck_pos = QPointF(180, 200)

    def show_rules(self):
        rules = (
                "Sabacc Rules:\n"
                "10 Chip buy in to enter the game.\n"
                "1. Each player is dealt two cards.\n"
                "2. Players take turns to draw a card, swap for the card at the top of the discard pile, stand (pass to the next player), or junk (forfeit the game).\n"
                "2.5. Players may choose to discard a card after drawing."
                "3. The goal is to have a hand value closest to zero.\n"
                "4. Positive and negative cards affect hand value.\n"
                "5. The game continues for 3 rounds.\n"
                "5.5. Players bet after every round.\n"
                "6. The player with the hand value closest to zero wins the money bet after each round."
                "7. If a player wins with exactly 0, they win the pot.\n"
        )
        QMessageBox.information(self, "Sabacc Rules", rules)
        print("Displayed Sabacc Rules")


    def leave(self):
        self.switch_to_menu.emit()




    
















































































































































class Sabacc:
    """Represents a Sabacc game.
    Input: list of player objects, game screen."""
    def __init__(self, players, screen, pot):
        self.deck = Sabacc_Deck()
        self.discard_pile = []
        self.players = players
        self.screen = screen
        self.pot = pot
        self.gamePot = 0

    """Gives the discard pile its initial card from the deck."""
    def initialize_discard_pile(self):
        card = self.deck.draw_card()
        if card:
            self.discard_pile.append(card)
        print("Initialized discard pile with card:", card)

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
        new_card = self.discard_pile.pop()
        player.hand.append(new_card)
        self.discard_pile.append(card_to_swap)
        print(f"{player.name} swapped {card_to_swap} with {new_card}.")

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
        print(f"{player.name} has junked their hand and is out of the game.")

    """Sets up the game by dealing initial hands to all players."""
    def game_setup(self):
        for player in self.players:
            self.deal(player, 2)
        for player in self.players:
            print(f"{player.name}'s initial hand: {[str(card) for card in player.hand]}")
            print(f"{player.name} has total hand value: {player.calc_hand_value()}")

    def enter_game(self):
        for player in self.players:
            if player.numchips < 10:
                self.players.remove(player)
        for player in self.players:
            self.pot += 10
            player.numchips -= 10
        self.screen.ui.sabacc_pot.display(self.pot)
        print("Players have entered the game. Pot is now:", self.pot)

    """Determines and announces the winner of the game and distributes the pot."""
    def determine_winner(self):
        track_winner = None
        for player in self.players:
            if not player.out_of_game:
                if track_winner == None:
                    """Set the winner equal to the first player found who is not out of the game."""
                    track_winner = player
                elif abs(player.calc_hand_value()) < abs(track_winner.calc_hand_value()):
                    """Found a new winner with a hand value closer to zero."""
                    track_winner = player
                elif abs(player.calc_hand_value()) == abs(track_winner.calc_hand_value()):
                    """Found a player with the same hand value, check for positive rank win."""
                    if player.calc_hand_value() > track_winner.calc_hand_value():
                        track_winner = player
                    else:
                        """Found a player with the same hand value, check for fewer cards win."""
                        if len(player.hand) > len(track_winner.hand):
                            track_winner = player
                        else:
                            """Found a player with the same hand value and same number of cards, check for highest value card to break the tie."""
                            player.max_card = max(player.hand, key=lambda c: c.rank)
                            track_winner.max_card = max(track_winner.hand, key=lambda c: c.rank)
                            if player.max_card.rank > track_winner.max_card.rank:
                                track_winner = player
                            else:
                                """It's a complete tie, no winner."""
                                track_winner = None

    """Executes a round of moves and bets for all players.
    Inputs: current round number."""
    def round(self, num_round):
        self.screen.ui.UserDialogBox.setPlainText(f"<-- Round {num_round} in progress.")
        for player in self.players:
            print(f"{player.name}'s turn. Hand value: {player.calc_hand_value()}")
            if player.name == "user":
                self.screen.ui.UserDialogBox.append("Please make your move.")
                player.make_move(self, num_round)
            else:
                if not player.out_of_game:
                    player.make_move(num_round, self.discard_pile, self)
                    print(f"{player.name} has finished their turn. Hand value: {player.calc_hand_value()}")

    """Handles the betting phase after each round.
    Inputs: current round number."""
    def betting_phase(self, num_round):
        self.screen.ui.UserDialogBox.append(f"<-- Betting phase for Round {num_round}")
        for player in self.players:
            sleep(1)
            if not player.out_of_game and not player.name == "user":
                bet_amount = 10  # Placeholder for bet amount logic
                player.numchips -= bet_amount
                player.numchips_bet += bet_amount
                self.gamePot += bet_amount
                self.screen.ui.gamePot.display(self.gamePot)
                print(f"{player.name} bets {bet_amount}. Remaining chips: {player.numchips}")
            else:
                if player.name == "user":
                    print("Waiting for user to place bet...")
                    player.make_bet(self)