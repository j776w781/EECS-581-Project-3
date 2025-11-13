from .hand import Hand
import random

class Opponent:
    def __init__(self, name, game):
        self.name = name
        self.game = game # The opponent needs the game instance to modify its state.
        self.oppHand = Hand()
        self.stake = 0
        self.chipTotal = 0

    def decision(self):
        if self.game.activeBet:
            num = random.randint(0, 2)
            if num == 0:
                self.game.call()
            elif num == 1:
                self.game._raise()
            elif num == 2:
                self.game.fold()
        else:
            num = random.randint(0, 2)
            if num == 0:
                self.game.check()
            elif num == 1:
                self.game.bet()
            elif num == 2:
                self.game.fold()