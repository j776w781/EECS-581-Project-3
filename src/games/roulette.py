from PyQt6.QtWidgets import QWidget, QGraphicsScene, QGraphicsObject, QGraphicsView, QPushButton, QMessageBox, QGraphicsPixmapItem
from PyQt6.QtCore import QObject, QPropertyAnimation, QPointF, QEasingCurve, QRectF, pyqtProperty, QTimer, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QColor
from .ui.roulette_ui import Ui_RouletteScreen
from .objects.table import Number, Table, Wheel
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TABLE_DIR = os.path.join(BASE_DIR, "../assets/table.jpg")
WHEEL_DIR = os.path.join(BASE_DIR, "../assets/wheel.png")
PTR_DIR = os.path.join(BASE_DIR, "../assets/pointer.png")

class AnimatedWheel(QObject):
    def __init__(self, pixmap_item):
        super().__init__()
        self._rotation = 0
        self.item = pixmap_item

    def getRotation(self):
        return self._rotation

    def setRotation(self, value):
        self._rotation = value
        self.item.setRotation(value)  # update the QGraphicsPixmapItem

    rotation = pyqtProperty(float, getRotation, setRotation)

class RouletteScreen(QWidget):
    #Connect to main window.
    switch_to_menu = pyqtSignal()

    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.ui = Ui_RouletteScreen()
        self.ui.setupUi(self)
        self.ui.tableLabel.setPixmap(QPixmap(TABLE_DIR))
        self.ui.wheelLabel.setPixmap(QPixmap(WHEEL_DIR))
        self.ui.label.setPixmap(QPixmap(PTR_DIR))

        #Used to stop betting during wheel spin.
        self.can_bet = True
        
        self.state = state
        self.game = Roulette()

        # Set up the scene for wheel animation.
        self.ui.wheelLabel.hide() # Remove static wheel picture.
        self.scene = QGraphicsScene(self) # Create graphic scene.
        self.ui.graphicsView.setScene(self.scene) # Put scene in graphicView.
        wheel_pixmap = QPixmap(WHEEL_DIR) # Create wheel sprite.
        self.wheel_item = QGraphicsPixmapItem(wheel_pixmap) # Create graphic wheel sprite.
        self.wheel_item.setTransformationMode(Qt.TransformationMode.SmoothTransformation) # Essentially creates movement more fluidly.
        self.wheel_item.setTransformOriginPoint(wheel_pixmap.width()/2, wheel_pixmap.height()/2) # Make wheel transform around its origin.
        
        # Move wheel so its corner appears from the graphicsView.
        self.wheel_item.setPos(self.ui.graphicsView.width() - (wheel_pixmap.width()/2), self.ui.graphicsView.height() - (wheel_pixmap.height()/2)) 
        self.scene.setSceneRect(0, 0, self.ui.graphicsView.width(), self.ui.graphicsView.height())
        # Remove scrollbars that let user move wheel sprite.
        self.ui.graphicsView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.ui.graphicsView.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # The user actually can still move the wheel sprite, but its negligible.

        # Add the wheel sprite to the view
        self.scene.addItem(self.wheel_item)

        self.ui.totalLabel.setText(f"Chip Total: {self.state.chips}")

        # Spin button handling. Animates wheel.
        self.ui.spinButton.clicked.connect(self.spin)

        #Leave button
        self.ui.leaveButton.clicked.connect(self.leave)

        # Single bets
        self.ui.s_0.clicked.connect(lambda: self.apply_bet("s_0"))
        self.ui.s_1.clicked.connect(lambda: self.apply_bet("s_1"))
        self.ui.s_2.clicked.connect(lambda: self.apply_bet("s_2"))
        self.ui.s_3.clicked.connect(lambda: self.apply_bet("s_3"))
        self.ui.s_4.clicked.connect(lambda: self.apply_bet("s_4"))
        self.ui.s_5.clicked.connect(lambda: self.apply_bet("s_5"))
        self.ui.s_6.clicked.connect(lambda: self.apply_bet("s_6"))
        self.ui.s_7.clicked.connect(lambda: self.apply_bet("s_7"))
        self.ui.s_8.clicked.connect(lambda: self.apply_bet("s_8"))
        self.ui.s_9.clicked.connect(lambda: self.apply_bet("s_9"))
        self.ui.s_10.clicked.connect(lambda: self.apply_bet("s_10"))
        self.ui.s_11.clicked.connect(lambda: self.apply_bet("s_11"))
        self.ui.s_12.clicked.connect(lambda: self.apply_bet("s_12"))
        self.ui.s_13.clicked.connect(lambda: self.apply_bet("s_13"))
        self.ui.s_14.clicked.connect(lambda: self.apply_bet("s_14"))
        self.ui.s_15.clicked.connect(lambda: self.apply_bet("s_15"))
        self.ui.s_16.clicked.connect(lambda: self.apply_bet("s_16"))
        self.ui.s_17.clicked.connect(lambda: self.apply_bet("s_17"))
        self.ui.s_18.clicked.connect(lambda: self.apply_bet("s_18"))
        self.ui.s_19.clicked.connect(lambda: self.apply_bet("s_19"))
        self.ui.s_20.clicked.connect(lambda: self.apply_bet("s_20"))
        self.ui.s_21.clicked.connect(lambda: self.apply_bet("s_21"))
        self.ui.s_22.clicked.connect(lambda: self.apply_bet("s_22"))
        self.ui.s_23.clicked.connect(lambda: self.apply_bet("s_23"))
        self.ui.s_24.clicked.connect(lambda: self.apply_bet("s_24"))
        self.ui.s_25.clicked.connect(lambda: self.apply_bet("s_25"))
        self.ui.s_26.clicked.connect(lambda: self.apply_bet("s_26"))
        self.ui.s_27.clicked.connect(lambda: self.apply_bet("s_27"))
        self.ui.s_28.clicked.connect(lambda: self.apply_bet("s_28"))
        self.ui.s_29.clicked.connect(lambda: self.apply_bet("s_29"))
        self.ui.s_30.clicked.connect(lambda: self.apply_bet("s_30"))
        self.ui.s_31.clicked.connect(lambda: self.apply_bet("s_31"))
        self.ui.s_32.clicked.connect(lambda: self.apply_bet("s_32"))
        self.ui.s_33.clicked.connect(lambda: self.apply_bet("s_33"))
        self.ui.s_34.clicked.connect(lambda: self.apply_bet("s_34"))
        self.ui.s_35.clicked.connect(lambda: self.apply_bet("s_35"))
        self.ui.s_36.clicked.connect(lambda: self.apply_bet("s_36"))

        # Split bets
        self.ui.p_1_2.clicked.connect(lambda: self.apply_bet("p_1_2"))
        self.ui.p_2_3.clicked.connect(lambda: self.apply_bet("p_2_3"))
        self.ui.p_4_5.clicked.connect(lambda: self.apply_bet("p_4_5"))
        self.ui.p_5_6.clicked.connect(lambda: self.apply_bet("p_5_6"))
        self.ui.p_7_8.clicked.connect(lambda: self.apply_bet("p_7_8"))
        self.ui.p_8_9.clicked.connect(lambda: self.apply_bet("p_8_9"))
        self.ui.p_10_11.clicked.connect(lambda: self.apply_bet("p_10_11"))
        self.ui.p_11_12.clicked.connect(lambda: self.apply_bet("p_11_12"))
        self.ui.p_13_14.clicked.connect(lambda: self.apply_bet("p_13_14"))
        self.ui.p_14_15.clicked.connect(lambda: self.apply_bet("p_14_15"))
        self.ui.p_16_17.clicked.connect(lambda: self.apply_bet("p_16_17"))
        self.ui.p_17_18.clicked.connect(lambda: self.apply_bet("p_17_18"))
        self.ui.p_19_20.clicked.connect(lambda: self.apply_bet("p_19_20"))
        self.ui.p_20_21.clicked.connect(lambda: self.apply_bet("p_20_21"))
        self.ui.p_22_23.clicked.connect(lambda: self.apply_bet("p_22_23"))
        self.ui.p_23_24.clicked.connect(lambda: self.apply_bet("p_23_24"))
        self.ui.p_25_26.clicked.connect(lambda: self.apply_bet("p_25_26"))
        self.ui.p_26_27.clicked.connect(lambda: self.apply_bet("p_26_27"))
        self.ui.p_28_29.clicked.connect(lambda: self.apply_bet("p_28_29"))
        self.ui.p_29_30.clicked.connect(lambda: self.apply_bet("p_29_30"))
        self.ui.p_31_32.clicked.connect(lambda: self.apply_bet("p_31_32"))
        self.ui.p_32_33.clicked.connect(lambda: self.apply_bet("p_32_33"))
        self.ui.p_34_35.clicked.connect(lambda: self.apply_bet("p_34_35"))
        self.ui.p_35_36.clicked.connect(lambda: self.apply_bet("p_35_36"))
        self.ui.p_1_4.clicked.connect(lambda: self.apply_bet("p_1_4"))
        self.ui.p_2_5.clicked.connect(lambda: self.apply_bet("p_2_5"))
        self.ui.p_3_6.clicked.connect(lambda: self.apply_bet("p_3_6"))
        self.ui.p_4_7.clicked.connect(lambda: self.apply_bet("p_4_7"))
        self.ui.p_5_8.clicked.connect(lambda: self.apply_bet("p_5_8"))
        self.ui.p_6_9.clicked.connect(lambda: self.apply_bet("p_6_9"))
        self.ui.p_7_10.clicked.connect(lambda: self.apply_bet("p_7_10"))
        self.ui.p_8_11.clicked.connect(lambda: self.apply_bet("p_8_11"))
        self.ui.p_9_12.clicked.connect(lambda: self.apply_bet("p_9_12"))
        self.ui.p_10_13.clicked.connect(lambda: self.apply_bet("p_10_13"))
        self.ui.p_11_14.clicked.connect(lambda: self.apply_bet("p_11_14"))
        self.ui.p_12_15.clicked.connect(lambda: self.apply_bet("p_12_15"))
        self.ui.p_13_16.clicked.connect(lambda: self.apply_bet("p_13_16"))
        self.ui.p_14_17.clicked.connect(lambda: self.apply_bet("p_14_17"))
        self.ui.p_15_18.clicked.connect(lambda: self.apply_bet("p_15_18"))
        self.ui.p_16_19.clicked.connect(lambda: self.apply_bet("p_16_19"))
        self.ui.p_17_20.clicked.connect(lambda: self.apply_bet("p_17_20"))
        self.ui.p_18_21.clicked.connect(lambda: self.apply_bet("p_18_21"))
        self.ui.p_19_22.clicked.connect(lambda: self.apply_bet("p_19_22"))
        self.ui.p_20_23.clicked.connect(lambda: self.apply_bet("p_20_23"))
        self.ui.p_21_24.clicked.connect(lambda: self.apply_bet("p_21_24"))
        self.ui.p_22_25.clicked.connect(lambda: self.apply_bet("p_22_25"))
        self.ui.p_23_26.clicked.connect(lambda: self.apply_bet("p_23_26"))
        self.ui.p_24_27.clicked.connect(lambda: self.apply_bet("p_24_27"))
        self.ui.p_25_28.clicked.connect(lambda: self.apply_bet("p_25_28"))
        self.ui.p_26_29.clicked.connect(lambda: self.apply_bet("p_26_29"))
        self.ui.p_27_30.clicked.connect(lambda: self.apply_bet("p_27_30"))
        self.ui.p_28_31.clicked.connect(lambda: self.apply_bet("p_28_31"))
        self.ui.p_29_32.clicked.connect(lambda: self.apply_bet("p_29_32"))
        self.ui.p_30_33.clicked.connect(lambda: self.apply_bet("p_30_33"))
        self.ui.p_31_34.clicked.connect(lambda: self.apply_bet("p_31_34"))
        self.ui.p_32_35.clicked.connect(lambda: self.apply_bet("p_32_35"))
        self.ui.p_33_36.clicked.connect(lambda: self.apply_bet("p_33_36"))

        #triple bets
        self.ui.tr_0_1_2.clicked.connect(lambda: self.apply_bet("tr_0_1_2"))
        self.ui.tr_0_2_3.clicked.connect(lambda: self.apply_bet("tr_0_2_3"))

        # Quad bets
        self.ui.q_1_2_4_5.clicked.connect(lambda: self.apply_bet("q_1_2_4_5"))
        self.ui.q_2_3_5_6.clicked.connect(lambda: self.apply_bet("q_2_3_5_6"))
        self.ui.q_4_5_7_8.clicked.connect(lambda: self.apply_bet("q_4_5_7_8"))
        self.ui.q_5_6_8_9.clicked.connect(lambda: self.apply_bet("q_5_6_8_9"))
        self.ui.q_7_8_10_11.clicked.connect(lambda: self.apply_bet("q_7_8_10_11"))
        self.ui.q_8_9_11_12.clicked.connect(lambda: self.apply_bet("q_8_9_11_12"))
        self.ui.q_10_11_13_14.clicked.connect(lambda: self.apply_bet("q_10_11_13_14"))
        self.ui.q_11_12_14_15.clicked.connect(lambda: self.apply_bet("q_11_12_14_15"))
        self.ui.q_13_14_16_17.clicked.connect(lambda: self.apply_bet("q_13_14_16_17"))
        self.ui.q_14_15_17_18.clicked.connect(lambda: self.apply_bet("q_14_15_17_18"))
        self.ui.q_16_17_19_20.clicked.connect(lambda: self.apply_bet("q_16_17_19_20"))
        self.ui.q_17_18_20_21.clicked.connect(lambda: self.apply_bet("q_17_18_20_21"))
        self.ui.q_19_20_22_23.clicked.connect(lambda: self.apply_bet("q_19_20_22_23"))
        self.ui.q_20_21_23_24.clicked.connect(lambda: self.apply_bet("q_20_21_23_24"))
        self.ui.q_22_23_25_26.clicked.connect(lambda: self.apply_bet("q_22_23_25_26"))
        self.ui.q_23_24_26_27.clicked.connect(lambda: self.apply_bet("q_23_24_26_27"))
        self.ui.q_25_26_28_29.clicked.connect(lambda: self.apply_bet("q_25_26_28_29"))
        self.ui.q_26_27_29_30.clicked.connect(lambda: self.apply_bet("q_26_27_29_30"))
        self.ui.q_28_29_31_32.clicked.connect(lambda: self.apply_bet("q_28_29_31_32"))
        self.ui.q_29_30_32_33.clicked.connect(lambda: self.apply_bet("q_29_30_32_33"))
        self.ui.q_31_32_34_35.clicked.connect(lambda: self.apply_bet("q_31_32_34_35"))
        self.ui.q_32_33_35_36.clicked.connect(lambda: self.apply_bet("q_32_33_35_36"))

        # Single row bets
        self.ui.r_1.clicked.connect(lambda: self.apply_bet("r_1"))
        self.ui.r_2.clicked.connect(lambda: self.apply_bet("r_2"))
        self.ui.r_3.clicked.connect(lambda: self.apply_bet("r_3"))
        self.ui.r_4.clicked.connect(lambda: self.apply_bet("r_4"))
        self.ui.r_5.clicked.connect(lambda: self.apply_bet("r_5"))
        self.ui.r_6.clicked.connect(lambda: self.apply_bet("r_6"))
        self.ui.r_7.clicked.connect(lambda: self.apply_bet("r_7"))
        self.ui.r_8.clicked.connect(lambda: self.apply_bet("r_8"))
        self.ui.r_9.clicked.connect(lambda: self.apply_bet("r_9"))
        self.ui.r_10.clicked.connect(lambda: self.apply_bet("r_10"))
        self.ui.r_11.clicked.connect(lambda: self.apply_bet("r_11"))
        self.ui.r_12.clicked.connect(lambda: self.apply_bet("r_12"))

        # Paired row bets
        self.ui.rp_1_2.clicked.connect(lambda: self.apply_bet("rp_1_2"))
        self.ui.rp_2_3.clicked.connect(lambda: self.apply_bet("rp_2_3"))
        self.ui.rp_3_4.clicked.connect(lambda: self.apply_bet("rp_3_4"))
        self.ui.rp_4_5.clicked.connect(lambda: self.apply_bet("rp_4_5"))
        self.ui.rp_5_6.clicked.connect(lambda: self.apply_bet("rp_5_6"))
        self.ui.rp_6_7.clicked.connect(lambda: self.apply_bet("rp_6_7"))
        self.ui.rp_7_8.clicked.connect(lambda: self.apply_bet("rp_7_8"))
        self.ui.rp_8_9.clicked.connect(lambda: self.apply_bet("rp_8_9"))
        self.ui.rp_9_10.clicked.connect(lambda: self.apply_bet("rp_9_10"))
        self.ui.rp_10_11.clicked.connect(lambda: self.apply_bet("rp_10_11"))
        self.ui.rp_11_12.clicked.connect(lambda: self.apply_bet("rp_11_12"))

        # Half bets
        self.ui.h_1.clicked.connect(lambda: self.apply_bet("h_1"))
        self.ui.h_2.clicked.connect(lambda: self.apply_bet("h_2"))

        # Column bets
        self.ui.c_1.clicked.connect(lambda: self.apply_bet("c_3"))
        self.ui.c_2.clicked.connect(lambda: self.apply_bet("c_2"))
        self.ui.c_3.clicked.connect(lambda: self.apply_bet("c_1"))

        #Twelves bets
        self.ui.tw_1.clicked.connect(lambda: self.apply_bet("tw_1"))
        self.ui.tw_2.clicked.connect(lambda: self.apply_bet("tw_2"))
        self.ui.tw_3.clicked.connect(lambda: self.apply_bet("tw_3"))

        # Even/Odd bets
        self.ui.even.clicked.connect(lambda: self.apply_bet("e"))
        self.ui.odd.clicked.connect(lambda: self.apply_bet("o"))

        # Red/Black bets
        self.ui.red.clicked.connect(lambda: self.apply_bet("rd"))
        self.ui.black.clicked.connect(lambda: self.apply_bet("b"))




        #TEMPLATE FOR BUTTON CONNECTIONS
        #Assumes the user has clicked the 3 space, placing a bet on 3.
        #SINGLE NUMBER betcode should be of the form s_#, where s stands for single, # is the actual betting number.
        #Pairs: p_#_#
        #Triples: tr_#_#_#
        #Quads: q_#_#_#_#
        #Rows: r_# (Row 1 is 1, 2, 3)
        #Row Pair: rp_#_# (# are row numbers)
        #Col: c_# (Col 1 is the one with 1)
        #Twelves: tw_#
        #Halves: h_#
        #Red/black: rd/b
        #Even/Odd: e/o
        #Code to put:
        #self.ui.s_3.clicked.connect(lambda: self.apply_bet("s_3"))

        #IN THE GUI, SET THE BUTTON'S NAME TO THE BETCODE. USE GAVIN'S WORK AS AN EXAMPLE.

    #Wrapper for adding a bet to the game logic. Simply passes it to the appropriate Roulette method.
    #NOTE: We could also use this to add chip graphics if we have time/update the "chips bet" for a button.
    #If we have to update the function call for that(pass in self.ui.[button] as well, I can do the tedium, since I should have thought about this before.)
    def apply_bet(self, betcode, chipamount=50):
        #This effectively disables all the betting buttons(can still click, but nothing happens)
        if self.can_bet:
            #No betting once you've run out of chips.
            if self.state.chips > 0:
                #Passes the betcode and chipamount to the Roulette class, which will record the bet for a possible payout.
                self.game.add_bet(betcode, chipamount)
                #Removes the chips from the user's balance. Does not immediately kick them out.
                self.state.chips = self.state.chips-chipamount
                #Updates chip total on GUI.
                self.ui.totalLabel.setText(f"Chip Total: {self.state.chips}")
            #Let's the user know they're out.
            else:
                QMessageBox.information(self, "No chips", f"You're all out, buddy! Spin the wheel and start prayin!")




    # Function to animate wheel to spin.
    def spin(self):
        #Disable betting during the wheel spin.
        self.can_bet = False

        print('Spinning...')
        self.ui.spinButton.setEnabled(False)
        self.rotatable_wheel = AnimatedWheel(self.wheel_item)
        self.animation = QPropertyAnimation(self.rotatable_wheel, b'rotation')
        self.animation.setDuration(4000)  # 4 seconds

        # Use the power of MATH to spin the wheel to our random desintation. 
        #target_index = self.game.wheel.spin()

        #Lets the GameLogic class give us the index for the wheel animation and the numerical result.
        target_index, result = self.game.spin_wheel()
        final_angle = (5*-360) + target_index * -9.729 # Spins 5 full times before landing on random value.

        # Set start and ending values of animation.
        self.animation.setStartValue(0)
        self.animation.setEndValue(final_angle)  # spin 5 full turns + offset
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic) # Adjusts acceleration of animation.
        self.animation.start() # Begin the animation!

        # Do not enable the spin button again until the animation is completely finished.
        QTimer.singleShot(4000, Qt.TimerType.PreciseTimer, lambda: self.ui.spinButton.setEnabled(True))
        QTimer.singleShot(4100, Qt.TimerType.PreciseTimer, lambda: self.aftermath())

        # Now grab the legitimate result (that should line up with the wheel).
        #result = self.game.wheel.order[target_index]
        print("The winning number is:", result) # Test print to see result.

    
    '''
    This function should be called immediately after the wheel animation has spun. All it does is obtain the final payout,
    add it to the player's chips, and notify the user of how many chips they won.
    '''
    def aftermath(self):
        #Get our payout from our bets.
        payout = self.game.generate_payout()
        #Update our chips with the payout.
        self.state.chips += payout
        #Update the GUI's chip total.
        self.ui.totalLabel.setText(f"Chip Total: {self.state.chips}")
        #Let the user know what they've won.
        QMessageBox.information(self, "Chips gained.", f"Good job! Your bets gained you {payout} chips!")
        #Reset the Roulette's result and bets.
        self.game.reset()
        # If player has no chips get them out!
        if self.state.chips == 0:
            QMessageBox.information(self, "No chips.", "No chips? Get out!")
            self.leave()
        #Re-enable betting.
        self.can_bet = True

        

    def leave(self):
        #If the user has already placed bets, let them know the bad news.
        if len(self.game.bets) != 0:
            QMessageBox.information(self, "Abandoning chips", f"Haha, you just gave up your chips.")
        #Reset game state.
        self.game.reset()
        #Re-enable betting.
        self.switch_to_menu.emit()


