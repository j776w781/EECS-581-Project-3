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
from PyQt6.QtCore import QPropertyAnimation, QRect, QPointF, QEasingCurve, QRectF, pyqtProperty, QTimer, pyqtSignal, Qt, QTimer, QUrl
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from .objects.sabacc_players import SabaccAI, SabaccPlayer
from .ui.sabacc_ui import Ui_Form
import os
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARDS_DIR = os.path.join(BASE_DIR, "../assets/sabaac_cards")
CHIPS_DIR = os.path.join(BASE_DIR, "../assets")
OPPS_DIR = os.path.join(BASE_DIR, "../assets/sabacc_ops/")
MUSIC_DIR = os.path.join(BASE_DIR, "../assets/music/")


class SabaccScreen(QWidget):
    switch_to_menu = pyqtSignal()

    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.scene = QGraphicsScene(0,0,600,590, self)
        self.ui.graphicsView.setScene(self.scene)
        

        self.audplayer = QMediaPlayer(self)
        self.audio = QAudioOutput(self)
        self.audplayer.setAudioOutput(self.audio)
        self.audio.setVolume(0.3)
        self.songs = [
            os.path.join(MUSIC_DIR, "song1.mp3"),
            os.path.join(MUSIC_DIR, "song2.mp3"),
            os.path.join(MUSIC_DIR, "song3.mp3"),
        ]
        self.current_sond_index = None
        self.audplayer.mediaStatusChanged.connect(self.handle_status)



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
        self.ui.MatchButton.setEnabled(False)
        self.ui.MatchButton.clicked.connect(lambda: self.bet(True))
        self.ui.RaiseButton.setEnabled(False)
        self.ui.RaiseButton.clicked.connect(self.bet)
        self.ui.ContButton.setEnabled(False)
        self.ui.ContButton.clicked.connect(self.done_betting)


        self.state = state
        self.deck_pos = QPointF(180, 200)

        self.card_buttons = [self.ui.card1, self.ui.card2, self.ui.card3, self.ui.card4, self.ui.card5]
        self.card_pos = [QPointF(100, 420), QPointF(185, 420), QPointF(270, 420), QPointF(355, 420), QPointF(440, 420)]

        self.discard_widgets = []


        self.oppstuff = [self.ui.lando, self.ui.han, self.ui.chewie, self.ui.Landochips, self.ui.Hanchips, self.ui.Chewbaccachips, self.ui.Landostake, self.ui.Hanstake, self.ui.Chewbaccastake]
        self.opp_positions = [QPointF(320, 15), QPointF(515, 90), QPointF(-70, 90)]
        self.opponents = self.initializeOpponents()
        self.refreshOpps(3)

        self.player = SabaccPlayer("user", self.state.chips)

        self.ui.Userchips.setText(f"Your Chips: {self.player.chips}")

        players = []
        for opp in self.opponents:
            players.append(opp)
        players.append(self.player)

        sabacc_pot = random.randint(1, 100) * 50
        self.ui.Sabaccpot.setText(f"Sabacc Pot: {sabacc_pot}")
        self.game = Sabacc(players, sabacc_pot)


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

    
    def leave(self):
        if self.game.playing:
            QMessageBox.information(self, "Exiting", "Haha! You just forfeited your chips!")
        self.state.chips = self.player.chips
        self.reset(True)
        self.switch_to_menu.emit()




    #=============================MUSIC ZONE================================================#

    def start_music(self):
        self.play_random_song()

    def stop_music(self):
        self.audplayer.stop()


    def play_random_song(self):
        self.current_song_index = random.randrange(len(self.songs))
        file = self.songs[self.current_song_index]
        self.audplayer.setSource(QUrl.fromLocalFile(file))
        self.audplayer.play()

    def handle_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.play_random_song()

    def showEvent(self, event):
        super().showEvent(event)
        self.start_music()
    
    def hideEvent(self, event):
        super().hideEvent(event)
        self.stop_music()



    #==========================Opponent Management Functions======================#

    def initializeOpponents(self):
        opponents = []
        ai_names = ["Lando", "Han", "Chewbacca"]
        for i in range(3):
            ai_player = SabaccAI(ai_names[i], self.opp_positions[i], "medium")
            opponents.append(ai_player)
            #print(f"Added AI Opponent: {ai_names[i]} at position {self.opp_positions[i]}")
            self.ui.__getattribute__(f"{ai_names[i]}chips").setText(f'Chips: {ai_player.chips}')
        return opponents
    
    def refreshOpps(self, oppcnt):
        for i in range(3):
            if i < oppcnt:
                self.oppstuff[i].show()
                self.oppstuff[i+3].show()
                self.oppstuff[i+6].show()
                self.opponents[i].defeated = False
            if i >= oppcnt:
                self.oppstuff[i].hide()
                self.oppstuff[i+3].hide()
                self.oppstuff[i+6].hide()
                self.opponents[i].defeated = True
        #self.game.oppNo = value


    def defeatOpp(self, i):
        opp = self.opponents[i]
        opp.defeated = True
        self.oppstuff[i].hide()
        self.oppstuff[i+3].hide()
        self.oppstuff[i+6].hide()
        QMessageBox.information(self, "Victory", f"{opp.name} has left the game!")


    #========================ANIMATION HELP===================================#
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



    #===============================GAME MOVE WRAPPERS=================================#


    def deal(self, shift=False):
        # Game deals cards.
        if not shift:
            print("Dealing cards...")
            self.ui.oppcount.setEnabled(False)
            self.ui.opplabel.hide()
            self.ui.oppcount.hide()
            self.ui.StartButton.setEnabled(False)
        
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

        

    def stand(self, ai=None):
        if ai:
            return
        else:
            self.ui.drawButton.setEnabled(False)
            self.ui.swapButton.setEnabled(False)
            self.ui.junkButton.setEnabled(False)
            self.ui.standButton.setEnabled(False)
            #Deactivate the card buttons (Don't want to discard!)
            for i in range(len(self.player.hand)):
                try:
                    self.card_buttons[i].clicked.disconnect()
                except TypeError:
                    pass
                self.card_buttons[i].setEnabled(False)
            self.plays_over()



    def discard(self, cardnum, ai=None, shift=False):
        if ai:
            #update hand in game logic
            self.game.discard(ai, cardnum)

            #animate discarding.
            self.updateDiscard(ai.position + QPointF(cardnum*20, 0))

            if cardnum == len(ai.hand):
                self.scene.removeItem(ai.hand_widgets[cardnum])
                ai.hand_widgets[cardnum] = None
            else:
                self.scene.removeItem(ai.hand_widgets[cardnum])
                self.scene.removeItem(ai.hand_widgets[len(ai.hand)])

                #Move furthest card over.
                card_sprite = self.createCard(ai.hand[len(ai.hand)-1], True)
                start = ai.position + QPointF((20 * len(ai.hand)), 0)
                end = ai.position + QPointF(cardnum*20, 0)
                ai.hand_widgets[cardnum] = self.animateCard(start, end, card_sprite)
                over = ai.hand_widgets[cardnum+1]
                ai.hand_widgets[cardnum].setZValue(over.zValue() - 1)
                
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
            
            if not shift:
                self.plays_over()
            


    def draw(self, ai=None):
        if ai:
            #For timings, the actual game logic drawing is done in round(). The AI version of draw simply implements the animations.
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
            
            self.game_over(True)


        
    def background_finish(self):
        not_over = self.game.advance_round()
        while not_over:
            opp_order = [2, 0, 1]
        
            for num in opp_order:
                opp = self.opponents[num]
                if not opp.out_of_game and not opp.defeated:
                    move = opp.make_move(self.game.round_num+1, self.game.discard_pile)

                    if move[0] == "draw":
                        #print(f"Calling draw for {opp}")
                        self.game.draw(opp)
                        drop = opp.should_discard()
                        if drop >= 0:
                            self.game.discard(opp, drop)
                            
                        elif move[0] == "swap":
                            self.game.swap(opp, move[1])
                            self.discard_widgets.pop()
                            
                        elif move[0] == "junk":   
                            self.game.junk(opp)
            
            for i in opp_order:
                opp = self.opponents[i]
                if not opp.out_of_game and not opp.defeated:
                    bet = opp.should_bet(self.game.current_bet)
                    self.game.bet(opp, bet)

            if self.game.should_shift([random.randint(1,6), random.randint(1,6)]):
                #Opponents discard
                lengths = []
                for opp in self.opponents:
                    length = len(opp.hand)
                    lengths.append(length)
                    if not opp.out_of_game and not opp.defeated:
                        for i in range(length-1, -1, -1):
                            self.game.discard(opp, i)
                            
                self.game.shift(lengths)

            not_over = self.game.advance_round()


    def bet(self, match=False):
        '''
        if self.player.chips < self.game.current_bet:
            self.game.bet(self.player, self.player.chips)
            self.ui.Userchips.setText(f"Your Chips: {self.player.chips}")
            self.ui.Userstake.setText(f"Your Stake: {self.player.stake}")
            self.ui.Gamepot.setText(f"Game Pot: {self.game.gamePot}")
            QMessageBox.information(self, "Low Chips", "Looks like your out of chips! Don't worry, you can still keep playing!")
            self.done_betting()
        '''
        cutoff = False
        if match:
            if self.player.chips < self.game.current_bet:
                cutoff = True
                self.game.bet(self.player, self.player.chips)
            else:
                self.game.bet(self.player, self.game.current_bet)
            self.ui.MatchButton.setEnabled(False)
        else:
            if self.player.chips >= 50:
                self.game.bet(self.player, 50, True)
            else:
                self.game.bet(self.player, self.player.chips, True)
                cutoff = True

        self.ui.Userchips.setText(f"Your Chips: {self.player.chips}")
        self.ui.Userstake.setText(f"Your Stake: {self.player.stake}")
        self.ui.Gamepot.setText(f"Game Pot: {self.game.gamePot}")
        self.ui.CurBet.setText(f"Bet to Match: {self.game.current_bet}")

        if cutoff:
            QMessageBox.information(self, "Low Chips", "Looks like your out of chips! Don't worry, you can still keep playing!")
            self.done_betting()
        else:
            self.ui.ContButton.setEnabled(True)
            self.ui.RaiseButton.setEnabled(True)
    

    def done_betting(self):
        self.ui.CurBet.setText(f"Bet to Match: ")
        self.ui.MatchButton.setEnabled(False)
        self.ui.RaiseButton.setEnabled(False)
        self.ui.ContButton.setEnabled(False)
        self.end_of_round()



    #==============================CLEANUP=======================================#


    def reset(self, hard=False):
        self.scene.clear()
        self.ui.drawButton.setEnabled(False)
        self.ui.swapButton.setEnabled(False)
        self.ui.standButton.setEnabled(False)
        self.ui.junkButton.setEnabled(False)
        self.ui.card1.setEnabled(False)
        self.ui.card2.setEnabled(False)
        self.ui.card3.setEnabled(False)
        self.ui.card4.setEnabled(False)
        self.ui.card5.setEnabled(False)
        self.ui.StartButton.setEnabled(True)
        self.ui.dice1.display("-")
        self.ui.dice2.display("-")
        self.ui.oppcount.setEnabled(True)
        self.ui.MatchButton.setEnabled(False)
        self.ui.RaiseButton.setEnabled(False)
        self.ui.ContButton.setEnabled(False)

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

            sabacc_pot = random.randint(1, 100) * 50
            self.game = Sabacc(players, sabacc_pot)

        self.player.stake = 0

        self.ui.Userchips.setText(f"Your Chips: {self.player.chips}")
        self.ui.Userstake.setText(f"Your Stake: ")
        self.ui.Gamepot.setText("Game Pot: ")
        self.ui.Sabaccpot.setText(f"Sabacc Pot: {self.game.sabbacpot}")
        self.ui.CurBet.setText(f"Bet to Match: ")
        for i in range(len(self.opponents)):
            opp = self.opponents[i]
            opp.stake = 0
            self.oppstuff[i+3].setText(f"Chips: {opp.chips}")
            self.oppstuff[i+6].setText("Stake: ")

    
    def clear_game(self):
        for item in self.scene.items():
            self.scene.removeItem(item)
        for i in range(len(self.game.discard_pile)):
            self.animateCard(self.ui.discard_spot.pos(), self.deck_pos, self.createCard(self.game.discard_pile[i]))

        for opp in self.opponents:
            for i in range(len(opp.hand)):
                self.animateCard((opp.position + QPointF(i * 20, 0)), self.deck_pos, self.createCard(opp.hand[i]))
                opp.hand_widgets[i] = None
            opp.hand = []

        for i in range(len(self.player.hand)):
                self.animateCard(self.card_pos[i], self.deck_pos, self.createCard(self.player.hand[i]))
                self.player.hand_widgets[i] = None
        self.player.hand = []
            
        self.game.reset()



    #=================GAME FLOW CONTROL==========================================#  

    def round(self):
        opp_order = [2, 0, 1]
        report_str = ""
        i = 1
        for num in opp_order:
            opp = self.opponents[num]
            if not opp.out_of_game and not opp.defeated:
                move = opp.make_move(self.game.round_num+1, self.game.discard_pile)
                report_str += f"{opp.name} chose to {move[0]}"

                if move[0] == "draw":
                    #print(f"Calling draw for {opp}")
                    self.game.draw(opp)
                    QTimer.singleShot(1000 * i, lambda offset=i, a=opp: self.draw(a))
                    i+=1

                    drop = opp.should_discard()
                    if drop >= 0:
                        report_str += f" and discard"
                        QTimer.singleShot(1000 * i, lambda c=drop, a=opp: self.discard(c, a))
                        i+=1
                    
                elif move[0] == "swap":
                    QTimer.singleShot(1000 * i, lambda m=move, a=opp: self.swap_helper(m[1], a))
                    i+=1
                elif move[0] == "junk":
                    QTimer.singleShot(1000*i, lambda a=opp: self.junk(a))
                    i+=1
                else:
                    QTimer.singleShot(1000*i, lambda a=opp: self.stand(a))
                
                report_str += ".\n"
            
        QTimer.singleShot(1000*i, lambda s=report_str: QMessageBox.information(self, "Opponents' Moves", s))
        #Let the AI do what it needs to do.
        #Effectuate changes

        QTimer.singleShot(1000*i, lambda: self.ui.drawButton.setEnabled(True))
        QTimer.singleShot(1000*i, lambda: self.ui.swapButton.setEnabled(True))
        QTimer.singleShot(1000*i, lambda: self.ui.junkButton.setEnabled(True))
        QTimer.singleShot(1000*i, lambda: self.ui.standButton.setEnabled(True))
        QTimer.singleShot(1000*i, lambda: self.ui.leaveButton.setEnabled(True))
        


    def plays_over(self):
        self.ui.drawButton.setEnabled(False)
        self.ui.swapButton.setEnabled(False)
        self.ui.junkButton.setEnabled(False)
        self.ui.standButton.setEnabled(False)

        opp_order = [2, 0, 1]
        report_str = ''
        for i in opp_order:
            opp = self.opponents[i]
            if not opp.out_of_game and not opp.defeated:
                bet = opp.should_bet(self.game.current_bet)
                self.game.bet(opp, bet)
                self.oppstuff[i+3].setText(f"Chips: {opp.chips}")
                self.oppstuff[i+6].setText(f"Stake: {opp.stake}")
                report_str += f"{opp.name} bet {bet} chips"
                if bet < self.game.current_bet:
                    report_str += "(he ran out)"
                report_str += ".\n"
                self.ui.CurBet.setText(f"Bet to Match: {self.game.current_bet}")
        
        self.ui.Gamepot.setText(f"Game Pot: {self.game.gamePot}")

        
        if self.player.chips == 0:
            report_str += "Looks like you already bet all your chips...May the Force Be With You, because the dice certainly won't."
            QMessageBox.information(self, "Bet Summary", report_str)
            QTimer.singleShot(500, self.done_betting)
        else:
            report_str += "Now it's your turn! First click Match to match the current bet.\nThen, you can raise it by 50 as much as you can, or click continue!"
            QMessageBox.information(self, "Bet Summary", report_str)
            self.ui.MatchButton.setEnabled(True)
        return



    def roll_dice(self, hack=False):
        self.ui.dice1.display(str(random.randint(1,6)))
        self.ui.dice2.display(str(random.randint(1,6)))
        print("Rolled Dice")
        print("Dice 1:", self.ui.dice1.value())
        print("Dice 2:", self.ui.dice2.value())
        
        if hack:
            return [1,1]
        return [self.ui.dice1.value(), self.ui.dice2.value()]


    def reset_hands(self):
        lengths = []

        #Opponents discard
        for opp in self.opponents:
            length = len(opp.hand)
            lengths.append(length)
            if not opp.out_of_game and not opp.defeated:
                for i in range(length-1, -1, -1):
                    self.discard(i, opp)

        #Player discards.
        length = len(self.player.hand)
        lengths.append(len(self.player.hand))
        for i in range(length-1, -1, -1):
            self.discard(i, shift=True)

        self.game.shift(lengths)
        self.deal(True)


    def end_of_round(self):
        self.game.reset_bet()
        not_over = self.game.advance_round()
        if not_over:
            if self.game.should_shift(self.roll_dice()):
                QMessageBox.information(self, "Doubles!", "Dice came up doubles! Time to shift!")
                self.reset_hands()
                self.round()
                print("NEXT ROUND(DOUBLES)")
            else:
                self.round()
                print("NEXT ROUND")
        else:
            if self.game.should_shift(self.roll_dice()):
                QMessageBox.information(self, "Doubles!", "Dice came up doubles! Time to shift!")
                self.reset_hands()
                QTimer.singleShot(1000, self.game_over)
            else:
                self.game_over()

    def begin_game(self):
        #Initial entry fee.
        self.ui.leaveButton.setEnabled(False)
        self.game.entry_fees()
        self.ui.Userchips.setText(f"Your Chips: {self.player.chips}")
        self.ui.Userstake.setText(f"Your Stake: {self.player.stake}")
        for i in range(len(self.opponents)):
            opp = self.opponents[i]
            if not opp.defeated:
                self.oppstuff[i+3].setText(f"Chips: {opp.chips}")
                self.oppstuff[i+6].setText(f"Stake: {opp.stake}")
        self.ui.Gamepot.setText(f"Game Pot: {self.game.gamePot}")

        self.game.initialize_discard_pile()
        self.updateDiscard(self.deck_pos)
        self.deal()
        self.round()



    def aftermath(self, winner):
        payout = self.game.determine_payout(winner)


        for i in range(len(self.opponents)):
            opp = self.opponents[i]
            print(f"{opp.name} has {opp.chips} right now")
            if opp.name == winner.name:
                opp.chips += payout
            self.oppstuff[i+3].setText(f"Chips: {opp.chips}")
            self.oppstuff[i+6].setText(f"Stake: ")

        for j in range(len(self.opponents)):
            opp = self.opponents[j]
            if opp.chips <= 0:
                self.defeatOpp(j)

        if winner.name == "user":
            self.player.chips += payout
            self.ui.Userchips.setText(f"Your Chips: {self.player.chips}")
            self.ui.Userstake.setText(f"Your Stake: ")
            QMessageBox.information(self, "You Win!", f"You won {payout} chips with a score of {winner.calc_hand_value()}")
           
            alive = 0
            for opp in self.opponents:
                if not opp.defeated:
                    alive+=1
            
            if alive == 0:
                QMessageBox.information(self, "Flawless Victory", "WOW! You beat...everyone! Come back later!")
                self.game.reset()
                self.leave()
                return
        else:
            QMessageBox.information(self, "You Lose!", f"{winner.name} won {payout} chips with a score of {winner.calc_hand_value()}")

            if self.player.chips <= 0:
                self.ui.Userstake.setText(f"Your Stake: ")
                QMessageBox.information(self, "Defeat", "No more chips? GET OUTTA HERE!")
                self.game.reset()
                self.leave()
                return

        QTimer.singleShot(500, lambda: self.clear_game())
        QTimer.singleShot(1250, lambda: self.reset())


    def game_over(self, fast_frwd=False):
        if fast_frwd:
            self.background_finish()
        else:
            for opp in self.opponents:
                for i in range(len(opp.hand)):
                    self.scene.removeItem(opp.hand_widgets[i])
                    opp.hand_widgets[i] = self.scene.addPixmap(self.createCard(opp.hand[i]))
                    opp.hand_widgets[i].setPos(opp.position + QPointF(i * 20, 0))
    
        self.aftermath(self.game.determine_winner())



    





