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

    def calc_hand_value(self):
        total_value = 0
        for card in self.hand:
            total_value += card.rank
        return total_value











#============================Object for ROBOPPONENTS===================================#

class SabaccAI:
    """Represents an AI player in Sabacc.
    Input: name, position for GUI, difficulty level."""
    def __init__(self, name, position, difficulty):
        self.name = name
        self.position = position
        self.difficulty = difficulty
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
        if self.difficulty == "medium":
            if checkHand == 0:
                # AI decides to stand with a perfect hand
                #game.stand(self)
                return ["stand"]
            if optimalSwap != None:
                if num_round == 1 or abs(optimalSwap[1]) < 2:
                    #game.swap(self, optimalSwap)
                    card_idx = self.hand.index(optimalSwap[0])
                    return ["swap", card_idx]
            if abs(checkHand) < 3:
                # AI decides to try and win with the current hand
                #game.stand(self)
                return ["stand"]
            if abs(checkHand) > 23 and num_round == 3:
                #game.junk(self)
                return ["junk"]
            #game.draw(self)
            return ["draw"]
        

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
    '''
    def should_bet(self, current_bet):
        if self.chips == 0:
            return 0
        
        hand_val = abs(self.calc_hand_value())

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

        #Add random noise
        strength += random.uniform(-0.1, 0.1)

        '''
        LLM Contributions Begin Here
        '''
        strength = max(0.0, min(1.0, strength))   # clamp

        #Convert strength into action probabilities
        p_raise = 0.2 + 0.8 * strength
        p_call  = 1 - (p_raise)

        #Choose action
        r = random.random()

        if r < p_call:
            if current_bet == 0:
                return min(50, self.chips)
            #Call the current bet
            return min(current_bet, self.chips)
        else:
            if self.chips < current_bet:
                return self.chips
            #Raise amount based on strength
            raise_fraction = 0.5 * strength
            raw_raise = int((self.chips * raise_fraction) // 50) * 50

            if current_bet == 0:
                return max(50, raw_raise)
            
            raise_amount = min(self.chips, current_bet + raw_raise)

            return raise_amount