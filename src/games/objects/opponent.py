from .hand import Hand

class Opponent:
    def __init__(self, name):
        self.name = name
        self.oppHand = Hand()
        self.stake = 0
        self.chipTotal = 0

    def decision(self):
        pass