'''
Sabacc Game Class
'''
class Sabacc:
    """Represents a Sabacc game.
    Input: list of player objects, game screen."""

    def __init__(self, players, pot):
        self.deck = Sabacc_Deck()
        self.discard_pile = []
        self.players = players
        self.sabbacpot = pot
        self.gamePot = 0
        self.round_num = 0
        self.current_bet = 0
        self.playing = False

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
        self.playing = True
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
        player.stake = 0
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
        self.playing = False
    

    def update_players(self):
        for player in self.players:
            player.out_of_game = False


    def should_shift(self, results):
        return results[0] == results[1]
    
    def shift(self, lengths):
        for num in range(len(lengths)):
            if not self.players[num].out_of_game and not self.players[num].defeated:
                self.deal(self.players[num], lengths[num])


    """Determines and announces the winner of the game and distributes the pot."""
    def determine_winner(self):
        track_winner = None
        for player in self.players:
            if not player.out_of_game and not player.defeated:
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
                    elif player.calc_hand_value() == track_winner.calc_hand_value():
                        """Found a player with the same hand value, check for fewer cards win."""
                        if len(player.hand) > len(track_winner.hand):
                            track_winner = player
                        elif len(player.hand) == len(track_winner.hand):
                            """Found a player with the same hand value and same number of cards, check for highest value card to break the tie."""
                            player.max_card = max(player.hand, key=lambda c: c.rank)
                            track_winner.max_card = max(track_winner.hand, key=lambda c: c.rank)
                            if player.max_card.rank > track_winner.max_card.rank:
                                track_winner = player
                            elif player.max_card.rank == track_winner.max_card.rank and player.name=="user":
                                track_winner = player
        return track_winner


    def entry_fees(self):
        for player in self.players:
            self.gamePot += 50
            if not player.defeated:
                player.chips += -50
                player.stake += 50


    def determine_payout(self, winner):
        payout = self.gamePot
        true_sabbac = winner.calc_hand_value() == 0
        if true_sabbac:
            payout += self.sabbacpot
            self.sabbacpot = 0
        return payout
    
    def bet(self, player, amount, is_raise = False):
        self.gamePot += amount
        player.stake += amount
        player.chips += -1 * amount
        if amount > self.current_bet:
            self.current_bet = amount
        elif is_raise:
            self.current_bet += amount
    
    def reset_bet(self):
        self.current_bet = 0