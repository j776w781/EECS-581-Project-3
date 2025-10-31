import random

class Number:
    def __init__(self, num):
        self.value = num
        self.color = 'black'
        self.row = 0
        self.col = 0
        self.third = 0
        self.half = 0
        self.isEven = False
        self.categorizeNumber(self.value)

    def categorizeNumber(self, num):
        # First we give a number its color.
        reds = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        if num in reds:
            self.color = 'red'
        elif num == 0:
            self.color = 'green'

        # Next we give a number its column value (1-3)
        if num % 3 == 1:
            self.col = 1
        elif num % 3 == 2:
            self.col = 2
        elif num % 3 == 0 and num != 0:
            self.col = 3

        # Row calculations! It's clunky, I know.
        if num in range(1, 4):
            self.row = 1
        elif num in range(4,7):
            self.row = 2
        elif num in range(7,10):
            self.row = 3
        elif num in range(10,13):
            self.row = 4
        elif num in range(13,16):
            self.row = 5
        elif num in range(16,19):
            self.row = 6
        elif num in range(19,22):
            self.row = 7
        elif num in range(22,25):
            self.row = 8
        elif num in range(25,28):
            self.row = 9
        elif num in range(28,31):
            self.row = 10
        elif num in range(31,34):
            self.row = 11
        elif num in range(34,37):
            self.row = 12


        # Next we give a number which third in a range of 36 its in.
        if num in range(1, 13):
            self.third = 1
        elif num in range(13, 25):
            self.third = 2
        elif num in range(25, 37):
            self.third = 3

        # Next we give a number which half in range of 36 its in.
        if num in range(1, 19):
            self.half = 1
        elif num in range(19, 37):
            self.half = 2
            
        # Finally, we pick if the number is even or odd.
        if num % 2 == 0:
            self.isEven = True

    def __str__(self):
        return str(self.color) + ': ' + str(self.value)
    
    def __eq__(self, other):
        return self.value == other.value
    
class Wheel:
    def __init__(self):
        self.order = []
        order = [28, 12, 35, 3, 26, 0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7]
        for i in range(len(order)):
            self.order.append(Number(order[i]))

    def __str__(self):
        output = ''
        for i in range(len(self.order)):
            output += str(self.order[i]) + '\n'
        return output[:len(output)-1]
    
    def spin(self):
        # Grab random index in range of wheel's order list.
        index = random.randint(0, 36)
        return index

        # Why not just pick a random number from the wheel?
            # 1) To preserve statistics of standard Roulette
            # 2) This logic will likely help when making GUI later.