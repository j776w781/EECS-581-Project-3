from PyQt6.QtWidgets import QWidget, QGraphicsScene, QGraphicsObject
from PyQt6.QtCore import QPropertyAnimation, QPointF, QEasingCurve, QRectF, pyqtProperty
from PyQt6.QtGui import QPixmap, QPainter
from .ui.blackjack_ui import Ui_BlackJackScreen
from .objects.deck import Deck
import time
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARDS_DIR = os.path.join(BASE_DIR, "../assets/cards")

class AnimatedCard(QGraphicsObject):
	def __init__(self, pixmap):
		super().__init__()
		self._pixmap = pixmap
		self._pos = QPointF(0, 0)

	def boundingRect(self):
		return QRectF(0, 0, self._pixmap.width(), self._pixmap.height())

	def paint(self, painter, option, widget=None):
		painter.drawPixmap(0, 0, self._pixmap)

	def getPos(self):
		return super().pos()
	
	def setPos(self, pos):
		super().setPos(pos)

	pos = pyqtProperty(QPointF, fget=getPos, fset=setPos)

class BlackJackScreen(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.ui = Ui_BlackJackScreen()
		self.ui.setupUi(self)

		self.scene = QGraphicsScene()
		self.ui.cardGraphicsView.setScene(self.scene)

		self.deck_pos = QPointF(0, 240)
		self.player_pos = QPointF(200, 470)
		self.dealer_pos = QPointF(200, 90)

		self.game = BlackJack(1000)
		self.ui.dealButton.clicked.connect(self.deal)

	def deal(self):
		# Deal player hand first.
		print("Dealing cards...")
		self.game.deal(self.game.playerHand)
		for i, card in enumerate(self.game.playerHand):
			card_sprite = self.createCard(card)
			end = self.player_pos + QPointF(i*80, 0)
			self.animateCard(self.deck_pos, end, card_sprite)

		# Deal dealer hand next.
		self.game.deal(self.game.dealerHand)
		for i, card in enumerate(self.game.dealerHand):
			if i == 0:
				card_sprite = self.createCard(card, True)
			else:
				card_sprite = self.createCard(card)
			end = self.dealer_pos + QPointF(i*80, 0)
			self.animateCard(self.deck_pos, end, card_sprite)
		print(self.game.dealerHand)
		print(self.game.playerHand)
		self.ui.dealButton.setEnabled(False)	

	def createCard(self, card, hidden=False):
		print("Creating cards...")
		# The line below is what we'll use when the card sprites are finished.
		# path = os.path.join(CARDS_DIR, f"{card.rank}_of_{card.suit}.png")
		# For now I'm using a placeholder card.
		if hidden:
			path = os.path.join(CARDS_DIR, "card_back.jpg")
		else:
			path = os.path.join(CARDS_DIR, "ace_of_spade.png")
		print(path)
		pixmap = QPixmap(path).scaled(100, 145)
		return pixmap

	def animateCard(self, start, end, pixmap):
		print("Animating cards...")
		card_sprite = AnimatedCard(pixmap)
		self.scene.addItem(card_sprite)

		anim = QPropertyAnimation(card_sprite, b'pos')
		anim.setDuration(700)
		anim.setStartValue(start)
		anim.setEndValue(end)
		anim.setEasingCurve(QEasingCurve.Type.OutCubic)
		anim.start()

		if not hasattr(self, '_anims'):
			self._anims = []
		self._anims.append(anim)

class BlackJack:
	def __init__(self, chips):
		self.deck = Deck()
		self.playerHand = []
		self.dealerHand = []
		self.playerScore = 0
		self.dealerScore = 0
		self.chips = chips
		self.bust = False

	# A charming method. It just gives the player and the dealer their hands.
	def deal(self, hand):
		hand.append(self.deck.draw())
		hand.append(self.deck.draw())

	# A method to display hand in terminal. Should be overwritten with GUI in future.
	def printHand(self, hand, hide=False):
		for card in hand:
			if hide and hand.index(card) == 0:
				print('*')
			else:
				print(card)
		return

	# Returns a list of numeric total and Aces. We consider the Ace's effect on total later.
	def getTotal(self, hand):
		total = [0]
		for card in hand:
			if card.rank == 'ace':
				if total[0] + 11 > 21:
					total[0] = total[0] + 1
				else:
					total.append('ace')
			elif card.rank == 'jack' or card.rank == 'queen' or card.rank == 'king':
				total[0] = total[0] + 10
			else:
				total[0] = total[0] + card.rank
		return total	

	# Iterates through total list and checks if old Aces no longer work as '11' values. Adds them to total as '1' and removes Ace from total list.
	def verifyTotal(self, total):
		for i in range(1, len(total)):
			if total[0] + 11 <= 21:
				continue
			else:
				total[0] += 1
				total[i] = '' # Set Ace to dead value
		while '' in total: # This lets us remove dead values safely from list.
			index = total.index('')
			total.pop(index)

	# Checks total and if there are remaining live Aces. Adds those live Aces if possible. Otherwise add the smallest value to avoid busting.
		# It is still possible to lose with BestSum, this just tries to avoid it as much as possible.
	def getBestSum(self, total):
		final = total[0]
		for i in range(1, len(total)):
			if final + 11 <= 21:
				final += 11
			else:
				final += 1
		return final
				

	def playerTurn(self):
		while True:
			# Display the hands for user
			print("\nDealer's hand:")
			self.printHand(self.dealerHand, True)
			print("\nPlayer's hand:")
			self.printHand(self.playerHand)
	
			# Ask for choice, hit or stand?
			choice = input('\nHit or Stand?: ')
			choices = ['hit', 'h', 'stand', 's']
			while choice.lower() not in choices: # Input sanitization 
				print("Invalid choice. Please 'hit' or 'stand'.")
				choice = input('Hit or Stand: ')

			# With valid input, we will go over each scenario.
			if choice.lower() == 'hit' or choice.lower() == 'h':
				# HIT SCENARIO
				self.playerHand.append(self.deck.draw()) # Give player another card.
				total = self.getTotal(self.playerHand) # Keep track of total. Interestingly, total is a list.

				# A very interesting event is drawing an Ace, because it puts the hand in a bit of quantum state.
					# When we check for bust, we have to be kind enough to set aces to a value of 1
					# When we check for highest total, we have to be kind enough to set as many aces to their highest value.

				if len(total) > 1:
					self.verifyTotal(total) # This configures the total so the Ace doesn't count toward bust.
				if total[0] > 21: # We check the total against 21 and if its over we end player's turn
					total = self.getBestSum(total) # Set total as a single numeric value for player.
					return total # Return final score for player
			else:
				# STAND SCENARIO
				total = self.getTotal(self.playerHand) # Get total from hand.
				if len(total) > 1: # In the event we have an Ace...
					self.verifyTotal(total) # Verify live or dead Aces.
				total = self.getBestSum(total) # Add any live Aces to total.
				return total # Return final score for player
			
	def dealerTurn(self):
		while True:
			print("\nDealer\'s hand:")
			self.printHand(self.dealerHand)
			print('\nPlayer\'s hand:')
			self.printHand(self.playerHand)

			time.sleep(2) # For now, this gives some pause between dealer moves.			

			# Dealer doesn't choose like the player does. It hits or stands until its score is same, better or busts.
			total = self.getTotal(self.dealerHand)
			if len(total) > 1:
				self.verifyTotal(total)
			if self.getBestSum(total) < self.playerScore:
				# HIT SCENARIO
				print('\nDealer hits.')
				self.dealerHand.append(self.deck.draw()) # Give dealer another card.
				total = self.getTotal(self.dealerHand)
				if len(total) > 1:
					self.verifyTotal(total)
				if total[0] > 21:
					total = self.getBestSum(total)
					return total
			else:
				# STAND SCENARIO
				print('\nDealer stands.')
				total = self.getBestSum(total)
				return total

	def play(self):
		# In a single run of BlackJack we start by dealing to each player.
		self.deal(self.dealerHand)
		self.deal(self.playerHand)

		# Get bet for game. Use error handling.
		print('\nChip total:', self.chips)
		i = 0
		while i == 0:
			try:
				bet = int(input('How much would you like to bet?: '))
				if bet < 1 or bet > self.chips:
					print('\nInvalid bet. Try again.')	
					raise
				i = 1
			except:
				i = 0
		
		# Remove bet from chips.
		self.chips -= bet

		# Now we start the gameplay loop for player.
		self.playerScore = self.playerTurn()
		
		# Record result of player's turn.
		print('\nDealer\'s hand:')
		self.printHand(self.dealerHand, True)
		print('\nPlayer\'s hand:')
		self.printHand(self.playerHand)

		if self.playerScore > 21:
			print('\nTotal:', self.playerScore)
			print("BUST!!! Game Over!")
			self.bust = True
		else:
			print('\nTotal:', self.playerScore)
			print('\nDealer\'s Turn...')
	
		if not self.bust:
			time.sleep(5) # Give some pause between turns.
			# Now we start the gameplay loop for dealer.
			self.dealerScore = self.dealerTurn()

			# Record result after dealer's turn.
			print('\nDealer\'s hand:')
			self.printHand(self.dealerHand)
			print('\nPlayer\'s hand:')
			self.printHand(self.playerHand)

			if self.dealerScore > 21: # If dealer busts, the player wins.
				print('\nPlayer Total:', self.playerScore)
				print('Dealer Total:', self.dealerScore)
				print("\nDealer busts!!! You Win!")
				self.chips += 2 * bet
			elif self.dealerScore == self.playerScore: # If dealer and player tie score. Check for special scenarios.
				if self.dealerScore == 21: # If the equivalent score is 21. Check for BlackJack
					# BlackJack is defined as a 2-card hand that equals 21.
					# If one of the players have a smaller, 2-card hand that equals 21.
					if len(self.dealerHand) < len(self.playerHand) and len(self.dealerHand) == 2:
						print('\nPlayer Total:', self.playerScore)
						print('Dealer Total:', self.dealerScore)
						print('\nDealer wins.')
					elif len(self.dealerHand) > len(self.playerHand) and len(self.playerHand) == 2:
						print('\nPlayer Total:', self.playerScore)
						print('Dealer Total:', self.dealerScore)
						print("\nYou Win!")
						self.chips += 2 * bet
					else: # If the above conditions don't apply, its a regular tie.
						print('\nPlayer Total:', self.playerScore)
						print('Dealer Total:', self.dealerScore)
						print("\nA tie. No chips lost.")
						self.chips += bet
				else: # If the score isn't 21, its a regular tie.
					print('\nPlayer Total:', self.playerScore)
					print('Dealer Total:', self.dealerScore)
					print("\nA tie. No chips lost.")
					self.chips += bet
			else:
				print('\nPlayer Total:', self.playerScore)
				print('Dealer Total:', self.dealerScore)
				print('\nDealer wins.')
			
		return self.chips
