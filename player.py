from enum import Enum
from collections import namedtuple
import numpy as np

Point = namedtuple('Point', 'x, y')

class Direction(Enum):
	RIGHT = 1
	LEFT = 2
	UP = 3
	DOWN = 4
	STATIC = 5

class Player:
	def __init__(self, id,position, name = "NoName"):
		self.score = 0
		self.id = id
		self.direction = Direction.STATIC
		self.position = position
		self.reward = 0
		self.name = name

	def new_dir(self,action):
		if np.array_equal(action, [0,0,0,0]):
			new_dir = self.direction # STATIC
		elif np.array_equal(action, [1,0,0,0]):
			new_dir = Direction.UP
		elif np.array_equal(action,[0,1,0,0]): # [ 1,0,0 ] left trun
			new_dir = Direction.DOWN
		elif np.array_equal(action,[0,0,1,0]):
			new_dir = Direction.RIGHT
		else:
			new_dir = Direction.LEFT
		self.direction = new_dir

	def move(self):
		match self.direction:
			case Direction.RIGHT:
				self.position = Point(self.position.x + 1, self.position.y)
			case Direction.LEFT:
				self.position = Point(self.position.x - 1, self.position.y)
			case Direction.UP:
				self.position = Point(self.position.x, self.position.y - 1)
			case Direction.DOWN:
				self.position = Point(self.position.x, self.position.y + 1)
			case Direction.STATIC:
				pass