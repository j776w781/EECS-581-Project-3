from .objects.deck import Deck
from .objects.hand import Hand

class Poker:
    def __init__(self):
        self.deck = Deck() # We need the deck of course.
        self.playerHand = Hand() # We need the player hand of course.
        self.board = [] # Keeps track of cards in center.
        self.oppNo = 0 # We need to know how many opponents we have in order to make that many later.
        self.fold = False # This will likely be valuable in interrupting gameflow.

    # Method to deal initial two cards to a given player.
    def deal(self, hand):
        hand.add(self.deck.draw())
        hand.add(self.deck.draw())

    # Game flow occurs in three stages: flop, turn, and river.
    # We are going to abstract each stage into methods.
    # So while the methods are quite elementary, (and two are exactly the same)
        # The abstraction will make later coding easier (at least for me it will).
    def flop(self):
        self.board.append(self.deck.draw())
        self.board.append(self.deck.draw())
        self.board.append(self.deck.draw())

    def turn(self):
        self.board.append(self.deck.draw())

    def river(self):
        self.board.append(self.deck.draw())

    def analyzeHand(self, hand):
        hand_type, best_hand = self.playerHand.getBestHand(self.board)
        print(hand_type)
        print(best_hand)