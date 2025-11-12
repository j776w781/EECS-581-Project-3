"""
Sabaac Deck and Card Classes
Authors: Joshua Welicky, Gavin Billinger, Mark Kitchin, Bisshoy Bhattacharjee, Max Biundo
Description: Implementation for Sabaac playing card and card deck.
"""
import random

class Sabaac_Card:
    def __init__(self, sign, rank, suit):
        self.sign = sign
        self.rank = rank
        self.suit = suit
        if sign == 'neg':
            self.rank = -rank

    def __str__(self):
        return self.sign + ": " + self.suit + ": " + str(self.rank)
	
    def __repr__(self):
        return str(self)
	
    def __add__(self, other):
        if isinstance(other, int):
            return self.rank + other
        return self.rank + other.rank


class Sabaac_Deck:
    def __init__(self):
        self.deck = []
        signs = ['pos', 'neg']
        suits = ['square', 'circle', 'triangle']
        ranks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        for sign in signs:
            for suit in suits:
                for rank in ranks:
                    self.deck.append(Sabaac_Card(sign, rank, suit))
        self.deck.append(Sabaac_Card('zero', 0, 'revan'))
        self.deck.append(Sabaac_Card('zero', 0, 'anakin'))

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
    
    def draw(self):
        card = random.choice(self.deck)
        index = self.deck.index(card)
        self.deck.pop(index)
        return card
    
    def shuffle(self):
        self.deck = []
        signs = ['pos', 'neg']
        suits = ['square', 'circle', 'triangle']
        ranks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        for sign in signs:
            for suit in suits:
                for rank in ranks:
                    self.deck.append(Sabaac_Card(sign, rank, suit))
        self.deck.append(Sabaac_Card('zero', 0, 'revan'))
        self.deck.append(Sabaac_Card('zero', 0, 'anakin'))