'''
Name: deck.py

Authors: Joshua Welicky, Gavin Billinger, Mark Kitchin, Bisshoy Bhattacharjee, Max Biundo

Description: Implementation for Playing card and card deck.
'''

import random

#Implementation for playing card, whic just has a suit and rank.
class Card:
	def __init__(self, suit, rank):
		self.suit = suit
		self.rank = rank

	def __str__(self):
		return self.suit + ': ' + str(self.rank)
	
	def __repr__(self):
		return str(self)
	
	def __add__(self, other):
		if isinstance(other, int):
			return self.rank + other
		return self.rank + other.rank


'''
Implementation for card deck, which is essentially just a list of Cards.

Drawing removes a random card from the deck.
Shuffling restores the initial state of the deck.
'''
class Deck:
	def __init__(self):
		self.deck = []
		suits = ['spade', 'club', 'diamond', 'heart']
		ranks = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'jack', 'queen', 'king', 'ace']
		for suit in suits:
			for rank in ranks:
				self.deck.append(Card(suit, rank))

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
		suits = ['spade', 'club', 'diamond', 'heart']
		ranks = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'jack', 'queen', 'king', 'ace']	
		for suit in suits:
			for rank in ranks:
				self.deck.append(Card(suit, rank))
