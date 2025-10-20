# card_button.py
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QMouseEvent, QPainter, QColor, QPen, QBrush


class CardButton(QWidget):
    clicked = pyqtSignal()  # custom signal

    def __init__(self, title: str = "Card Title", description: str = "", parent=None):
        super().__init__(parent)

        # --- Layout and labels ---
        self.title = QLabel(title)
        self.title.setStyleSheet("font-weight: bold; font-size: 16px;")

        self.description = QLabel(description)
        self.description.setWordWrap(True)
        self.description.setStyleSheet("color: gray; font-size: 12px;")

        layout = QVBoxLayout(self)
        layout.addWidget(self.title)
        layout.addWidget(self.description)
        layout.setContentsMargins(15, 15, 15, 15)

        # --- Visual styling ---
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        # self.setStyleSheet("background-color: white; border-radius: 10px;")
        self._hovered = False

    '''
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

		# rotate around center
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self.angle)
        painter.translate(-self.width() / 2, -self.height() / 2)

		# draw card rectangle
        painter.setBrush(QBrush(QColor("white")))
        painter.setPen(QPen(QColor("black"), 2))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 12, 12)
    '''
    # --- Painting for hover effect ---
    def paintEvent(self, event):
        painter = QPainter(self)
        color = QColor("#f0f0f0") if self._hovered else QColor("white")
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor("#d0d0d0"), 1))
        painter.drawRoundedRect(self.rect(), 10, 10)

    # --- Mouse handling ---
    def enterEvent(self, event):
        self._hovered = True
        self.update()

    def leaveEvent(self, event):
        self._hovered = False
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    # --- Convenience methods ---
    def setTitle(self, text):
        self.title.setText(text)

    def setDescription(self, text):
        self.description.setText(text)

