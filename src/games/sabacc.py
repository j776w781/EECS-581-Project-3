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
from .ui.sabacc_ui import Ui_Form
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
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.scene = QGraphicsScene(0,0,600,590, self)
        self.ui.graphicsView.setScene(self.scene)

        self.ui.deckback.setPixmap(QPixmap(os.path.join(CARDS_DIR, "sabacc_deck_back.png")))
        self.ui.han.setPixmap(QPixmap(OPPS_DIR + "han.png"))
        self.ui.chewie.setPixmap(QPixmap(OPPS_DIR + "chewbacca.jpg"))
        self.ui.lando.setPixmap(QPixmap(OPPS_DIR + "lando.png"))

        #Disable all buttons except leave and rules until game starts
        self.ui.drawButton.setEnabled(False)
        self.ui.drawButton.clicked.connect(self.draw)
        self.ui.swapButton.setEnabled(False)
        self.ui.swapButton.clicked.connect(self.swap)
        self.ui.standButton.setEnabled(False)
        self.ui.standButton.clicked.connect(self.stand)
        self.ui.junkButton.setEnabled(False)
        self.ui.junkButton.clicked.connect(self.junk)
        self.ui.bet5.setEnabled(False)
        self.ui.bet50.setEnabled(False)
        self.ui.bet100.setEnabled(False)
        self.ui.card1.setEnabled(False)
        self.ui.card2.setEnabled(False)
        self.ui.card3.setEnabled(False)
        self.ui.card4.setEnabled(False)
        self.ui.card5.setEnabled(False)
        self.ui.StartButton.setEnabled(True)
        self.ui.dice1.display("-")
        self.ui.dice2.display("-")
        self.ui.leaveButton.clicked.connect(self.leave)
        self.ui.rules.clicked.connect(self.show_rules)
        self.ui.oppcount.valueChanged.connect(self.refreshOpps)
        self.ui.StartButton.clicked.connect(self.begin_game)


        self.state = state
        self.deck_pos = QPointF(180, 200)

        self.card_buttons = [self.ui.card1, self.ui.card2, self.ui.card3, self.ui.card4, self.ui.card5]
        self.card_pos = [QPointF(100, 420), QPointF(185, 420), QPointF(270, 420), QPointF(355, 420), QPointF(440, 420)]

        self.discard_widgets = []


        self.oppstuff = [self.ui.lando, self.ui.han, self.ui.chewie, self.ui.Landochips, self.ui.Hanchips, self.ui.Chewbaccachips]
        self.opp_positions = [QPointF(320, 15), QPointF(515, 90), QPointF(-70, 90)]
        self.opponents = self.initializeOpponents()
        self.refreshOpps(3)

        self.player = SabaccPlayer("user", self.state.chips)

        players = []
        for opp in self.opponents:
            players.append(opp)
        players.append(self.player)
        self.game = Sabacc(players, 200323)

        



    def initializeOpponents(self):
        opponents = []
        ai_names = ["Lando", "Han", "Chewbacca"]
        for i in range(3):
            ai_player = SabaccAI(ai_names[i], self.opp_positions[i], "medium")
            opponents.append(ai_player)
            #print(f"Added AI Opponent: {ai_names[i]} at position {self.opp_positions[i]}")
            self.ui.__getattribute__(f"{ai_names[i]}chips").setText(f'Chips: {ai_player.numchips}')
        return opponents




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
        #print("Displayed Sabacc Rules")



    def reset(self, hard=False):
        self.scene.clear()
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
        self.ui.StartButton.setEnabled(True)
        self.ui.dice1.display("-")
        self.ui.dice2.display("-")
        self.ui.oppcount.setEnabled(True)
        for button in self.card_buttons:
            try:
                button.clicked.disconnect()
            except TypeError:
                pass

        self.discard_widgets = []

        if hard:
            self.ui.opplabel.show()
            self.ui.oppcount.show()
            self.ui.oppcount.setValue(3)

            self.opponents = self.initializeOpponents()
            self.refreshOpps(3)

            self.player = SabaccPlayer("user", self.state.chips)
            players = []
            for opp in self.opponents:
                players.append(opp)
            players.append(self.player)

            self.game = Sabacc(players, 200323)


    def leave(self):
        self.reset(True)
        self.switch_to_menu.emit()


    def refreshOpps(self, oppcnt):
        for i in range(3):
            if i < oppcnt:
                self.oppstuff[i].show()
                self.oppstuff[i+3].show()
                self.opponents[i].defeated = False
            if i >= oppcnt:
                self.oppstuff[i].hide()
                self.oppstuff[i+3].hide()
                self.opponents[i].defeated = True
        #self.game.oppNo = value


    '''
    Helpful function for obtaining the proper pixmap for a Card instance, based
    on rank, suit, and if its hidden.
    '''
    def createCard(self, card, hidden=False):
        #print("Creating cards...")
        if hidden:
            path = os.path.join(CARDS_DIR, "sabacc_deck_back.png")
        else:
            path = os.path.join(CARDS_DIR, "" + card.getName())
        #print(path)
        pixmap = QPixmap(path).scaled(80, 120)
        return pixmap

    '''
    Handles animation of a card. Takes in starting postiion, ending poisition, and pixmap.
    '''
    def animateCard(self, start, end, pixmap):
        #print("Animating cards...")
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


    def updateDiscard(self, pos, deck_idx=-1):
        if deck_idx < 0:
            deck_idx = len(self.game.discard_pile)-1
        card_sprite = self.createCard(self.game.discard_pile[deck_idx])
        self.discard_widgets.append(self.animateCard(pos, self.ui.discard_spot.pos(), card_sprite))


    def roll_dice(self):
        self.ui.dice1.display(str(random.randint(1,6)))
        self.ui.dice2.display(str(random.randint(1,6)))
        print("Rolled Dice")
        print("Dice 1:", self.ui.dice1.value())
        print("Dice 2:", self.ui.dice2.value())



    def deal(self):
        print("Dealing cards...")
        self.ui.oppcount.setEnabled(False)
        self.ui.opplabel.hide()
        self.ui.oppcount.hide()

        # Game deals cards.
        self.game.game_setup()

        # UI animates cards to player hand.
        for i, card in enumerate(self.player.hand):
            card_sprite = self.createCard(card)
            end = self.card_pos[i]
            self.player.hand_widgets[i]=self.animateCard(self.deck_pos, end, card_sprite)       

        # UI animates cards for each opponent
        for i in range(len(self.opponents)):
            #print(f"Animating to {self.opponents[i].name}")
            for j, card in enumerate(self.opponents[i].hand):
                card_sprite = self.createCard(card, True)
                end = self.opponents[i].position + QPointF(j * 20, 0)
                self.opponents[i].hand_widgets[j] = (self.animateCard(self.deck_pos, end, card_sprite))

        self.ui.StartButton.setEnabled(False)















    def round(self):
        report_str = ""
        i = 1
        for opp in self.opponents:
            if not opp.out_of_game and not opp.defeated:
                move = opp.make_move(self.game.round_num+1, self.game.discard_pile)
                report_str += f"{opp.name} chose to {move[0]}.\n"

                if move[0] == "draw":
                    #print(f"Calling draw for {opp}")
                    QTimer.singleShot(1000 * i, lambda a=opp: self.draw(ai=a))
                    i+=1
                elif move[0] == "swap":
                    QTimer.singleShot(1000 * i, lambda m=move, a=opp: self.swap_helper(m[1], a))
                    i+=1
                elif move[0] == "junk":
                    QTimer.singleShot(1000*i, lambda a=opp: self.junk(a))
                    i+=1
                else:
                    QTimer.singleShot(1000*i, lambda a=opp: self.stand(a))
            
        QTimer.singleShot(1000*i, lambda s=report_str: QMessageBox.information(self, "Opponents' Moves", s))
        #Let the AI do what it needs to do.
        #Effectuate changes

        QTimer.singleShot(1000*i, lambda: self.ui.drawButton.setEnabled(True))
        QTimer.singleShot(1000*i, lambda: self.ui.swapButton.setEnabled(True))
        QTimer.singleShot(1000*i, lambda: self.ui.junkButton.setEnabled(True))
        QTimer.singleShot(1000*i, lambda: self.ui.standButton.setEnabled(True))


    

    def stand(self, ai=None):
        if ai:
            return
        else:
            #Deactivate the card buttons (Don't want to discard!)
            for i in range(len(self.player.hand)):
                try:
                    self.card_buttons[i].clicked.disconnect()
                except TypeError:
                    pass
                self.card_buttons[i].setEnabled(False)
            self.plays_over()






    def discard(self, cardnum, ai=None):
        if ai:
            return

        

        else:
            #print(f"discarding {cardnum}")
            #Disable further discarding.
            for i in range(len(self.player.hand)):
                try:
                    self.card_buttons[i].clicked.disconnect()
                except TypeError:
                    pass
                self.card_buttons[i].setEnabled(False)

            #update hand in game logic
            self.game.discard(self.player, cardnum)

            #animate discarding.
            self.updateDiscard(self.card_pos[cardnum])

            if cardnum == len(self.player.hand):
                self.scene.removeItem(self.player.hand_widgets[cardnum])
                self.player.hand_widgets[cardnum] = None
            else:
                self.scene.removeItem(self.player.hand_widgets[cardnum])
                self.scene.removeItem(self.player.hand_widgets[len(self.player.hand)])

                #Move furthest card over.
                card_sprite = self.createCard(self.player.hand[len(self.player.hand)-1])
                start = self.card_pos[len(self.player.hand)]
                end = self.card_pos[cardnum]
                self.player.hand_widgets[cardnum] = self.animateCard(start, end, card_sprite)
            
            self.plays_over()
            


    def draw(self, ai=None):
        if ai:
            #print(ai)
            #Add to the hand.
            self.game.draw(ai)
            #Animate the new card.
            card_sprite = self.createCard(ai.hand[len(ai.hand)-1], True)
            end = ai.position + QPointF((len(ai.hand)-1) * 20, 0)
            ai.hand_widgets[len(ai.hand)-1] = self.animateCard(self.deck_pos, end, card_sprite)

        else:
            #Deactivate buttons.
            self.ui.drawButton.setEnabled(False)
            self.ui.swapButton.setEnabled(False)
            self.ui.junkButton.setEnabled(False)
            self.ui.standButton.setEnabled(False)

            #Add to the hand.
            self.game.draw(self.player)

            #Animate the new card.
            card_sprite = self.createCard(self.player.hand[len(self.player.hand)-1])
            end = self.card_pos[len(self.player.hand)-1]
            self.player.hand_widgets[len(self.player.hand)-1] = self.animateCard(self.deck_pos, end, card_sprite)

            QMessageBox.information(self, "Discard?", "If you have a card you just can't use, now's the time! Just click it and it will go away.\nOtherwise CLICK STAND.")

            #Enable available cards for discarding.
            for i in range(len(self.player.hand)):
                self.card_buttons[i].setEnabled(True)
                try:
                    self.card_buttons[i].clicked.disconnect()
                except TypeError:
                    pass
                self.card_buttons[i].clicked.connect(lambda _, idx=i: self.discard(idx))
            
            #print(f"New hand: {self.player.hand}")
            self.ui.standButton.setEnabled(True)



    def swap_helper(self, cardnum, ai=None):
        if ai:
            print(f"Here I go for {ai.name}, who wants to swap card {cardnum}")
            self.scene.removeItem(ai.hand_widgets[cardnum])
            self.scene.removeItem(self.discard_widgets.pop())

            #Animate taking the discard card.
            card_sprite = self.createCard(self.game.discard_pile[len(self.game.discard_pile)-1])
            end = ai.position + QPointF(cardnum * 20, 0)
            ai.hand_widgets[cardnum] = self.animateCard(self.ui.discard_spot.pos(), end, card_sprite)
            if cardnum != len(ai.hand)-1:
                over = ai.hand_widgets[cardnum+1]
                ai.hand_widgets[cardnum].setZValue(over.zValue() - 1)

            #Animate giving up old card
            card_sprite = self.createCard(ai.hand[cardnum])
            start = ai.position + QPointF(cardnum * 20, 0)
            self.discard_widgets.append(self.animateCard(start, self.ui.discard_spot.pos(), card_sprite))

            self.game.swap(ai, cardnum)
            return
        
        else:
            #Disable further swapping
            for i in range(len(self.player.hand)):
                try:
                    self.card_buttons[i].clicked.disconnect()
                except TypeError:
                    pass
                self.card_buttons[i].setEnabled(False)
            
            #Remove old card widget.
            self.scene.removeItem(self.player.hand_widgets[cardnum])
            self.scene.removeItem(self.discard_widgets.pop())

            #Animate taking the discard card.
            card_sprite = self.createCard(self.game.discard_pile[len(self.game.discard_pile)-1])
            end = self.card_pos[cardnum]
            self.player.hand_widgets[cardnum] = self.animateCard(self.ui.discard_spot.pos(), end, card_sprite)

            #Animate giving up old card
            card_sprite = self.createCard(self.player.hand[cardnum])
            start = self.card_pos[cardnum]
            self.discard_widgets.append(self.animateCard(start, self.ui.discard_spot.pos(), card_sprite))

            self.game.swap(self.player, cardnum)
            #print(f"Hand after swap: {self.player.hand}")
            self.plays_over()


    def swap(self):
        #Deactivate buttons.
        self.ui.drawButton.setEnabled(False)
        self.ui.swapButton.setEnabled(False)
        self.ui.junkButton.setEnabled(False)
        self.ui.standButton.setEnabled(False)

        #Enable available cards for swapping.
        for i in range(len(self.player.hand)):
            self.card_buttons[i].setEnabled(True)
            try:
                self.card_buttons[i].clicked.disconnect()
            except TypeError:
                pass
            self.card_buttons[i].clicked.connect(lambda _, idx=i: self.swap_helper(idx))
        QMessageBox.information(self, "Swap", "Time to swap! Pick a card to give up. Hope that discard is worth it.")




    def junk(self, ai=None):
        if ai:
            hand_len = len(ai.hand)
            self.game.junk(ai)
            for i in range(hand_len-1, -1, -1):
                self.scene.removeItem(ai.hand_widgets[i])
                ai.hand_widgets[i] = None
                self.updateDiscard(ai.position + QPointF(i * 20, 0), len(self.game.discard_pile)-1-i)

        else:
            self.ui.drawButton.setEnabled(False)
            self.ui.swapButton.setEnabled(False)
            self.ui.junkButton.setEnabled(False)
            self.ui.standButton.setEnabled(False)

            hand_len = len(self.player.hand)
            self.game.junk(self.player)
            for i in range(hand_len-1, -1, -1):
                self.scene.removeItem(self.player.hand_widgets[i])
                self.player.hand_widgets[i] = None
                self.updateDiscard(self.card_pos[i], len(self.game.discard_pile)-1-i)
            
            self.plays_over()


            






















    def plays_over(self):
        #Start the bets.

        self.end_of_round()
        return

        



    def end_of_round(self):
        not_over = self.game.advance_round()
        if not_over:
            print("NEXT ROUND")
            self.roll_dice()
            self.round()
        else:
            self.roll_dice()
            self.game_over()





    def clear_game(self):
        for i in range(len(self.game.discard_pile)):
            self.scene.removeItem(self.discard_widgets[i])
            self.animateCard(self.ui.discard_spot.pos(), self.deck_pos, self.createCard(self.game.discard_pile[i]))

        for opp in self.opponents:
            for i in range(len(opp.hand)):
                self.scene.removeItem(opp.hand_widgets[i])
                self.animateCard((opp.position + QPointF(i * 20, 0)), self.deck_pos, self.createCard(opp.hand[i]))
                opp.hand_widgets[i] = None
            opp.hand = []

        for i in range(len(self.player.hand)):
                self.scene.removeItem(self.player.hand_widgets[i])
                self.animateCard(self.card_pos[i], self.deck_pos, self.createCard(self.player.hand[i]))
                self.player.hand_widgets[i] = None
        self.player.hand = []
            
        self.game.reset()



    def game_over(self):
        for opp in self.opponents:
            for i in range(len(opp.hand)):
                self.scene.removeItem(opp.hand_widgets[i])
                opp.hand_widgets[i] = self.scene.addPixmap(self.createCard(opp.hand[i]))
                opp.hand_widgets[i].setPos(opp.position + QPointF(i * 20, 0))
        
        QMessageBox.information(self, "End", f"Final Score: {self.player.calc_hand_value()}")

        QTimer.singleShot(500, lambda: self.clear_game())
        QTimer.singleShot(3000, lambda: self.reset())
        return



    def begin_game(self):
        self.game.initialize_discard_pile()
        self.updateDiscard(self.deck_pos)
        self.deal()
        self.round()




    



    


    




























































