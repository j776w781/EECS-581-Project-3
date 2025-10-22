import time
from table import Number, Table, Wheel

class Roulette:
    def __init__(self, chips):
        self.chips = chips
        self.table = Table()
        self.wheel = Wheel()

    def insideBet(self):
        # Input with error handling for roulette number.
        i = 0
        while i == 0:
            try:
                num = int(input("\nPick a number to bet on: "))
                if num < 0 or num > 36:
                    raise
                num = Number(num)
                i = 1
            except:
                i = 0

        # Input with error handling for bet amount.
        i = 0
        while i == 0:
            try:
                print("\nChip total:", self.chips)
                bet = int(input("How much will you bet?: "))
                if bet > self.chips or bet < 0:
                    print("\nInvalid bet amount. Try again.")
                    raise
                self.chips -= bet
                i = 1
            except:
                i = 0
        
        result = self.wheel.spin()
        print("Result is:", result)
        if result == num:
            print("\nBet won! Congratulations!")
            self.chips += 36 * bet
        else:
            print("\nBet lost...")

    def play(self):
        print("\nWelcome to Roulette.")
        print("\n1) Inside Bet\n2) Outside Bet")

        # Get valid bet type input.
        i = 0
        while i == 0:
            bet_type = input("\nPick a bet type: ")
            bet_type = bet_type.lower()
            valid_bet_types =  ['1', '2', 'inside', 'outside', 'i', 'o']
            if bet_type in valid_bet_types:
                # Collapse valid bet type options into single options.
                if bet_type == '1' or bet_type == 'inside' or bet_type == 'i':
                    bet_type = 'inside'
                else:
                    bet_type = 'outside'
                i = 1
            else:
                print("Invalid option. Choose again.")
        
        # Get valid bet from bet type.
        if bet_type == 'inside':
            self.insideBet()
        else:
            pass
            # Give outside bet options.

        return self.chips
