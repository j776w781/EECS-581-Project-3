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
    switch_to_menu = pyqtSignal()

    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.ui = Ui_RouletteScreen()
        self.ui.setupUi(self)
        self.ui.tableLabel.setPixmap(QPixmap(TABLE_DIR))
        self.ui.wheelLabel.setPixmap(QPixmap(WHEEL_DIR))
        self.ui.label.setPixmap(QPixmap(PTR_DIR))
        
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

        self.ui.totalLabel.setText(f"Your Total: {self.state.chips}")

        # Spin button handling. Animates wheel.
        self.ui.spinButton.clicked.connect(self.spin)

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
        #Passes the betcode and chipamount to the Roulette class, which will record the bet for a possible payout.
        self.game.add_bet(betcode, chipamount)
        #Removes the chips from the user's balance. Does not immediately kick them out.
        self.state.chips = self.state.chips-chipamount

    # Function to animate wheel to spin.
    def spin(self):
        print('Spinning...')
        self.ui.spinButton.setEnabled(False)
        self.rotatable_wheel = AnimatedWheel(self.wheel_item)
        self.animation = QPropertyAnimation(self.rotatable_wheel, b'rotation')
        self.animation.setDuration(4000)  # 4 seconds

        # Use the power of MATH to spin the wheel to our random desintation. 
        target_index = self.game.wheel.spin()
        final_angle = (5*-360) + target_index * -9.9 # Spins 5 full times before landing on random value.

        # Set start and ending values of animation.
        self.animation.setStartValue(0)
        self.animation.setEndValue(final_angle)  # spin 5 full turns + offset
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic) # Adjusts acceleration of animation.
        self.animation.start() # Begin the animation!

        # Do not enable the spin button again until the animation is completely finished.
        QTimer.singleShot(4000, Qt.TimerType.PreciseTimer, lambda: self.ui.spinButton.setEnabled(True))

        # Now grab the legitimate result (that should line up with the wheel).
        result = self.game.wheel.order[target_index]
        print("The winning number is:", result) # Test print to see result.

class Roulette:
    def __init__(self):
        self.table = Table()
        self.wheel = Wheel()
        self.bets = []
        self.result = 0


    def add_bet(self, bet_code, chips_bet):
        if len(self.bets) == 0:
            self.bets.append([bet_code, chips_bet])
            print(f"Bet added: {bet_code} for {chips_bet}")
            return
        else:
            for i in range(len(self.bets)):
                if self.bets[i][0] == bet_code:
                    self.bets[i][1] += chips_bet
                    print(f"Bet for {bet_code} increased to {self.bets[i][1]} chips")
                    return
            self.bets.append([bet_code, chips_bet])
            print(f"Bet added: {bet_code} for {chips_bet}")
            return
        

        
        #Don't worry about this. Just send me your bets and I'll be implemented later.
        return

    def insideBet(self):
        # Input with error handling for roulette number.
        i = 0
        while i == 0:
            try:
                num = int(input("\nPick a number to bet on: "))
                if num < 0 or num > 36:
                    raise
                num = Number(num)
                i = 1
            except:
                i = 0

        # Input with error handling for bet amount.
        i = 0
        while i == 0:
            try:
                print("\nChip total:", self.chips)
                bet = int(input("How much will you bet?: "))
                if bet > self.chips or bet < 0:
                    print("\nInvalid bet amount. Try again.")
                    raise
                self.chips -= bet
                i = 1
            except:
                i = 0
        
        result = self.wheel.spin()
        print("Result is:", result)
        if result == num:
            print("\nBet won! Congratulations!")
            self.chips += 36 * bet
        else:
            print("\nBet lost...")

    def play(self):
        print("\nWelcome to Roulette.")
        print("\n1) Inside Bet\n2) Outside Bet")

        # Get valid bet type input.
        i = 0
        while i == 0:
            bet_type = input("\nPick a bet type: ")
            bet_type = bet_type.lower()
            valid_bet_types =  ['1', '2', 'inside', 'outside', 'i', 'o']
            if bet_type in valid_bet_types:
                # Collapse valid bet type options into single options.
                if bet_type == '1' or bet_type == 'inside' or bet_type == 'i':
                    bet_type = 'inside'
                else:
                    bet_type = 'outside'
                i = 1
            else:
                print("Invalid option. Choose again.")
        
        # Get valid bet from bet type.
        if bet_type == 'inside':
            self.insideBet()
        else:
            pass
            # Give outside bet options.

        return self.chips
