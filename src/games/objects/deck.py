import random

class Card:
	def __init__(self, suit, rank):
		self.suit = suit
		self.rank = rank

	def __str__(self):
		return self.suit + ': ' + str(self.rank)
	
	def __repr__(self):
		return str(self)
	
	def __add__(self, other):
		return self.rank + other.rank	


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
