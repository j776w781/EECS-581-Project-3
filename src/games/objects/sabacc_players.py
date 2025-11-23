'''
File: sabaac_players.py

Authors: Joshua Welicky, Gavin Billinger, Mark Kitchin, Max Biundo, Bisshoy Bhattacharjee

Description:
Store the SabaccPlayer class, which represents a human player, and a SabaccAI class.
Each one has a name, a hand (array of SabaccCards), a hand_widgets (Stores GUI elements for each
card for convenient access), their chips, their current stake, whether they're in the current game, and whether they're 
defeated.

Inputs: None

Outputs: None
'''

import random

#======================Object for the HUMAN======================================#

class SabaccPlayer:
    """Represents a player in Sabacc.
    Input: name, position for GUI."""
    def __init__(self, name, chips):
        self.name = name
        self.hand = []
        self.hand_widgets = [None, None, None, None, None]
        self.chips = chips
        self.stake = 0
        self.out_of_game = False
        self.defeated = False

    '''
    Returns the current value of the hand.
    '''
    def calc_hand_value(self):
        total_value = 0
        for card in self.hand:
            total_value += card.rank
        return total_value











#============================Object for ROBOPPONENTS===================================#

class SabaccAI:
    """Represents an AI player in Sabacc.
    Input: name, position for GUI, difficulty level."""
    def __init__(self, name, position):
        self.name = name
        self.position = position
        self.hand = []
        self.hand_widgets = [None, None, None, None, None]
        self.chips = random.randint(1, 25) * 50
        self.stake = 0
        self.out_of_game = False
        self.defeated = False

    """Calculates the total value of the AI's hand."""
    def calc_hand_value(self):
        total_value = 0
        for card in self.hand:
            total_value += card.rank
        return total_value
    
    """Checks possible swap options with the discard pile.
    Inputs: AI's hand, value of the top discard card.
    Outputs: The best swap option (card to swap, new hand value) or None if no beneficial swap exists."""
    def checkSwapOptions(self, hand, discard_value):
        possible_swaps = []
        for card in hand:
            new_hand_value = sum(c.rank for c in hand if c != card) + discard_value
            possible_swaps.append((card, new_hand_value))
        track_best = (None, 1000)
        for i in range(len(possible_swaps)):
            if abs(possible_swaps[i][1]) < abs(track_best[1]):
                track_best = possible_swaps[i]
        if track_best[1] < abs(self.calc_hand_value()):
            return track_best
        else:
            return None

    """Determines and executes the AI's move based on its difficulty level and hand value.
    Inputs: current round number."""
    def make_move(self, num_round, discard_pile):
        checkHand = self.calc_hand_value()
        checkDiscardValue = discard_pile[len(discard_pile)-1].rank if len(discard_pile) > 0 else None
        optimalSwap = self.checkSwapOptions(self.hand, checkDiscardValue)
        if True:
            if checkHand == 0:
                # AI decides to stand with a perfect hand
                return ["stand"]
            if optimalSwap != None:
                if num_round == 1 or abs(optimalSwap[1]) < 2:
                    #AI decides to swap.
                    card_idx = self.hand.index(optimalSwap[0])
                    return ["swap", card_idx]
            if abs(checkHand) < 3:
                # AI decides to try and win with the current hand
                return ["stand"]
            if abs(checkHand) > 23 and num_round == 3:
                return ["junk"]
            #If nothing else, they'll just draw.
            return ["draw"]
        

    '''
    This function lets the opponent decide what card they should discard, if any.
    It returns the index(in their hand) or the card they should discard.
    '''
    def should_discard(self):
        #Fetch current total.
        cur_sum = self.calc_hand_value()

        #Calculate the best sum which can be achieved from removing one card.
        best_sum = 100000
        card_to_drop = -1
        for card in self.hand:
            if abs(cur_sum - card.rank) < best_sum:
                card_to_drop = self.hand.index(card)
                best_sum = abs(cur_sum - card.rank)

        #Only recommend a discard if the best possible removal is actually beneficial.
        if abs(best_sum) <= abs(cur_sum):
            return card_to_drop
        else:
            return -1
    


    '''
    I must cite ChatGPT for giving me a coherent technique for deciding when to bet in Sabacc,
    as well as filling out the rest of this function.

    This function allows an opponent to decide how much to bet considering a current bet. It returns the
    amount to bet.
    '''
    def should_bet(self, current_bet):
        #Firstly, if they have no chips, they shouldn't bet.
        if self.chips == 0:
            return 0
        
        #Gain the value of their hand.
        hand_val = abs(self.calc_hand_value())

        #Assign strength based on the hand quality.
        if hand_val == 0:
            strength = 1.0
        elif hand_val <= 2:
            strength = 0.8
        elif hand_val <= 6:
            strength = 0.6
        elif hand_val <= 10:
            strength = 0.5
        else:
            strength = 0.1

        #Add random noise to strength, for unpredictability
        strength += random.uniform(-0.2, 0.2)

        '''
        LLM Contributions Begin Here
        '''
        #Clamp the strength at 1.
        strength = max(0.0, min(1.0, strength))

        #Convert strength into action probabilities
        p_raise = 0.8 * strength
        p_match  = 1 - (p_raise)

        #Choose action
        r = random.random()

        #If they decide to match or don't have enough chips to match/raise.
        if r < p_match or self.chips <= current_bet:
            #Use when the opponent is the first better.
            if current_bet == 0:
                #Bet either 50 or less.
                return min(50, self.chips)
            
            #Match the current bet, or self.chips if they don't have enough.
            return min(current_bet, self.chips)
        #Only runs if they can and want to raise.
        else:
            #Raise amount based on strength
            raise_fraction = 0.25 * strength
            #Make sure it's a multiple of fifty.
            raw_raise = int((self.chips * raise_fraction) // 50) * 50

            
            if current_bet == 0:
                return max(50, raw_raise)
            
            
            #raise_amount = min(self.chips, current_bet + raw_raise)

            return current_bet + raw_raise