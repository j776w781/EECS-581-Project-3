'''
File: sabaac.py

Authors: Joshua Welicky, Gavin Billinger, Mark Kitchin, Max Biundo, Bisshoy Bhattacharjee

Description:
Stores the Sabaac class, which handles game logic related to Sabaac, and SabaacScreen class,
which renders the GUI and effects the moves ordained by the Sabaac class.

Inputs: state = A GameState object storing the global chip count.
        paretn = A MainWindow object that this screen connects to.

Outputs: Functional GUI implementation for Sabaac.
'''
from .objects.sabacc_deck import Sabacc_Deck
from .objects.deck import AnimatedCard
from PyQt6.QtWidgets import QWidget, QGraphicsScene, QMessageBox
from PyQt6.QtCore import QPropertyAnimation, QPointF, QEasingCurve, QTimer, pyqtSignal, QTimer, QUrl
from PyQt6.QtGui import QPixmap
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from .objects.sabacc_players import SabaccAI, SabaccPlayer
from .ui.sabacc_ui import Ui_Form
import os
import random

#Helpful filepath variables
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARDS_DIR = os.path.join(BASE_DIR, "../assets/sabaac_cards")
CHIPS_DIR = os.path.join(BASE_DIR, "../assets")
OPPS_DIR = os.path.join(BASE_DIR, "../assets/sabacc_ops/")
MUSIC_DIR = os.path.join(BASE_DIR, "../assets/music/")


