from deck import Deck
from itertools import combinations
from collections import Counter

class Hand:
    def __init__(self):
        self.hand = []

    def add(self, card):
        self.hand.append(card)

    def __str__(self):
        output = ''
        for card in self.hand:
            output += str(card) + ' '
        return output

    # Helper function for getBestHand, if card order jumps, consecutivity is False.
    def isConsecutive(self, ranks):
        for i in range(1, len(ranks)):
            if ranks[i] != ranks[i-1] + 1:
                return False
        return True

    def getBestHand(self, board):
        pool = self.hand + board
        for card in pool:
            if card.rank == 'jack':
                card.rank = 11
            elif card.rank == 'queen':
                card.rank = 12
            elif card.rank == 'king':
                card.rank = 13
            elif card.rank == 'ace':
                card.rank = 14
        # This lovely little function gets every combination of 5 cards from the possible 7 that are given.
        combos = combinations(pool, 5)
        bestRank = 0 # This will keep track of the hand rank (not card rank)
        bestCombo = None # This will specifically hold that best card combo.

        # We will look through every five card hand and get properties to determine if its the best hand.
        for combo in combos:
            # Determine if hand has flush.
            suits = [card.suit for card in combo]
            isFlush = len(set(suits)) == 1 # If all suits are the same, duplicates should be removed and 1 suit should remain.
            
            # Get sorted list of card ranks
            ranks = sorted([card.rank for card in combo], reverse=True)
            
            # While we're at it, count occurrence of ranks in full list.
            rankCounts = Counter(ranks)
            counts = sorted(rankCounts.values(), reverse=True) # Puts those counts in a sorted list.

            # Once we're done counting, we can now eliminate duplicates to find straights
            sortedRanks = sorted(set(ranks)) # Get sorted list of unique ranks.
            isStraight = False # Initialize straight being found to false.
            # We might not even have to bother looking if there aren't enough unique values for a straight.
            if len(sortedRanks) == 5:
                if self.isConsecutive(sortedRanks): # We use separate function to check this.
                    isStraight = True
                elif sortedRanks == [2, 3, 4, 5, 14]: # Specific check for Ace-Low straight.
                    isStraight = True
                    ranks = [5, 4, 3, 2, 1] # Note Ace as low (1) value.

            # Now, we should have the information we need to determine hand rank for given 5-card combo.
            handRank = ''

            if isStraight and isFlush and max(ranks) == 14:
                handRank = 'Royal Flush'
            elif isStraight and isFlush:
                handRank = 'Straight Flush'
            elif counts == [4,1]:
                handRank = 'Four of a Kind'
            elif counts == [3, 2]:
                handRank = 'Full House'
            elif isFlush:
                handRank = 'Flush'
            elif isStraight:
                handRank = 'Straight'
            elif counts == [3,1,1]:
                handRank = 'Three of a Kind'
            elif counts == [2, 2, 1]:
                handRank = 'Two Pair'
            elif counts == [2, 1, 1, 1]:
                handRank = 'Pair'
            else:
                handRank = 'High Card'

            # Bank of poker hands.
            handRanks = [
                "High Card", "Pair", "Two Pair", "Three of a Kind", "Straight",
                 "Flush", "Full House", "Four of a Kind", "Straight Flush", "Royal Flush"
            ]

            # Compare poker hands by higher index.
            if handRanks.index(handRank) > bestRank:
                bestRank = handRanks.index(handRank)
                bestCombo = combo
            elif handRank == bestRank: # In tie breaker case, we go by highest value card.
                if sorted([card.rank for card in combo], reverse=True) > sorted([card.rank for card in bestCombo], reverse=True):
                    bestCombo = combo

        # Once we've checked every 5-card combination for best hand, return them!
        return handRanks[bestRank], bestCombo

def main():
    hand_type = ''
    while hand_type != "Pair":
        deck = Deck()
        hand = Hand()
        hand.add(deck.draw())
        hand.add(deck.draw())
        board = []
        board.append(deck.draw())
        board.append(deck.draw())
        board.append(deck.draw())
        board.append(deck.draw())
        board.append(deck.draw())
        print('Board: ')
        print(board)
        print('\nHand: ')
        print(hand, '\n')
        hand_type, best_hand = hand.getBestHand(board)
        print(hand_type)
        print(best_hand)

main()