class SabaccPlayer:
    """Represents a player in Sabacc.
    Input: name, position for GUI."""
    def __init__(self, name, chips):
        self.name = name
        self.hand = []
        self.hand_widgets = [None, None, None, None, None]
        self.numchips = chips
        self.numchips_bet = 0
        self.out_of_game = False
        self.defeated = False

    def calc_hand_value(self):
        total_value = 0
        for card in self.hand:
            total_value += card.rank
        return total_value












class SabaccAI:
    """Represents an AI player in Sabacc.
    Input: name, position for GUI, difficulty level."""
    def __init__(self, name, position, difficulty):
        self.name = name
        self.position = position
        self.difficulty = difficulty
        self.hand = []
        self.hand_widgets = [None, None, None, None, None]
        self.numchips = random.randint(50, 2000)
        self.numchips_bet = 0
        self.out_of_game = False
        self.defeated = False

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
    def make_move(self, num_round, discard_pile):
        checkHand = self.calc_hand_value()
        checkDiscardValue = discard_pile[len(discard_pile)-1].rank if len(discard_pile) > 0 else None
        optimalSwap = self.checkSwapOptions(self.hand, checkDiscardValue)
        if self.difficulty == "medium":
            '''TESTING APPARATUS--COMMENT WHEN NO LONGER NEEDED'''
            if self.name == "Han":
                if len(self.hand) < 3:
                    return ["draw"]
                else:
                    return ["junk"]
                
        
            if checkHand == 0:
                # AI decides to stand with a perfect hand
                #game.stand(self)
                return ["stand"]
            if optimalSwap != None:
                if num_round == 1 or abs(optimalSwap[1]) < 2:
                    #game.swap(self, optimalSwap)
                    card_idx = self.hand.index(optimalSwap[0])
                    return ["swap", card_idx]
            if abs(checkHand) < 3:
                # AI decides to try and win with the current hand
                #game.stand(self)
                return ["stand"]
            if abs(checkHand) > 23 and num_round == 3:
                #game.junk(self)
                return ["junk"]
            #game.draw(self)
            return ["draw"]




































































