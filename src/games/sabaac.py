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
        self.game = Sabacc()


    def leave(self):
        self.switch_to_menu.emit()
























class Sabacc:
    def __init__(self):
        return