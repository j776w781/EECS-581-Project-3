"""
Sabaac Deck and Card Classes
Authors: Joshua Welicky, Gavin Billinger, Mark Kitchin, Bisshoy Bhattacharjee, Max Biundo
Description: Implementation for Sabaac playing card and card deck. Methods are very similar to deck.py,
with slight modifications for Sabacc.
"""
import random
from .deck import AnimatedCard

class Sabacc_Card:
    def __init__(self, sign, rank, suit):
        self.sign = sign
        self.rank = rank
        self.suit = suit
        if sign == 'neg':
            self.rank = -1 * rank

    def __str__(self):
        return self.sign + ": " + self.suit + ": " + str(self.rank)
	
    def __repr__(self):
        return str(self)
    
    def getName(self):
        return f"{self.sign}_{abs(self.rank)}_of_{self.suit}.png"
	
    def __add__(self, other):
        if isinstance(other, int):
            return self.rank + other
        return self.rank + other.rank


class Sabacc_Deck:
    def __init__(self):
        self.deck = []
        signs = ['pos', 'neg']
        suits = ['square', 'circle', 'triangle']
        ranks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        for sign in signs:
            for suit in suits:
                for rank in ranks:
                    self.deck.append(Sabacc_Card(sign, rank, suit))
        self.deck.append(Sabacc_Card('zero', 0, 'revan'))
        self.deck.append(Sabacc_Card('zero', 0, 'anakin'))

    def __getitem__(self, i):
        if isinstance(i, int):
            return self.deck[i]
        else:
            raise
    
    def __str__(self):
        output = ''
        for i in range(len(self.deck)):
            output = output + str(self.deck[i]) + '\n'
        return output
            
    
    def draw_card(self):
        if len(self.deck) == 0:
            return None
        card = random.choice(self.deck)
        index = self.deck.index(card)
        self.deck.pop(index)
        return card
    
    def shuffle(self, deck= []):
        self.deck = deck
        self.deck = random.shuffle(self.deck)
        return self.deck