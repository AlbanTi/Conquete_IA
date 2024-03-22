from enum import Enum
from collections import namedtuple
import numpy as np
import pygame
import random

pygame.init()
font = pygame.font.Font('arial.ttf', 25)


class Direction(Enum):
	RIGHT = 1
	LEFT = 2
	UP = 3
	DOWN = 4
	STATIC = 5

Point = namedtuple('Point', 'x, y')

Field = namedtuple('Field', 'w,h')

WHITE = (255, 255, 255)
GRID = (200, 200, 200)
RED = (200,0,0)
BLUE = (0,100,200)
BACKGROUND = (40, 40, 40)

PLAYER_SIZE = 13

FIELD_BLUE = (0,100,200)
FIELD_RED = (200,100,0)

NEUTRAL_COLOR = (100,100,100)
NEUTRAL_COLOR_CENTER = (128,128,128)

BLOCK_SIZE = 26
SPEED = 15

LIST_COLOR_PLAYER = [BLUE,RED]

SPACE_SCORE = 110
SIZE_SCORE_TXT = 250

MOVE_REMPLISSAGE = [
	(-1,0),
	(1,0),
	(0,-1),
	(0,1)
]

class Player:
	def __init__(self, id,position, color = BLUE):
		self.position = position
		self.score = 0
		self.id = id
		self.color = color
		self.color_center = (color[0]+28,color[1]+28,color[2]+28)
		self.direction = Direction.STATIC
		self.position_grid = Point(0,0)