'''
Main GUI Manager for Sabacc. It interfaces with the Sabacc (game logic),
SabaccPlayer (human user), and SabaccAI (ai opponents) objects to effect GUI changes based on the 
game logic decisions.
'''
class SabaccScreen(QWidget):
    #This signal is monitored in main.py. When emitted, it switches us back to the main menu.
    switch_to_menu = pyqtSignal()

    #Initializes Default GUI state and initial Game objects.
    def __init__(self, state, parent=None):
        #Setup initial GUI
        super().__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        #Sets stage for adding animated cards and such.
        self.scene = QGraphicsScene(0,0,600,590, self)
        self.ui.graphicsView.setScene(self.scene)
        

        #Sets up the audio player for background music.
        self.audplayer = QMediaPlayer(self)
        self.audio = QAudioOutput(self)
        self.audplayer.setAudioOutput(self.audio)
        self.audio.setVolume(0.3)
        self.songs = [
            os.path.join(MUSIC_DIR, "song1.mp3"),
            os.path.join(MUSIC_DIR, "song2.mp3"),
            os.path.join(MUSIC_DIR, "song3.mp3"),
            os.path.join(MUSIC_DIR, "song4.mp3"),
        ]
        self.current_sond_index = None
        #This will fire off when a song ends. It then randomly plays another song.
        self.audplayer.mediaStatusChanged.connect(self.handle_status)

        #Sets the images for some GUI objects
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
        self.ui.StartButton.clicked.connect(self.begin_game)
        self.ui.dice1.display("-")
        self.ui.dice2.display("-")
        self.ui.leaveButton.clicked.connect(self.leave)
        self.ui.rules.clicked.connect(self.show_rules)
        self.ui.oppcount.valueChanged.connect(self.refreshOpps)
        self.ui.MatchButton.setEnabled(False)
        self.ui.MatchButton.clicked.connect(lambda: self.bet(True))
        self.ui.RaiseButton.setEnabled(False)
        self.ui.RaiseButton.clicked.connect(self.bet)
        self.ui.ContButton.setEnabled(False)
        self.ui.ContButton.clicked.connect(self.done_betting)

        #Attach GameState
        self.state = state
        
        #Hard-coded positions and GUI elements for easy access.
        self.deck_pos = QPointF(180, 200)
        self.card_pos = [QPointF(100, 420), QPointF(185, 420), QPointF(270, 420), QPointF(355, 420), QPointF(440, 420)]
        self.card_buttons = [self.ui.card1, self.ui.card2, self.ui.card3, self.ui.card4, self.ui.card5]
        
        #This will store the AnimatedCard widgets for the discard pile, so they can be accessed and removed after initialization.
        self.discard_widgets = []

        #Initializes opponent items, saving relevant GUI elements together, hard-coding positions, and setting up the SabaccAI class.
        self.oppstuff = [self.ui.lando, self.ui.han, self.ui.chewie, self.ui.Landochips, self.ui.Hanchips, self.ui.Chewbaccachips, self.ui.Landostake, self.ui.Hanstake, self.ui.Chewbaccastake]
        self.opp_positions = [QPointF(320, 15), QPointF(515, 90), QPointF(-70, 90)]
        self.opponents = self.initializeOpponents()
        self.refreshOpps(3)

        #Initialize the SabaccPlayer and link the global chip count.
        self.player = SabaccPlayer("user", self.state.chips)
        self.ui.Userchips.setText(f"Your Chips: {self.player.chips}")

        #Build up an array containing the game players, which is a required argument for the Sabacc class.
        players = []
        for opp in self.opponents:
            players.append(opp)
        players.append(self.player)

        #Initialize the bonus sabacc pot with a random multiple of 50.
        sabacc_pot = random.randint(1, 100) * 50
        self.ui.Sabaccpot.setText(f"Sabacc Pot: {sabacc_pot}")

        #Initialize the Sabacc game logic class.
        self.game = Sabacc(players, sabacc_pot)


    '''
    A relatively simple function that, when called, creates a message form with the rules of Sabacc.
    '''
    def show_rules(self):
        rules = (
                "Sabacc Rules:\n"
                "50 Chip buy in to enter the game.\n"
                "1. Each player is dealt two cards.\n"
                "2. Players take turns each round to draw a card, swap for the card at the top of the discard pile, stand (pass to the next player), or junk (forfeit the game).\n"
                "2.5. Players may choose to discard a card after drawing."
                "3. The goal is to have a hand value closest to zero.\n"
                "4. Positive and negative cards affect hand value.\n"
                "5. The game continues for 3 rounds.\n"
                "5.5. Players bet after every round.\n"
                "6. The player with the hand value closest to zero after the last round wins the game pot.\n"
                "7. If a player wins with exactly 0, they win the sabacc pot.\n"
        )
        QMessageBox.information(self, "Sabacc Rules", rules)

    
    '''
    Another simple function called when exiting the Sabacc screen. It links the player's current chips to the global amount.
    It performs a hard reset, reinitializing everything, and it fires off the switch_to_menu signal.
    '''
    def leave(self):
        if self.game.playing:
            QMessageBox.information(self, "Exiting", "Haha! You just forfeited your chips!")
        self.reset(True)
        self.switch_to_menu.emit()




    #=============================MUSIC ZONE================================================#
    '''
    A few simple functions to facilitate a constant, randomly ordered stream of background music
    that starts upon Sabacc entry, and leaves upon exit, restarting again when needed.
    '''

    '''Function to begin music playing.'''
    def start_music(self):
        self.play_random_song()

    '''Function to stop playing music.'''
    def stop_music(self):
        self.audplayer.stop()

    '''Function that randomly selects one of the random songs, and plays it.'''
    def play_random_song(self):
        self.current_song_index = random.randrange(len(self.songs))
        file = self.songs[self.current_song_index]
        self.audplayer.setSource(QUrl.fromLocalFile(file))
        self.audplayer.play()

    '''When a song ends, this function will iniate a new song to be played.'''
    def handle_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.play_random_song()

    '''This function is called any time the Sabacc screen comes into focus. It starts music.'''
    def showEvent(self, event):
        super().showEvent(event)

        #Useful for updating sabacc balance when you've left to play another game.
        self.player.chips = self.state.chips
        self.ui.Userchips.setText(f"Your Chips: {self.player.chips}")

        self.start_music()
    
    '''This function is called any time the Sabacc screen goes out of focus. It ends the music.'''
    def hideEvent(self, event):
        super().hideEvent(event)
        self.stop_music()



    #==========================Opponent Management Functions======================#
    '''
    A few helper functions to manage AI opponents. These include initialization, showing,
    and hiding.
    '''

    '''
    This is called when the AI opponents need to be manually reset, either upon initalization
    or hard reset. It returns a list of new SabaccAI objects.
    '''
    def initializeOpponents(self):
        opponents = []
        #Not the game order, but the order of the widgets stored in init.
        #This is because we want Lando to be the only required player (opponent 1), even though Chewbacc will always play first(if he's included)
        ai_names = ["Lando", "Han", "Chewbacca"]
        for i in range(3):
            #Sabacc AI will store their name, chip amount, current stake, and a few GUI things (GUI position, card hand widgets) for convenience.
            ai_player = SabaccAI(ai_names[i], self.opp_positions[i])
            opponents.append(ai_player)
            #Update GUI with their chip amount.
            self.ui.__getattribute__(f"{ai_names[i]}chips").setText(f'Chips: {ai_player.chips}')
        return opponents
    
    '''
    This should only be called when the Opponent Count spin box is altered. It "adds" or "removes" 
    opponents in a fixed order (Lando is always present, Han can be, Chewbacca can be). It doesn't
    actually delete anything. When a player is not desired, all of their GUI elements (Photo, chip count,
    stake) are hidden from view. They can be restored. The oppcnt parameter is the just the specified number of opponents.
    '''
    def refreshOpps(self, oppcnt):
        for i in range(3):
            #While the GUI's oppcnt is bounded 1<3, the internal count is actually 0<2. So if oppcnt=1, only opponent 0 (lando) will be shown.
            if i < oppcnt:
                self.oppstuff[i].show()
                self.oppstuff[i+3].show()
                self.oppstuff[i+6].show()
                #Makes sure no looping GUI/Game logic actions are performed on him, since we're not deleting him
                self.opponents[i].defeated = False
            #Opposite case, where the opponent's existed is desired.
            if i >= oppcnt:
                self.oppstuff[i].hide()
                self.oppstuff[i+3].hide()
                self.oppstuff[i+6].hide()
                self.opponents[i].defeated = True

    '''
    Used to "defeat" an opponent, which occurs when the opponent, (i = index in self.opponents) runs out of chips, and is then kicked out of the game. 
    All of their GUI stuff is hidden, and a message explaining the situation is shown to the user.
    '''
    def defeatOpp(self, i):
        opp = self.opponents[i]
        opp.defeated = True
        self.oppstuff[i].hide()
        self.oppstuff[i+3].hide()
        self.oppstuff[i+6].hide()
        QMessageBox.information(self, "Victory", f"{opp.name} has left the game!")


    #========================ANIMATION HELP===================================#
    '''
    A few functions dedicated entirely for card animation assistance. The first
    two are reused from previous game implementations. The third manages standard
    UpdateDiscard animates standard additions to the discard pile.
    '''

    '''
    Helpful function for obtaining the proper pixmap for a Card instance, based
    on rank, suit, and if its hidden.
    '''
    def createCard(self, card, hidden=False):
        if hidden:
            path = os.path.join(CARDS_DIR, "sabacc_deck_back.png")
        else:
            path = os.path.join(CARDS_DIR, "" + card.getName())
        pixmap = QPixmap(path).scaled(80, 120)
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


    '''
    Function that creates an animation for adding a card to the discard pile. pos is just the starting
    position for the animation, either the deck or somewhere in a player's hand. The DESTINATION IS ALWAYS
    THE DISCARD PILE POSITION. 
    
    dec_idx specifies a particular card index within the game logic's discard to generate the animation for.
    This function is usually called after the game logic's discard has been performed. So deck_idx allows for 
    "backtracking" after the fact. It will be set to the top of the discard pile if it goes unspecified.
    '''
    def updateDiscard(self, pos, deck_idx=-1):
        if deck_idx < 0:
            deck_idx = len(self.game.discard_pile)-1
        #Make a Pixmap for the card being "added" to the pile.
        card_sprite = self.createCard(self.game.discard_pile[deck_idx])
        #Create and SAVE animation widget. It may need to be removed later.
        self.discard_widgets.append(self.animateCard(pos, self.ui.discard_spot.pos(), card_sprite))



    #===============================GAME MOVE WRAPPERS=================================#
    '''
    This block of code contains the GUI-integrated handlers for game logic moves, including
    dealing, standing, betting, drawing, discarding, swapping, and junking. Most follow
    a common technique, i.e. calling the GameLogic to enact the change, then effecting those
    changes on the GUI. Some include ai cases, which slightly differ from the human player's case.
    '''



    '''
    Primary animator for dealing the hand to both the player and the opponents.
    Includes a shift parameter (which is active this is called within a shift context).
    If this parameter is active, this function doesn't need to perform some initial game logic setup of GUI management.
    '''
    def deal(self, shift=False):
        # Case for initial deal.
        if not shift:
            print("Dealing cards...")
            #Hide opponent count dial. Won't be restored until exit.
            self.ui.oppcount.setEnabled(False)
            self.ui.opplabel.hide()
            self.ui.oppcount.hide()
            self.ui.StartButton.setEnabled(False)
            #Set up each player's hand.
            self.game.game_setup()

        # UI animates cards to player hand.
        for i, card in enumerate(self.player.hand):
            card_sprite = self.createCard(card)
            end = self.card_pos[i]
            #Save the animated widgets for later use/replacement.
            self.player.hand_widgets[i]=self.animateCard(self.deck_pos, end, card_sprite)       

        # UI animates cards for each opponent
        for i in range(len(self.opponents)):
            for j, card in enumerate(self.opponents[i].hand):
                card_sprite = self.createCard(card, True)
                #Opponent's card positions are offset by 20 on the x axis for spacing.
                end = self.opponents[i].position + QPointF(j * 20, 0)
                #Save the widgets.
                self.opponents[i].hand_widgets[j] = (self.animateCard(self.deck_pos, end, card_sprite))

        

    '''
    Basic function for standing, where the user does nothing. In the AI case, no actions need to be performed.
    In the human case, some buttons need to be deactivated. Then, plays_over() is called, which initiates the betting phase.
    '''
    def stand(self, ai=None):
        if ai:
            return
        else:
            #Disable game moves.
            self.ui.drawButton.setEnabled(False)
            self.ui.swapButton.setEnabled(False)
            self.ui.junkButton.setEnabled(False)
            self.ui.standButton.setEnabled(False)
            #Deactivate the card buttons (Don't want to discard!)
            #This could be active after a Draw.
            for i in range(len(self.player.hand)):
                try:
                    self.card_buttons[i].clicked.disconnect()
                except TypeError:
                    pass
                self.card_buttons[i].setEnabled(False)
            #Move onto betting.
            self.plays_over()



    '''
    A relatively robust function that handles the animations involved with discarding a card to the 
    discard pile. It takes in a cardnum(int), which represents the specific card in a hand. 
    The ai parameter optionally specifies a SabaccAI to enter the ai case.
    The shift parameter allows this function to be reused for shifting, where all cards in a hand
    are discarded, without triggering a new round of betting.
    '''
    def discard(self, cardnum, ai=None, shift=False):
        if ai:
            #update hand in game logic
            self.game.discard(ai, cardnum)

            #animate discarding.
            self.updateDiscard(ai.position + QPointF(cardnum*20, 0))

            #If one of the innner cards is discarded, the outermost one should be moved over.
            if cardnum == len(ai.hand):
                self.scene.removeItem(ai.hand_widgets[cardnum])
                ai.hand_widgets[cardnum] = None
            else:
                #Remove current widgets to avoid untracked duplicates.
                self.scene.removeItem(ai.hand_widgets[cardnum])
                self.scene.removeItem(ai.hand_widgets[len(ai.hand)])
                #Move furthest card over.
                card_sprite = self.createCard(ai.hand[len(ai.hand)-1], True)
                start = ai.position + QPointF((20 * len(ai.hand)), 0)
                end = ai.position + QPointF(cardnum*20, 0)
                ai.hand_widgets[cardnum] = self.animateCard(start, end, card_sprite)
                #Adjusts z-axis position, so a card more to the left does not cover up its neighbor to the right.
                over = ai.hand_widgets[cardnum+1]
                ai.hand_widgets[cardnum].setZValue(over.zValue() - 1)

                ai.hand.insert(cardnum, ai.hand.pop())

        #The human player's case is almost exactly the same, with some slight changes for how the position is calculated.
        #Additional buttons also need to be deactivated.   
        else:
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

                self.player.hand.insert(cardnum, self.player.hand.pop())
            
            #If this discard is not being done within a shift, then the betting stage should begin, since the human plays last.
            if not shift:
                self.plays_over()
            


    '''
    Basic function for drawing. Both require animating their most recently added card.
    However, for the human, they must then be given the option to discard one of their cards. 
    Therefore, they can't finish their move until they click stand, or one of the card_buttons,
    which are placed and activated over all their available cards.
    '''
    def draw(self, ai=None):
        if ai:
            #For timings, the actual game logic drawing is done in round(). The AI version of draw simply implements the animations.
            #Animate the new card.
            card_sprite = self.createCard(ai.hand[len(ai.hand)-1], True)
            end = ai.position + QPointF((len(ai.hand)-1) * 20, 0)
            ai.hand_widgets[len(ai.hand)-1] = self.animateCard(self.deck_pos, end, card_sprite)

        else:
            #Deactivate buttons. Note the stand is not activated, since it can still be clicked during discard.
            self.ui.drawButton.setEnabled(False)
            self.ui.swapButton.setEnabled(False)
            self.ui.junkButton.setEnabled(False)
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



    '''
    This is the function that actually implements swapping animations. Like discard, it takes in a 
    cardnum(int), which specifies the card to swap, and an optional opponent. The human and ai cases
    are very similar, barring some changes to how positions are handled. Additionally, the plays_over()
    function is called for the human, since the human plays last.

    One way this function deviates from the others is that it performs the swap in game logic after performing
    the animations. This was done for a more intuitive implementation for swapping animations (discard-taking
    actually animates the card at the top of the discard pile. Otherwise, it would have to be the user's new
    card, which they would have gotten from the discard pile.).
    '''
    def swap_helper(self, cardnum, ai=None):
        if ai:
            #remove the old card widgets.
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

            #Now initiate the swap.
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

            #Now initiate the swap. 
            self.game.swap(self.player, cardnum)

            #User's turn is not over, so betting should begin.
            self.plays_over()



    '''
    A relatively simple function active when a user presses the swap button. It just makes the card buttons available for 
    pressing (connecting them to the swap implementer) and posts a quick message form.
    '''
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



    '''
    This is the function used to handle junking, where the player discards all their cards and essentially bows out of the game. 
    In the AI case, it only needs to perform the game logic call, then animate the discarding of each card in it's hand. The same is
    done in the human case. This is the function that makes use of the deck_idx parameter in updateDiscard.

    In the human case, junking does not continue standard game flow. Instead, it "fast-forwards" to the end, where the remaining AI opponents
    continue playing and betting in the background. That is why the game_over() call is made.
    '''
    def junk(self, ai=None):
        if ai:
            hand_len = len(ai.hand)
            #Actually clears the player's hand, which is why the hand_len is saved before hand.
            self.game.junk(ai)
            #The rightmost cards are discarded first, hence the reversed ordering.
            for i in range(hand_len-1, -1, -1):
                #Remove the widgets
                self.scene.removeItem(ai.hand_widgets[i])
                #Clear out the widgets
                ai.hand_widgets[i] = None
                #Backtrack through the discard pile to animate the right card.
                self.updateDiscard(ai.position + QPointF(i * 20, 0), len(self.game.discard_pile)-1-i)

        else:
            #Disable buttons.
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
            
            #Skip to the end.
            self.game_over(True)


    '''
    This function essentially finishes a game without applying any GUI activities. It is meant
    to be done when a player "junks", allowing the remaining opponents to finish the game naturally.
    '''
    def background_finish(self):
        opp_order = [0, 2, 1]

        while True:
            #This function occurs after the human plays, so betting should occur next.
            for i in opp_order:
                opp = self.opponents[i]
                if not opp.out_of_game and not opp.defeated:
                    bet = opp.should_bet(self.game.current_bet)
                    self.game.bet(opp, bet)

            #Check to see if shifting is necessary.
            if self.game.should_shift([random.randint(1,6), random.randint(1,6)]):
                #Opponents discard
                lengths = []
                for opp in self.opponents:
                    length = len(opp.hand)
                    lengths.append(length)
                    if not opp.out_of_game and not opp.defeated:
                        for i in range(length-1, -1, -1):
                            self.game.discard(opp, i)
                #shift hands
                self.game.shift(lengths)
        
            #Now check if the game is over.
            if self.game.advance_round():
                break

            #If not, have all opponents make their moves.
            for num in opp_order:
                opp = self.opponents[num]
                if not opp.out_of_game and not opp.defeated:
                    move = opp.make_move(self.game.round_num+1, self.game.discard_pile)

                    if move[0] == "draw":
                        self.game.draw(opp)
                        #should_discard returns a card to drop.
                        drop = opp.should_discard()
                        if drop >= 0:
                            self.game.discard(opp, drop)
                            
                        elif move[0] == "swap":
                            #move[1] is the card to swap.
                            self.game.swap(opp, move[1])
                            self.discard_widgets.pop()
                            
                        elif move[0] == "junk":   
                            self.game.junk(opp)


    '''
    The function that handles both betting and raising for a user. It uses a match parameter
    to determine whether the bet needs to match the current bet or if it can be rasied by 50.

    Essentially, the player must first click Match before unlocking raise.
    '''
    def bet(self, match=False):
        #Tracks if they can't bet anymore.
        cutoff = False
        #Case for matching.
        if match:
            #If they can't even match the bet, they bet what chips they have and are cut off.
            if self.player.chips < self.game.current_bet:
                cutoff = True
                self.game.bet(self.player, self.player.chips)
            else:
                self.game.bet(self.player, self.game.current_bet)
            #Once the bet is matched, the user can't match again.
            self.ui.MatchButton.setEnabled(False)
        #Case for raising.
        else:
            #When a user has at least 50 chips, they raise by 50.
            if self.player.chips >= 50:
                self.game.bet(self.player, 50, True)
            #Otherwise, they raise by what they have.
            else:
                self.game.bet(self.player, self.player.chips, True)
                cutoff = True

        #Update GUI.
        self.ui.Userchips.setText(f"Your Chips: {self.player.chips}")
        self.ui.Userstake.setText(f"Your Stake: {self.player.stake}")
        self.ui.Gamepot.setText(f"Game Pot: {self.game.gamePot}")
        self.ui.CurBet.setText(f"Bet to Match: {self.game.current_bet}")

        #If they are out of chips, they can't bet anymore.
        if cutoff:
            QMessageBox.information(self, "Low Chips", "Looks like your out of chips! Don't worry, you can still keep playing!")
            self.done_betting()
        #Otherwise, enable the continue button to stop betting, or the raise button to keep betting.
        else:
            self.ui.ContButton.setEnabled(True)
            self.ui.RaiseButton.setEnabled(True)
    

    '''
    Very simple function that moves the game out of the betting phase. It disables all betting buttons and ends the round.
    '''
    def done_betting(self):
        self.ui.MatchButton.setEnabled(False)
        self.ui.RaiseButton.setEnabled(False)
        self.ui.ContButton.setEnabled(False)
        self.end_of_round()


    '''
    Very simple function to generate the dice roll results. It updates the proper dice GUI elements,
    and returns the rolled values. roll_dice() is called after betting has concluded.
    '''
    def roll_dice(self):
        self.ui.dice1.display(str(random.randint(1,6)))
        self.ui.dice2.display(str(random.randint(1,6)))
        print("Rolled Dice")
        print("Dice 1:", self.ui.dice1.value())
        print("Dice 2:", self.ui.dice2.value())
        return [self.ui.dice1.value(), self.ui.dice2.value()]


    '''
    This function manages the animations of the shift action, in which all players discard their entire hand and replace them
    with new ones of equal length. 
    '''
    def reset_hands(self):
        #Since the hands must have the same length after shifting, the old lengths must be saved before the hands are cleared.
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
            #shift=True so that a new round of betting does not begin.
            self.discard(i, shift=True)

        #Game logic will now redeal hands to each player according to their original lengths.
        self.game.shift(lengths)
        #Implement the dealing animations, without resetting the game.
        self.deal(True)



    #==============================CLEANUP=======================================#
    '''
    These functions are for cleanup. They include reset(), a bulky function that reinitializes GUI and game logic
    as well as clear_game(), which animates the resetting of the Game logic.
    '''

    '''
    Main function used to reset the GUI and game elements. The hard parameter is set to true when a user leaves the Sabacc Screen.
    In a "hard reset", the SabaccPlayer, SabaccAI, and Sabacc game logic classes are completely reset, and the sabacc_pot is reinitialized
    as well. In a soft reset, only minimal elements, such as the GUI displays for their chip and stake amounts are updated.
    '''
    def reset(self, hard=False):
        #Remove any and all widgets that may somehow remain.
        for item in self.scene.items():
            self.scene.removeItem(item)
        self.scene.clear()

        self.state.chips = self.player.chips

        #Reset/disable buttons.
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
        self.ui.leaveButton.setEnabled(True)
        self.ui.dice1.display("-")
        self.ui.dice2.display("-")
        self.ui.MatchButton.setEnabled(False)
        self.ui.RaiseButton.setEnabled(False)
        self.ui.ContButton.setEnabled(False)

        for button in self.card_buttons:
            try:
                button.clicked.disconnect()
            except TypeError:
                pass

        #Completely clear out any discard_widgets that may still be present
        self.discard_widgets = []

        #use only for leaving. In this case, reset EVERYTHING.
        if hard:
            self.ui.oppcount.setEnabled(True)
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

        #GUI updates that apply in both hard and soft resetting.
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

    

    '''
    In this function, the animations for cleaning up the game are made. Essentially, all the cards from hands and the discard pile are
    returned to the deck (animated to the deck graphic).
    '''
    def clear_game(self):
        #Purge all widgets from the scene. They'll be replaced with new AnimatedCards.
        for item in self.scene.items():
            self.scene.removeItem(item)

        #First animate the return of discards.
        for i in range(len(self.game.discard_pile)):
            self.animateCard(self.ui.discard_spot.pos(), self.deck_pos, self.createCard(self.game.discard_pile[i]))

        #Animate all opponents' hands.
        for opp in self.opponents:
            for i in range(len(opp.hand)):
                self.animateCard((opp.position + QPointF(i * 20, 0)), self.deck_pos, self.createCard(opp.hand[i]))
                opp.hand_widgets[i] = None
            #Clear out the hand.
            opp.hand = []

        #Animate user's hand.
        for i in range(len(self.player.hand)):
                self.animateCard(self.card_pos[i], self.deck_pos, self.createCard(self.player.hand[i]))
                self.player.hand_widgets[i] = None
        self.player.hand = []
            
        #Performs acutal game logic resetting.
        self.game.reset()


    #=================GAME FLOW CONTROL==========================================#
    '''
    Main block of code that manages the flow of a single game of Sabacc. begin_game() is called first.
    Then, round->plays_over->end_of_round occur in a loop until the game logic decides its over. Then,
    game_over() occurs, followed by aftermath(), which handles chip rewarding, player removing, and soft
    resetting. If a player junks during their turn, the data flow is slightly different, from round->game_over(True)->background_finish.
    Then, game_over calls aftermath.
    '''  


    '''
    Handles the start of a standard round. Here, each opponent, in a fixed order, makes their gameplay decision. These decisions are animated in sequential order,
    and all reported to the screen. thsi function then enables the player's move buttons, and allows them to make their move.
    '''
    def round(self):
        #This order occurs so that the leftmost player (Chewbacca) plays, then the center, then the rightmost.
        opp_order = [2, 0, 1]
        #Stores the moves made by each opponent.
        report_str = ""
        #Useful variable for animation synchonization.
        i = 1

        #Allow opponents to make their move.
        for num in opp_order:
            opp = self.opponents[num]
            #Don't give defeated or junked players a move.
            if not opp.out_of_game and not opp.defeated:
                #Obtain the opp's decision.
                move = opp.make_move(self.game.round_num+1, self.game.discard_pile)
                report_str += f"{opp.name} chose to {move[0]}"

                #Case for drawing.
                if move[0] == "draw":
                    #The opponent's drawing is done here, not in self.draw(), so that the discard action does not have to wait until the draw animation
                    #is complete.
                    self.game.draw(opp)
                    QTimer.singleShot(1000 * i, lambda offset=i, a=opp: self.draw(a))
                    i+=1

                    #Pick a card to discard.
                    drop = opp.should_discard()
                    if drop >= 0:
                        report_str += f" and discard"
                        QTimer.singleShot(1000 * i, lambda c=drop, a=opp: self.discard(c, a))
                        i+=1

                #Case for swap.
                elif move[0] == "swap":
                    QTimer.singleShot(1000 * i, lambda m=move, a=opp: self.swap_helper(m[1], a))
                    i+=1
                #Case for junk.
                elif move[0] == "junk":
                    QTimer.singleShot(1000*i, lambda a=opp: self.junk(a))
                    i+=1
                #Case for standing.
                else:
                    QTimer.singleShot(1000*i, lambda a=opp: self.stand(a))
                
                report_str += ".\n"
            
        #Report opponents' moves, enable player's buttons, since it's their turn.
        QTimer.singleShot(1000*i, lambda s=report_str: QMessageBox.information(self, "Opponents' Moves", s))
        QTimer.singleShot(1000*i, lambda: self.ui.drawButton.setEnabled(True))
        QTimer.singleShot(1000*i, lambda: self.ui.swapButton.setEnabled(True))
        QTimer.singleShot(1000*i, lambda: self.ui.junkButton.setEnabled(True))
        QTimer.singleShot(1000*i, lambda: self.ui.standButton.setEnabled(True))
        #Player can't leave during the animations to prevent crashing.
        QTimer.singleShot(1000*i, lambda: self.ui.leaveButton.setEnabled(True))
        


    '''
    Function that occurs after a user finishes their play. It generates the bets for each opponent, reports them to the screen,
    and then allows the user to bet if they have chips. If they have no chips, it skips to end_of_round().
    '''
    def plays_over(self):
        #Disable buttons as a catchall.
        self.ui.drawButton.setEnabled(False)
        self.ui.swapButton.setEnabled(False)
        self.ui.junkButton.setEnabled(False)
        self.ui.standButton.setEnabled(False)

        #Determine bet amount for each ACTIVE opponent.
        opp_order = [2, 0, 1]
        report_str = ''
        for i in opp_order:
            opp = self.opponents[i]
            #Opp can't bet if they junked or were defeated.
            if not opp.out_of_game and not opp.defeated:
                #This is where the actual bet amount is determined.
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

        #Skip right to the end of the round if the user has no chips.
        if self.player.chips == 0:
            report_str += "Looks like you already bet all your chips...May the Force Be With You, because the dice certainly won't."
            QMessageBox.information(self, "Bet Summary", report_str)
            QTimer.singleShot(500, self.done_betting)
        #Otherwise, enable the MATCH button ONLY. They must first match before they can raise or continue.
        else:
            report_str += "Now it's your turn! First click Match to match the current bet.\nThen, you can raise it by 50 as much as you can, or click continue!"
            QMessageBox.information(self, "Bet Summary", report_str)
            self.ui.MatchButton.setEnabled(True)
        return




    '''
    This function occurs after the player's betting is complete. This implements the dice roll, and iniates any
    shifting if necessary. IF the game is still over (not the end of round 3), then a new round is initiated. Otherwise,
    game_over() is called.
    '''
    def end_of_round(self):
        not_over = self.game.advance_round()
        #Run if the game's not over.
        if not_over:
            #Checks if the dice came up doubles.
            if self.game.should_shift(self.roll_dice()):
                #in this case, reset the hands and start a new round.
                QMessageBox.information(self, "Doubles!", "Dice came up doubles! Time to shift!")
                self.reset_hands()
                self.round()
            else:
                self.round()
        #Pretty much the same thing, but the game ends after a potential shift.
        else:
            if self.game.should_shift(self.roll_dice()):
                QMessageBox.information(self, "Doubles!", "Dice came up doubles! Time to shift!")
                self.reset_hands()
                QTimer.singleShot(1000, self.game_over)
            else:
                self.game_over()



    '''
    This is the first function that is called to begin a game.
    '''
    def begin_game(self):
        #Disable the leave button while animations occur.
        self.ui.leaveButton.setEnabled(False)
        #Initial entry fees.
        self.game.entry_fees()
        #Update user's and opponents' GUI labels and the game pot.
        self.ui.Userchips.setText(f"Your Chips: {self.player.chips}")
        self.ui.Userstake.setText(f"Your Stake: {self.player.stake}")
        for i in range(len(self.opponents)):
            opp = self.opponents[i]
            if not opp.defeated:
                self.oppstuff[i+3].setText(f"Chips: {opp.chips}")
                self.oppstuff[i+6].setText(f"Stake: {opp.stake}")
        self.ui.Sabaccpot.setText(f"Sabacc Pot: {self.game.sabbacpot}")

        #Setup discard pile, animate changes, deal, then start the first round.
        self.game.initialize_discard_pile()
        self.updateDiscard(self.deck_pos)
        self.deal()
        self.round()



    '''
    Main function for payout determination and allocation. It also handles removing any
    players who are now out of chips, potentially including the user.
    '''
    def aftermath(self, winner):
        #Determine payout.
        payout = self.game.determine_payout(winner)

        #Add payout to the winning opponent.
        for i in range(len(self.opponents)):
            opp = self.opponents[i]
            if opp.name == winner.name:
                opp.chips += payout
            self.oppstuff[i+3].setText(f"Chips: {opp.chips}")
            self.oppstuff[i+6].setText(f"Stake: ")

        #Remove opponent after payout allocation, but only if they haven't already been removed.
        for j in range(len(self.opponents)):
            opp = self.opponents[j]
            if opp.chips <= 0 and not opp.defeated:
                self.defeatOpp(j)

        #Case for the user winning.
        if winner.name == "user":
            self.player.chips += payout
            self.ui.Userchips.setText(f"Your Chips: {self.player.chips}")
            self.ui.Userstake.setText(f"Your Stake: ")
            QMessageBox.information(self, "You Win!", f"You won {payout} chips with a score of {winner.calc_hand_value()}")
           
            #Check how many opponents are not defeated.
            alive = 0
            for opp in self.opponents:
                if not opp.defeated:
                    alive+=1
            
            #If all opponents have been defeated, force the user to exit.
            if alive == 0:
                QMessageBox.information(self, "Flawless Victory", "WOW! You beat...everyone! Come back later!")
                self.leave()
                return
        #Case for player loss.
        else:
            QMessageBox.information(self, "You Lose!", f"{winner.name} won {payout} chips with a score of {winner.calc_hand_value()}")

            #If the player's out of chips, they need to be removed.
            if self.player.chips <= 0:
                self.ui.Userstake.setText(f"Your Stake: ")
                QMessageBox.information(self, "Defeat", "No more chips? GET OUTTA HERE!")
                self.game.reset()
                self.leave()
                return

        QTimer.singleShot(500, lambda: self.clear_game())
        #Give the animations time to actually run.
        QTimer.singleShot(3000, lambda: self.reset())


    '''
    Basic function to get to the end of a game. Handles fast forwarding if the user junks out of the game.
    Otherwise, it simply reveals each potentially hidden card in the opponents' hands. Then passes control to aftermath.
    '''
    def game_over(self, fast_frwd=False):
        #If the user junked, finish the game in the background.
        if fast_frwd:
            self.background_finish()
        #If not, reveal each Opponent's card.
        else:
            for opp in self.opponents:
                for i in range(len(opp.hand)):
                    self.scene.removeItem(opp.hand_widgets[i])
                    opp.hand_widgets[i] = self.scene.addPixmap(self.createCard(opp.hand[i]))
                    opp.hand_widgets[i].setPos(opp.position + QPointF(i * 20, 0))
    
        #Determine winner and pass to the aftermath function.
        self.aftermath(self.game.determine_winner())



    