class Roulette:
    def __init__(self):
        self.table = Table()
        self.wheel = Wheel()
        self.bets = []
        self.result = None



    #Simple function that restores the initial state of the Roulette class.
    def reset(self):
        #Clear all prior bets.
        self.bets = []
        #Remove the prior wheel result.
        self.result = None
        print("Game reset.")



    #Basic wrapper for the wheel class. I don't think the RouletteScreen class really needs
    #to interact with the Wheel class at all (coupling).
    def spin_wheel(self):
        #Get the proper index, since RouletteScreen will need it for the animation.
        idx = self.wheel.spin()
        #Save the result of the wheel spin for payout generation.
        self.result = self.wheel.order[idx]
        #Return the wheel index and numerical result for the RouletteScreen's use.
        return idx, self.result.value




    '''
    This is the function used to add a bet for future payout generation. Note that bets in this
    program will be represented as a "tuple" (a two element list for indexing ability). The 
    first index will be the bet_code as defined below:

    #SINGLE NUMBER betcode should be of the form s_#, where s stands for single, # is the actual betting number.
    Pairs: p_#_#
    Triples: tr_#_#_#
    Quads: q_#_#_#_#
    Rows: r_# (Row 1 is 1, 2, 3)
    Row Pair: rp_#_# (# are row numbers)
    Col: c_# (Col 1 is the one with 1)
    Twelves(Thirds): tw_#
    Halves: h_#
    Red/black: rd/b
    Even/Odd: e/o

    There should only be one instance of a bet_code in self.bets at any given time. Therefore, if a user
    decides to add chips onto a bet they've made before, this code intuitively adds those chips to the existing
    bet in self.bets.
    '''
    def add_bet(self, bet_code, chips_bet):
        #If there's no bets currently, no need to check existing bets for matches.
        if len(self.bets) == 0:
            #Just add the bet.
            self.bets.append([bet_code, chips_bet])
            print(f"Bet added: {bet_code} for {chips_bet}")
            return
        #If there are bets, must check to see if the user is increasing a previous bet or making a new one.
        else:
            #Go through each bet one-by-one.
            for i in range(len(self.bets)):
                #Check for a matching bet_code.
                if self.bets[i][0] == bet_code:
                    #If there's a match, don't add a new bet, just increase the chips of the prior bet.
                    self.bets[i][1] += chips_bet
                    print(f"Bet for {bet_code} increased to {self.bets[i][1]} chips")
                    return
            #If the code makes it through, there were no matches, so this is a new bet. Add it.
            self.bets.append([bet_code, chips_bet])
            print(f"Bet added: {bet_code} for {chips_bet}")
            return



    '''
    This bulky function takes in a bet "tuple" ([bet_code, chip amount]). It checks if the
    wheel's result, saved in self.result, validates the bet. If so, it returns the proper
    payout amount based on roulette rules. If not, it merely returns 0.

    NOTE: You'll see that each payout multiplier is increased by 1. This is because the 
    betted chips are initially removed from the user's balance, so they must also be 
    restored upon success. Therefore, a 1x payout becomes 2x, and a 2x becomes 3x, and
    so on.
    '''
    def val_bet(self, bet):
        #Split up the bet code for further use.
        bet_code = bet[0].split("_")
        #Used for payout calculations.
        chips = bet[1]

        #Simplest way to check for each bet type.
        match bet_code[0]:
            #Case for single bet. Next element in bet_code will be the number.
            case "s":
                if int(bet_code[1]) == self.result.value:
                    return 36*chips
                else:
                    return 0
            #Case for pair bet. Next elements in bet_code will be the numbers.
            case "p":
                vals = [int(bet_code[1]), int(bet_code[2])]
                if self.result.value in vals:
                    return 18*chips
                else:
                    return 0
            #Case for triples bet. Next elements in bet_code will be the numbers.
            case "tr":
                vals = [int(bet_code[1]), int(bet_code[2]), int(bet_code[3])]
                if self.result.value in vals:
                    return 12*chips
                else:
                    return 0
            #Case for quad bet. Next elements in bet_code will be the numbers.
            case "q":
                vals = [int(bet_code[1]), int(bet_code[2]), int(bet_code[3]), int(bet_code[4])]
                if self.result.value in vals:
                    return 12*chips
                else:
                    return 0
            #Case for row bet. Next element in bet_code will be the row number.
            case "r":
                if self.result.row == int(bet_code[1]):
                    return 12*chips
                else:
                    return 0
            #Case for row pair bet. Next elements in bet_code will be the row numbers.
            case "rp":
                rows = [int(bet_code[1]), int(bet_code[2])]
                if self.result.row in rows:
                    return 6*chips
                else:
                    return 0
            #Case for red bet. Shouldn't have any other elements in bet_code.
            case "rd":
                if self.result.color == "red":
                    return 2*chips
                else:
                    return 0
            #Case for black bet. Shouldn't have any other elements in bet_code.
            case "b":
                if self.result.color == "black":
                    return 2*chips
                else:
                    return 0
            #Case for even bet. Shouldn't have any other elements in bet_code.
            case "e":
                if self.result.isEven and self.result.value != 0:
                    return 2*chips
                else:
                    return 0
            #Case for odd bet. Shouldn't have any other elements in bet_code.
            case "o":
                if not self.result.isEven:
                    return 2*chips
                else:
                    return 
            #Case for halves bet. Next element should be which half.
            case "h":
                if int(bet_code[1]) == self.result.half:
                    return 2*chips
                else:
                    return 0
            #Case for thirds(or twelves) bet. Next element should be which third(or twelve).
            case "tw":
                if int(bet_code[1]) == self.result.third:
                    return 3*chips
                else:
                    return 0
            #Case for column bet. Next element should be the column number.
            case "c":
                if int(bet_code[1]) == self.result.col:
                    return 3*chips
                else:
                    return 0
            #This case should never be reached. But, just in case, any invalid bet should have no payout.
            case _:
                return 0
        return



    '''
    This function should be called after the wheel has been spun and a result
    has been saved. It will process all recorded bets, computing the total
    payout from all the bets and returning it to the caller.
    '''
    def generate_payout(self):
        #Total bet payout initialization
        tot_payout = 0
        #Process all bets.
        for bet in self.bets:
            #Payout for each bet is computed.
            payout = self.val_bet(bet)
            #Simple debugging statement(make sure bets are actually matching).
            if payout > 0:
                print(f"Bet {bet[0]} netted {payout} chips.")
            #Add whatever payout(never less than 0) to the total.
            tot_payout += payout
        
        print(f"Your total payout is: {tot_payout}.")
        #Return this for the RouletteScreen to use.
        return tot_payout