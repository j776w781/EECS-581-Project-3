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
        print(self.bestHand)

        # For now I just have the AI defaulting to checking.
        hand_strengths = {
            "High Card": 0.1,
            "Pair": 0.25,
            "Two Pair": 0.4,
            "Three of a Kind": 0.55,
            "Straight": 0.65,
            "Flush": 0.75,
            "Full House": 0.85,
            "Four of a Kind": 0.9,
            "Straight Flush": 0.95,
            "Royal Flush": 1.0,
        }

        strength = hand_strengths.get(self.handRank, 0.1)
        strength += random.uniform(-0.1, 0.1)

        if self.game.activeBet:
            if strength < 0.2:
                self.game.fold(id) if random.random() < 0.8 else self.game.call(id)
            elif strength < 0.5:
                self.game.call(id)
            elif strength < 0.8:
                self.game.call(id) if random.random() < 0.7 else self.game._raise(id)
            else:
                self.game._raise(id) if random.random() < 0.6 else self.game.call(id)
        else:
            if strength > 0.75 and random.random() < 0.5:
                self.game.bet(id)
            elif strength > 0.5 and random.random() < 0.3:
                self.game.bet(id)
            else:
                self.game.check(id)