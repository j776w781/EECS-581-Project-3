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




class SabaccScreen(QWidget):
    switch_to_menu = pyqtSignal()

    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.ui = Ui_SabaccScreen()
        self.ui.setupUi(self)


        self.scene = QGraphicsScene(0,0,600,590, self)
        self.ui.graphicsView.setScene(self.scene)

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
        self.game = SabaccManager(self)
        """Position to place deck graphic on GUI. 180, 200 is center of scene."""
        self.deck_pos = QPointF(180, 200)
    
    def addDeckBack(self):
        deck_back_path = os.path.join(CARDS_DIR, "sabacc_deck_back.png")
        deck_back_pixmap = QPixmap(deck_back_path).scaled(80, 120)
        self.deck_item = self.scene.addPixmap(deck_back_pixmap)
        self.deck_item.setPos(self.deck_pos)

    def addDeckBackSideways(self):
        deck_back_path = os.path.join(CARDS_DIR, "sabacc_deck_back.png")
        deck_back_pixmap = QPixmap(deck_back_path).scaled(80, 120)
        self.deck_item = self.scene.addPixmap(deck_back_pixmap)
        self.deck_item.setPos(self.deck_pos)
        self.deck_item.setRotation(90)

    def addDeckBackSideways2(self):
        deck_back_path = os.path.join(CARDS_DIR, "sabacc_deck_back.png")
        deck_back_pixmap = QPixmap(deck_back_path).scaled(80, 120)
        self.deck_item = self.scene.addPixmap(deck_back_pixmap)
        self.deck_item.setPos(self.deck_pos)
        self.deck_item.setRotation(270)

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

    def roll_dice(self):
        self.ui.dice1.display(str(random.randint(1,6)))
        self.ui.dice2.display(str(random.randint(1,6)))
        print("Rolled Dice")
        print("Dice 1:", self.ui.dice1.value())
        print("Dice 2:", self.ui.dice2.value())

    

class SabaccManager:
    """Manages the overall Sabacc game control flow."""
    def __init__(self, screen):
        """Initializes the Sabacc pot at a random value between 100 and 1000."""
        self.screen = screen
        self.pot = random.randint(100, 1000)
        self.screen.ui.sabacc_pot.display(self.pot)
        self.startGameSequence()

    def startGameSequence(self):
        """Sets up the initial game state and prompts the user to select the number of opponents."""
        self.screen.ui.UserDialogBox.setPlainText("<-- Choose your number of opponents.")
        self.screen.ui.opponents1.setEnabled(True)
        self.screen.ui.opponents2.setEnabled(True)
        self.screen.ui.opponents3.setEnabled(True)
        self.num_opponents = 0
        self.screen.ui.opponents1.clicked.connect(lambda: self.numOpponents(1))
        self.screen.ui.opponents2.clicked.connect(lambda: self.numOpponents(2))
        self.screen.ui.opponents3.clicked.connect(lambda: self.numOpponents(3))


    def numOpponents(self, num):
        """Sets the number of opponents for the game and prompts the user to start the game."""
        self.num_opponents = num
        print("Number of Opponents Chosen:", self.num_opponents)
        self.screen.ui.UserDialogBox.setPlainText("<-- Press Start to begin the game.")
        self.screen.ui.StartButton.setEnabled(True)
        self.screen.ui.StartButton.clicked.connect(self.startGame)

    def startGame(self):
        """Starts the Sabacc game by initializing players and dealing initial hands."""
        self.screen.ui.StartButton.setEnabled(False)
        self.screen.ui.opponents1.setEnabled(False)
        self.screen.ui.opponents2.setEnabled(False)
        self.screen.ui.opponents3.setEnabled(False)
        self.screen.addDeckBack()
        self.players = []
        ai_names = ["Lando", "Han", "Leia"]
        if self.num_opponents == 1:
            ai_positions = [QPointF(260, 10)]
        elif self.num_opponents == 2:
            ai_positions = [QPointF(50, 20), QPointF(550, 400)]
        elif self.num_opponents == 3:
            ai_positions = [QPointF(260, 10), QPointF(50, 20), QPointF(550, 400)]
        for i in range(self.num_opponents):
            ai_player = SabaccAI(ai_names[i], ai_positions[i], "medium")
            self.players.append(ai_player)
            print(f"Added AI Opponent: {ai_names[i]} at position {ai_positions[i]}")
        user_player = SabaccPlayer("user", QPointF(260, 450), self.screen)
        self.players.append(user_player)
        print("Added User Player at position (260, 450) with chips:", self.screen.state.chips)
        self.game()

    def game(self):
        self.game = Sabacc(self.players, self.screen, self.pot)
        self.game.enter_game()
        self.game.game_setup()
        self.game.initialize_discard_pile()
        self.game.round(1)
        self.game.round(2)
        self.game.round(3)
        self.game.end_game()



