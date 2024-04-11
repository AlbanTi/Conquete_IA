from enum import Enum
from collections import namedtuple
import numpy as np
import pygame
import random

from .player import Player, Direction

pygame.init()
font = pygame.font.Font('./game/arial.ttf', 25)


Point = namedtuple('Point', 'x, y')

WHITE = (255, 255, 255)
GRID = (200, 200, 200)
RED = (200,0,0)
GREEN = (0,200,100)
BLUE = (0,100,200)
BACKGROUND = (40, 40, 40)

PLAYER_SIZE = 13

FIELD_BLUE = (0,100,200)
FIELD_RED = (200,100,0)

NEUTRAL_COLOR = (100,100,100)
NEUTRAL_COLOR_CENTER = (128,128,128)

BLOCK_SIZE = 26
SPEED = 1550

LIST_COLOR_PLAYER = [BLUE,RED,GREEN]

SPACE_SCORE = -200
SIZE_SCORE_TXT = 350

MOVE_REMPLISSAGE = [
	(-1,0),
	(1,0),
	(0,-1),
	(0,1)
]

class Player_UI:
	def __init__(self,color,position):
		self.color = color
		self.color_center = (color[0] + 28, color[1] + 28, color[2] + 28)
		self.position  = position

class Conquete:
	def __init__(self, w=1274,h=754, nbr_player = 2):
		self.w = w
		self.h = h
		self.nbr_player = nbr_player

		self.height = 20
		self.width = 35
		self.recor = 0
		self.last_score = 0
		self.start_field = Point(260,156)

		self.display = pygame.display.set_mode((self.w, self.h))

		pygame.display.set_caption('Conquete Game')

		self.clock = pygame.time.Clock()

		self.reset()


	def reset(self):
		self.players = []
		self.players_UI = []
		self.grid  = np.zeros((self.height, self.width), dtype=np.int8)
		self.direction = Direction.STATIC
		self._place_player()
		self.frame_iteration = 0
		self.player_winner = None

	def _place_player(self):
		for i in range(0,self.nbr_player):
			x = random.randint(0, self.width - 1)
			y = random.randint(0, self.height - 1)

			position = Point(x,y)

			x_ui = (self.start_field.x + x * BLOCK_SIZE) + PLAYER_SIZE
			y_ui = (self.start_field.y + y * BLOCK_SIZE) + PLAYER_SIZE

			pos_ui = Point(x_ui,y_ui)

			player_ui = Player_UI(LIST_COLOR_PLAYER[i],pos_ui)
			player = Player(i+1,position)
			self.players.append(player)
			self.players_UI.append(player_ui)

	def _move_ui(self, player):
		x_ui = self.players_UI[player.id -1].position.x
		y_ui = self.players_UI[player.id -1].position.y

		match player.direction:
			case Direction.RIGHT:
				x_ui += BLOCK_SIZE
			case Direction.LEFT:
				x_ui -= BLOCK_SIZE
			case Direction.UP:
				y_ui -= BLOCK_SIZE
			case Direction.DOWN:
				y_ui += BLOCK_SIZE
			case Direction.STATIC:
				pass

		self.players_UI[player.id - 1].position = Point(x_ui,y_ui)

	def check_voisin_color_player(self,player):
		pos = player.position
		pos_color_same = []
		pos_color_same_diago = []
		neighbors = [(pos.x - 1, pos.y),
		             (pos.x + 1, pos.y),
		             (pos.x, pos.y - 1),
		             (pos.x, pos.y + 1)]

		neighbors_diago = [(pos.x - 1, pos.y - 1),
		                   (pos.x + 1, pos.y + 1),
		                   (pos.x + 1, pos.y - 1),
		                   (pos.x - 1 , pos.y +1)]
		for n in neighbors:
			#In Grid
			if 0 <= n[0] <= self.width-1 and 0 <= n[1] <= self.height-1:
				if self.grid[n[1],n[0]] == player.id:
					pos_color_same.append(n)
		for n in neighbors_diago:
			#In Grid
			if 0 <= n[0] <= self.width-1 and 0 <= n[1] <= self.height-1:
				if self.grid[n[1],n[0]] == player.id:
					pos_color_same_diago.append(n)

		if len(pos_color_same) > 1 and len(pos_color_same_diago) < 4:
			return pos_color_same
		return None

	def conquete_field(self,x,y, player):
		pull = []
		queue = []
		queue.append([x,y])
		while queue:
			current_queue = queue.pop()
			pos_x = current_queue[0]
			pos_y = current_queue[1]
			neighbors = [(pos_x - 1, pos_y),
			             (pos_x + 1, pos_y),
			             (pos_x, pos_y - 1),
			             (pos_x, pos_y + 1)]

			for n in neighbors:
				if 0 <= n[0] <= self.width - 1 and 0 <= n[1] <= self.height - 1:
					if self.grid[n[1],n[0]] != 0 and self.grid[n[1],n[0]] != player.id:
						return []
					if self.grid[n[1],n[0]] == 0:
						if n not in pull:
							pull.append(n)
							queue.append(n)
				else:
					return []
		return pull
	#CHECK LES BORDURES
	def check_field(self,player):
		match player.direction:
			case Direction.RIGHT:
				if player.position.x == self.width - 1:
					return False
				else:
					return True
			case Direction.LEFT:
				if player.position.x == 0:
					return False
				else:
					return True
			case Direction.UP:
				if player.position.y == 0:
					return False
				else:
					return True
			case Direction.DOWN:
				if player.position.y == self.height-1:
					return False
				else:
					return True
			case _:
				return True

	def play_step(self,player_id,action):

		player = self.players[player_id-1]

		self.frame_iteration += 1

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()

		player.new_dir(action)

		if self.check_field(player) != False:
			player.move()
			self._move_ui(player)

		#Update Field
		self.update_field()

		voisins = self.check_voisin_color_player(player)


		if voisins is not None:
			for v in voisins:
				voisin_neutral = self.return_voisin_neutre(v[0], v[1])
				if len(voisin_neutral) > 0:
					for vn in voisin_neutral:
						conquete = self.conquete_field(vn[0],vn[1],player)
						if len(conquete) > 0:
							player.score += len(conquete)
							value = len(conquete)
							player.reward = self.conquete_reward(value)
							for c in conquete:
								self.grid[c[1],c[0]] = player.id

		#check_game_over
		game_over = False
		check_neutral = False
		for y,x in np.ndindex(self.grid.shape):
			if self.grid[y,x] == 0:
				check_neutral = True

		if check_neutral == False or self.frame_iteration > 1000:
			game_over = True
			winner = 0
			best_score = 0
			for player in self.players:
				if player.score >= best_score:
					best_score = player.score
					winner = player.id
					self.player_winner = player
			for player in self.players:
				if player.id == winner:
					if player.score > self.recor:
						self.recor = player.score
						player.reward = 20
					elif player.score < self.last_score:
						player.reward = -20
				else:
					if player.score > self.last_score:
						player.reward = 10
					else:
						player.reward = -20

			return game_over

		self._update_ui()
		#self.clock.tick(SPEED)
		pygame.display.flip()
		return game_over

	def conquete_reward(self,value_conquete):
		return value_conquete
		match value_conquete:
			case t if value_conquete in range(10, 20):
				return 20
			case t if value_conquete in range(20, 40):
				return 25
			case t if value_conquete > 40:
				return 30


	def return_voisin_neutre(self,x,y):
		voisin_neutre = []
		neighbors = [(x - 1, y),
		             (x + 1, y),
		             (x, y - 1),
		             (x, y + 1)]
		for n in neighbors:
			if 0 <= n[0] <= self.width - 1 and 0 <= n[1] <= self.height - 1:
				if self.grid[n[1]][n[0]] == 0:
					voisin_neutre.append(n)
		return voisin_neutre

	def _update_ui(self):
		self.display.fill(BACKGROUND)
		self.color_field()
		self.drawGrid()
		frame_ite = font.render(f"Frame iteration : {self.frame_iteration}",True, RED,WHITE)
		self.display.blit(frame_ite, [0, 50])

		for player in self.players:
			score_txt = font.render(f"Score {player.name} : {player.score} ",True, self.players_UI[player.id -1].color,WHITE)
			self.display.blit(score_txt, [SPACE_SCORE + (player.id * SIZE_SCORE_TXT), 0])

		for player_ui in self.players_UI:
			pygame.draw.circle(self.display, player_ui.color,(player_ui.position.x, player_ui.position.y), PLAYER_SIZE)
		pygame.display.flip()

	def update_field(self):
		for player in self.players:

			y = player.position.y
			x = player.position.x

			if self.grid[y,x] == 0:
				self.grid[y,x] = player.id
				player.score += 1
				player.reward = 1
			else:
				player.reward = - 1

	def drawGrid(self):
		for y,x in np.ndindex(self.grid.shape):
			rect = pygame.Rect(self.start_field.x + x * BLOCK_SIZE, self.start_field.y + y * BLOCK_SIZE,BLOCK_SIZE, BLOCK_SIZE)
			pygame.draw.rect(self.display, GRID, rect, 1)

	def color_field(self):
		for y, x in np.ndindex(self.grid.shape):
			rect = pygame.Rect(self.start_field.x + 1 + x * BLOCK_SIZE,
			                   self.start_field.y + 1 + y * BLOCK_SIZE,
			                   BLOCK_SIZE - 2,
			                   BLOCK_SIZE - 2)
			rect_center = pygame.Rect((self.start_field.x + (x * BLOCK_SIZE)) + 4,
			                          (self.start_field.y + (y * BLOCK_SIZE)) + 4,
			                          BLOCK_SIZE - 8, BLOCK_SIZE - 8)
			if self.grid[y,x] == 0:
				pygame.draw.rect(self.display, NEUTRAL_COLOR, rect)
				pygame.draw.rect(self.display, NEUTRAL_COLOR_CENTER, rect_center)
			else:
				pygame.draw.rect(self.display, self.players_UI[self.grid[y,x] - 1].color, rect)
				pygame.draw.rect(self.display, self.players_UI[self.grid[y,x] - 1].color_center, rect_center)