#====================================GAME LOGIC CLASS===============================================#
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


    #Simply increases the round number, and returns True if the round number is < 3, meaning there are more rounds to play.
    def advance_round(self):
        self.round_num += 1
        return self.round_num < 3
    
    '''
    Function that resets all relevant game fields, such as the pot, the discard_pile, and the deck.
    '''
    def reset(self):
        self.round_num = 0
        self.reset_bet()
        self.gamePot = 0
        self.discard_pile = []
        self.deck = Sabacc_Deck()
        self.update_players()
        self.playing = False
    
    '''
    Clears the out_of_game field for all players (defeated players still won't be able to play.)
    '''
    def update_players(self):
        for player in self.players:
            player.out_of_game = False

    #Simply returns true if a shift is warranted (dice results are doubles)
    def should_shift(self, results):
        return results[0] == results[1]
    
    #When a shift occurs, each active player receives a new hand equal in length to their old one (specified by the lengths array)
    def shift(self, lengths):
        for num in range(len(lengths)):
            if not self.players[num].out_of_game and not self.players[num].defeated:
                self.deal(self.players[num], lengths[num])


    """Determines and announces the winner of the game and distributes the pot."""
    def determine_winner(self):
        track_winner = None
        for player in self.players:
            print(f"{player.name}'s Hand: {player.hand} with value {player.calc_hand_value()}")
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
                        """Found a player with the same hand value, check for more cards win."""
                        if len(player.hand) > len(track_winner.hand):
                            track_winner = player
                        elif len(player.hand) == len(track_winner.hand):
                            """Found a player with the same hand value and same number of cards, check for highest value card to break the tie."""
                            player_max_max_card = max(player.hand, key=lambda c: c.rank)
                            track_winner_max_card = max(track_winner.hand, key=lambda c: c.rank)
                            if player_max_max_card.rank > track_winner_max_card.rank:
                                track_winner = player
                            elif player_max_max_card.rank == track_winner_max_card.rank and player.name=="user":
                                track_winner = player
        return track_winner


    '''
    Simply deducts 50 chips from each undefeated player, adding it to the pot.
    '''
    def entry_fees(self):
        for player in self.players:
            if not player.defeated:
                self.sabbacpot += 50
                player.chips += -50


    '''
    Simple payout determination for a winning player. 
    '''
    def determine_payout(self, winner):
        #Of course, they get the pot.
        payout = self.gamePot
        #Check if they have a score of 0
        true_sabbac = winner.calc_hand_value() == 0
        #If so, they also get the sabbacpot, which is reset to zero
        if true_sabbac:
            payout += self.sabbacpot
            self.sabbacpot = 0
        return payout
    

    '''
    Simple function allowing a player to bet a specified amount.
    The is_raise flag allows for the human user to incrementally bet 50 after matching.
    '''
    def bet(self, player, amount, is_raise = False):
        #Increase the game pot by the amount, and adjust player-specific chip counts.
        self.gamePot += amount
        player.stake += amount
        player.chips += -1 * amount
        #If the bet amount is higher than the current bet, then raise the bet to that current amount.
        if amount > self.current_bet:
            self.current_bet = amount
        #If it's explicitly specified as a raise, just add the amount to the current bet.
        elif is_raise:
            self.current_bet += amount
    
    #Simple function that just sets the current bet back to 0.
    def reset_bet(self):
        self.current_bet = 0