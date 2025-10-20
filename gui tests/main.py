# main.py
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import QSize
from PyQt6 import uic
from card_button import CardButton  # import your custom widget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 👇 Load the .ui file directly
        uic.loadUi("card_test.ui", self)

        # Access your promoted widget by its object name (from Designer)
        self.card1.setTitle("Playing card.")
        self.card1.setDescription("Ace of Spaces")
        self.card2.setTitle("Playing card.")
        self.card2.setDescription("Ace of Spaces")
        self.card3.setTitle("Playing card.")
        self.card3.setDescription("Ace of Spaces")
        self.card1.clicked.connect(self.on_card_clicked)


        self.exitButton.clicked.connect(self.close)

    def on_card_clicked(self):
        QMessageBox.information(self, "Card Clicked", "You clicked the card!")

# Run the app
app = QApplication([])
window = MainWindow()
window.show()
app.exec()