class SabaccPlayer:
    """Represents a player in Sabacc.
    Input: name, position for GUI."""
    def __init__(self, name, position, screen):
        self.name = name
        self.position = position
        self.screen = screen
        self.hand = []
        self.numchips = self.screen.state.chips
        self.numchips_bet = 0
        self.out_of_game = False

    def calc_hand_value(self):
        total_value = 0
        for card in self.hand:
            total_value += card.rank
        return total_value
    
    def make_bet(self):
        betValue = 0
        betting = True
        self.screen.ui.UserDialogBox.append("Please place your bet by clicking the Bet buttons. When you are finished, press Start.")
        self.screen.ui.bet5.setEnabled(True)
        self.screen.ui.bet50.setEnabled(True)
        self.screen.ui.bet100.setEnabled(True)

        def bet5_clicked():
            nonlocal betValue
            if self.numchips - 5 >= 0:
                betValue += 5
                self.numchips -= 5
                self.screen.ui.UserDialogBox.append(f"You bet 5 chips. Total bet: {betValue}. Remaining chips: {self.numchips}")
            else:
                self.screen.ui.UserDialogBox.append("Not enough chips to bet 5.")

        def bet50_clicked():
            nonlocal betValue
            if self.numchips - 50 >= 0:
                betValue += 50
                self.numchips -= 50
                self.screen.ui.UserDialogBox.append(f"You bet 50 chips. Total bet: {betValue}. Remaining chips: {self.numchips}")
            else:
                self.screen.ui.UserDialogBox.append("Not enough chips to bet 50.")

        def bet100_clicked():
            nonlocal betValue
            if self.numchips - 100 >= 0:
                betValue += 100
                self.numchips -= 100
                self.screen.ui.UserDialogBox.append(f"You bet 100 chips. Total bet: {betValue}. Remaining chips: {self.numchips}")
            else:
                self.screen.ui.UserDialogBox.append("Not enough chips to bet 100.")

        self.screen.ui.bet5.clicked.connect(bet5_clicked)
        self.screen.ui.bet50.clicked.connect(bet50_clicked)
        self.screen.ui.bet100.clicked.connect(bet100_clicked)

        self.screen.ui.StartButton.setEnabled(True)
        self.screen.ui.StartButton.clicked.connect(lambda: self.finish_betting(betValue))

    def finish_betting(self, betValue):
        self.screen.ui.bet5.setEnabled(False)
        self.screen.ui.bet50.setEnabled(False)
        self.screen.ui.bet100.setEnabled(False)
        return betValue
    
    def make_move(self, game):
        self.screen.ui.UserDialogBox.append("Please make your move by clicking one of the action buttons.")
        self.screen.ui.drawButton.setEnabled(True)
        self.screen.ui.swapButton.setEnabled(True)
        self.screen.ui.standButton.setEnabled(True)
        self.screen.ui.junkButton.setEnabled(True)
        self.screen.ui.drawButton.clicked.connect(lambda: game.draw(self))
        self.screen.ui.swapButton.clicked.connect(lambda: game.swap(self))
        self.screen.ui.standButton.clicked.connect(lambda: game.stand(self))
        self.screen.ui.junkButton.clicked.connect(lambda: game.junk(self))

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
            if abs(possible_swaps[i][1]) < abs(track_best[1]):
                track_best = possible_swaps[i]
        if track_best[1] < abs(self.calc_hand_value()):
            return track_best
        else:
            return None

    """Determines and executes the AI's move based on its difficulty level and hand value.
    Inputs: current round number."""
    def make_move(self, num_round, discard_pile, game):
        checkHand = self.calc_hand_value()
        checkDiscardValue = discard_pile[len(discard_pile)-1].rank if len(discard_pile) > 0 else None
        optimalSwap = self.checkSwapOptions(self.hand, checkDiscardValue)
        if self.difficulty == "medium":
            if checkHand == 0:
                # AI decides to stand with a perfect hand
                game.stand(self)
                return
            if optimalSwap != None:
                if num_round == 1 or abs(optimalSwap[1]) < 2:
                    game.swap(self, optimalSwap)
                    return
            if abs(checkHand) < 3:
                # AI decides to try and win with the current hand
                game.stand(self)
                return
            if abs(checkHand) > 23 and num_round == 3:
                game.junk(self)
                return
            game.draw(self)
            return
            
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

    
    """Executes a round of moves and bets for all players.
    Inputs: current round number."""
    def round(self, num_round):
        self.screen.ui.UserDialogBox.setPlainText(f"<-- Round {num_round} in progress.")
        for player in self.players:
            self.screen.ui.UserDialogBox.append(f"{player.name}'s turn:")
            if player.name == "user":
                self.screen.ui.UserDialogBox.append("Please make your move.")
                player.make_move(self)
            else:
                sleep(2)
                if not player.out_of_game:
                    player.make_move(num_round, self.discard_pile, self)
                    print(f"{player.name} has finished their turn. Hand value: {player.calc_hand_value()}")
                sleep(2)
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
                    betValue = player.make_bet()
                    self.gamePot += betValue
                    self.screen.ui.gamePot.display(self.gamePot)
                    print(f"User bets {betValue}. Remaining chips: {player.numchips}")
            sleep(1)
        print(f"Round {num_round} complete. Game pot is now: {self.gamePot}")
            

    
