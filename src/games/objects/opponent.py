from .hand import Hand
import random

#=========================================================#
#=================== AI OPPONENT CLASS ===================#
#=========================================================#

# To be honest, I'm not sure how extensible this is to Sabaac, but this is what I needed for Poker.

class Opponent:
    def __init__(self, name, game, id):
        self.name = name
        self.game = game # The opponent needs the game instance to modify its state.
        self.oppHand = Hand()
        self.bestHand = []
        self.handRank = 0
        self.stake = 0
        self.chipTotal = 0
        self.id = id

    def __str__(self):
        return self.name

    def decision(self, id):
        self.handRank, self.bestHand = self.oppHand.getBestHand(self.game.board)
        print(f"{self.name}'s Best Hand:")
        print(self.handRank)

        # For now I just have the AI defaulting to checking.
        self.game.check(id)
        '''
        if self.game.activeBet:
            num = random.randint(0, 2)
            if num == 0:
                self.game.call(id)
            elif num == 1:
                self.game._raise(id)
            elif num == 2:
                self.game.fold(id)
        else:
            num = random.randint(0, 2)
            if num == 0:
                self.game.check(id)
            elif num == 1:
                self.game.bet(id)
            elif num == 2:
                self.game.fold(id)
        '''