class Sabacc:
    """Represents a Sabacc game.
    Input: list of player objects, game screen."""
    '''
    def __init__(self, players, screen, pot):
        self.deck = Sabacc_Deck()
        self.discard_pile = []
        self.players = players
        self.screen = screen
        self.pot = pot
        self.gamePot = 0
    '''

    def __init__(self, players, pot):
        self.deck = Sabacc_Deck()
        self.discard_pile = []
        self.players = players
        self.pot = pot
        self.gamePot = 0
        self.round_num = 0

    """Gives the discard pile its initial card from the deck."""
    def initialize_discard_pile(self):
        card = self.deck.draw_card()
        if card:
            self.discard_pile.append(card)
        #print("Initialized discard pile with card:", card)

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

    """Sets up the game by dealing initial hands to all players."""
    def game_setup(self):
        for player in self.players:
            if not player.defeated and not player.out_of_game:
                self.deal(player, 2)
                print(f"{player.name}'s initial hand: {[str(card) for card in player.hand]}")
                print(f"{player.name} has total hand value: {player.calc_hand_value()}")
    

    """Handles the discard action for a player.
    Inputs: player object, card to discard."""
    def discard(self, player, cardnum):
        #print(f"Player's hand length before discard: {len(player.hand)}")
        self.discard_pile.append(player.hand.pop(cardnum))

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
    def swap(self, player, cardnum):
        #print(f"Hand before swap: {player.hand}")
        card_to_swap = player.hand[cardnum]
        new_card = self.discard_pile.pop()
        player.hand[cardnum] = new_card
        self.discard_pile.append(card_to_swap)
        #print(f"{player.name} swapped {card_to_swap} with {new_card}.")
        #print(f"Hand: {player.hand}")


    """Handles the junk action for a player.
    Inputs: player object."""
    def junk(self, player):
        for i in range(len(player.hand)-1, -1, -1):
            self.discard(player, i)
        player.numchips_bet = 0
        player.out_of_game = True
        print(f"{player.name} has junked their hand and is out of the game.")



    def advance_round(self):
        self.round_num += 1
        return self.round_num < 3
    
    def reset(self):
        self.round_num = 0
        self.discard_pile = []
        self.deck = Sabacc_Deck()
        self.update_players()
    

    def update_players(self):
        for player in self.players:
            player.out_of_game = False

























    

    """Handles the stand action for a player.
    Inputs: player object. Strictly for the format. No logic needed."""
    def stand(self, player):
        pass  # Implement stand logic
    

    def enter_game(self):
        for player in self.players:
            if player.numchips < 10:
                self.players.remove(player)
        for player in self.players:
            self.pot += 10
            player.numchips -= 10
        #self.screen.ui.sabacc_pot.display(self.pot)
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
        #self.screen.ui.UserDialogBox.setPlainText(f"<-- Round {num_round} in progress.")
        for player in self.players:
            print(f"{player.name}'s turn. Hand value: {player.calc_hand_value()}")
            if player.name == "user":
                #self.screen.ui.UserDialogBox.append("Please make your move.")
                player.make_move(self, num_round)
            else:
                if not player.out_of_game:
                    player.make_move(num_round, self.discard_pile, self)
                    print(f"{player.name} has finished their turn. Hand value: {player.calc_hand_value()}")

    """Handles the betting phase after each round.
    Inputs: current round number."""
    def betting_phase(self, num_round):
        #self.screen.ui.UserDialogBox.append(f"<-- Betting phase for Round {num_round}")
        for player in self.players:
            sleep(1)
            if not player.out_of_game and not player.name == "user":
                bet_amount = 10  # Placeholder for bet amount logic
                player.numchips -= bet_amount
                player.numchips_bet += bet_amount
                self.gamePot += bet_amount
                #self.screen.ui.gamePot.display(self.gamePot)
                print(f"{player.name} bets {bet_amount}. Remaining chips: {player.numchips}")
            else:
                if player.name == "user":
                    print("Waiting for user to place bet...")
                    player.make_bet(self)