from blackjack import BlackJack
from roulette import Roulette

def main():
	chips = 1000
	
	game = input('b or r?: ')

	if game == 'b':
		play = 'y'
		while play == 'y':
			blackjack = BlackJack(chips)
			chips = blackjack.play()
			if chips > 0:
				play = input('Play again?: ')
			else:
				print("You have run out of chips.")
				play = 'n'
	elif game == 'r':
		play = 'y'
		while play == 'y':
			roulette = Roulette(chips)
			chips = roulette.play()
			if chips > 0:
				play = input('Play again?: ')
			else:
				print("You have run out of chips.")
				play = 'n'

main()