class Conquete:
	def __init__(self, w=1274,h=754, nbr_player = 2):
		self.w = w
		self.h = h
		self.nbr_player = nbr_player

		self.players = []

		self.nbr_row = 20
		self.nbr_column = 35

		self.grid = [[0 for _ in range(self.nbr_column)] for _ in range(self.nbr_row)]
		self.mask = self.grid.copy()

		self.start_field = Point(260,156)

		self.display = pygame.display.set_mode((self.w, self.h))
		pygame.display.set_caption('Conquete Game')
		self.clock = pygame.time.Clock()
		self.reset()

	def reset(self):
		self.direction = Direction.STATIC
		self._place_player()
		self.frame_iteration = 0

	def _place_player(self):
		for i in range(0,self.nbr_player):

			x = random.randint(0, self.nbr_column-1)
			y = random.randint(0, self.nbr_row-1)


			x_pos = (self.start_field.x + x * BLOCK_SIZE) + PLAYER_SIZE
			y_pos = (self.start_field.y + y * BLOCK_SIZE) + PLAYER_SIZE

			player = Player(i+1,Point(x_pos,y_pos),LIST_COLOR_PLAYER[i])
			player.position_grid = Point(x,y)
			if player in self.players:
				self._place_player()
			else:
				self.players.append(player)

	def _move(self, player, action):
		if np.array_equal(action, [0,0,0]):
			new_dir = player.direction # STATIC
		elif np.array_equal(action, [1,1,0]):
			new_dir = Direction.RIGHT
		elif np.array_equal(action,[1,0,0]): # [ 1,0,0 ] left trun
			new_dir = Direction.LEFT
		elif np.array_equal(action,[1,0,1]):
			new_dir = Direction.DOWN
		else:
			new_dir = Direction.UP

		if self.check_field(player,new_dir) == False:
			new_dir = Direction.STATIC

		player.direction = new_dir


		x = player.position.x
		y = player.position.y

		match player.direction:
			case Direction.RIGHT:
				x += BLOCK_SIZE
				player.position_grid = Point(player.position_grid.x + 1, player.position_grid.y)
			case Direction.LEFT:
				x -= BLOCK_SIZE
				player.position_grid = Point(player.position_grid.x - 1, player.position_grid.y)
			case Direction.UP:
				y -= BLOCK_SIZE
				player.position_grid = Point(player.position_grid.x, player.position_grid.y - 1)
			case Direction.DOWN:
				y += BLOCK_SIZE
				player.position_grid = Point(player.position_grid.x, player.position_grid.y + 1)
			case Direction.STATIC:
				pass

		player.position = Point(x,y)

	def check_voisin_color_player(self,player):
		width = len(self.grid[0])
		height = len(self.grid)
		pos_grid = player.position_grid
		pos_color_same = []
		pos_color_same_diago = []
		neighbors = [(pos_grid.x - 1, pos_grid.y),
		             (pos_grid.x + 1, pos_grid.y),
		             (pos_grid.x, pos_grid.y - 1),
		             (pos_grid.x, pos_grid.y + 1)]

		neighbors_diago = [(pos_grid.x - 1, pos_grid.y - 1),
		                   (pos_grid.x + 1, pos_grid.y + 1),
		                   (pos_grid.x + 1, pos_grid.y - 1),
		                   (pos_grid.x - 1 , pos_grid.y +1)]
		for n in neighbors:
			#In Grid
			if 0 <= n[0] <= width-1 and 0 <= n[1] <= height-1:
				if self.grid[n[1]][n[0]] == player.id:
					pos_color_same.append(n)
		for n in neighbors_diago:
			#In Grid
			if 0 <= n[0] <= width-1 and 0 <= n[1] <= height-1:
				if self.grid[n[1]][n[0]] == player.id:
					pos_color_same_diago.append(n)

		if len(pos_color_same) > 1 and len(pos_color_same_diago) < 4:
			return pos_color_same
		return None

	def conquete_field(self,x,y, player):
		pull = []
		width = len(self.grid[0])
		height = len(self.grid)

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
				if 0 <= n[0] <= width - 1 and 0 <= n[1] <= height - 1:
					if self.grid[n[1]][n[0]] != 0 and self.grid[n[1]][n[0]] != player.id:
						return []
					if self.grid[n[1]][n[0]] == 0:
						if n not in pull:
							pull.append(n)
							queue.append(n)
				else:
					return []
		return pull
	#CHECK LES BORDURES
	def check_field(self,player,new_dir):
		match new_dir:
			case Direction.RIGHT:
				if player.position.x ==  (self.start_field.x + (self.nbr_column-1) * BLOCK_SIZE) + PLAYER_SIZE:
					return False
				else:
					return True
			case Direction.LEFT:
				if player.position.x == (self.start_field.x + 0 * BLOCK_SIZE) + PLAYER_SIZE:
					return False
				else:
					return True
			case Direction.UP:
				if player.position.y == (self.start_field.y + 0 * BLOCK_SIZE) + PLAYER_SIZE:
					return False
				else:
					return True
			case Direction.DOWN:
				if player.position.y == (self.start_field.y + (self.nbr_row-1) * BLOCK_SIZE) + PLAYER_SIZE:
					return False
				else:
					return True
			case _:
				return True

	def play_step(self,player,action):
		self.frame_iteration += 1

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()

		self._move(player,action)
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
							for c in conquete:
								self.grid[c[1]][c[0]] = player.id

		#REWARD

		self._update_ui()
		self.clock.tick(SPEED)
		pygame.display.update()

	def return_voisin_neutre(self,x,y):
		width = len(self.grid[0])
		height = len(self.grid)
		voisin_neutre = []
		neighbors = [(x - 1, y),
		             (x + 1, y),
		             (x, y - 1),
		             (x, y + 1)]
		for n in neighbors:
			if 0 <= n[0] <= width - 1 and 0 <= n[1] <= height - 1:
				if self.grid[n[1]][n[0]] == 0:
					voisin_neutre.append(n)

		return voisin_neutre

	def check_limite(self,pos):
		width = len(self.grid[0])
		height = len(self.grid)

		# hits boundary
		if 0 <= pos.x <= width - 1 and 0 <= pos.y <= height - 1:
			return False

		return True

	def _update_ui(self):
		self.display.fill(BACKGROUND)

		self.color_field()
		self.drawGrid()



		for player in self.players:
			pygame.draw.circle(self.display,player.color,(player.position.x,player.position.y),PLAYER_SIZE)
			score_txt = font.render(f"Score player {player.id} : {player.score} ",True, player.color,WHITE)
			self.display.blit(score_txt, [SPACE_SCORE + (player.id * SIZE_SCORE_TXT), 0])

		pygame.display.flip()

	def update_field(self):
		for player in self.players:

			cell_x = (player.position.x - self.start_field.x)//BLOCK_SIZE
			cell_y = (player.position.y - self.start_field.y)//BLOCK_SIZE

			if self.grid[cell_y][cell_x] == 0:
				self.grid[cell_y][cell_x] = player.id
				player.score += 1

	def drawGrid(self):
		for row in range(len(self.grid)):
			for cell in range(len(self.grid[row])):
				rect = pygame.Rect(self.start_field.x + cell * BLOCK_SIZE, self.start_field.y + row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
				pygame.draw.rect(self.display,GRID,rect,1)

	def color_field(self):
		for row in range(len(self.grid)):
			for cell in range(len(self.grid[row])):
				rect = pygame.Rect(self.start_field.x + 1 + cell * BLOCK_SIZE,
				                   self.start_field.y + 1 + row * BLOCK_SIZE,
				                   BLOCK_SIZE - 2,
				                   BLOCK_SIZE - 2)

				rect_center = pygame.Rect((self.start_field.x + (cell * BLOCK_SIZE)) + 4,
				                          (self.start_field.y + (row * BLOCK_SIZE)) + 4,
				                          BLOCK_SIZE - 8, BLOCK_SIZE - 8)
				if self.grid[row][cell] == 0:
					pygame.draw.rect(self.display, NEUTRAL_COLOR, rect)
					pygame.draw.rect(self.display, NEUTRAL_COLOR_CENTER, rect_center)
				else :
					pygame.draw.rect(self.display, self.players[self.grid[row][cell]-1].color, rect)
					pygame.draw.rect(self.display, self.players[self.grid[row][cell]-1].color_center, rect_center)
