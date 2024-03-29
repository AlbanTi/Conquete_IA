from game import Conquete, Direction
import pygame

import torch
import random
import numpy as np
from collections import deque
from game import Conquete, Direction, Point

from model import MonteCarloAgent,QTrainer

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:
	def __init__(self,epsilon_const = 80, gamma = 0.99, hidden_size = 2560):
		self.n_games = 0
		self.epsilon = 0  # Randomness
		self.epsilon_const = epsilon_const
		self.gamma = gamma  # discount rate
		self.memory = deque(maxlen=MAX_MEMORY)
		self.model = MonteCarloAgent(2105, 5)
		self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

	def update_trainer(self):
		self.trainer = QTrainer(self.model,lr=LR,gamma=self.gamma)

	def get_state(self,game,id):
		my_player = None

		for player in game.players:
			if player.id == id:
				my_player = player


		#DIRECTION
		dir_l = my_player.direction == Direction.LEFT
		dir_r = my_player.direction == Direction.RIGHT
		dir_u = my_player.direction == Direction.UP
		dir_d = my_player.direction == Direction.DOWN
		static = my_player.direction == Direction.STATIC
		player_direction = np.array([dir_l, dir_r, dir_u, dir_d, static], dtype='int')
		#RESULTA == > [0,0,0,0,0]


		#PLAYER POSITION ONE HOT Encoding
		player_position = np.zeros((game.height, game.width), dtype='int')
		player_position[player.position_grid.y,player.position_grid.x] = 1
		player_position = player_position.flatten()
		#RESULTA ==> [0,0,0,0,0,...]
		state = np.concatenate((player_direction,player_position))

		#OTEHR PLAYER POSITION ONE HOT Encoding
		other_player_position = np.zeros((game.height, game.width), dtype='int')
		for p in game.players:
			if p != player.id:
				other_player_position[p.position_grid.y,p.position_grid.x] = 1
		other_player_position = other_player_position.flatten()
		# RESULAT ==> [0,0,0,0,0,...]
		state = np.concatenate((state, other_player_position))


		grid = game.grid.copy().flatten()
		state = np.concatenate((state, grid))
		return state

	def remember(self, state, action, reward, next_state, done):
		self.memory.append((state, action, reward, next_state,done))

	def train_long_memory(self):
		if len(self.memory) > BATCH_SIZE:
			mini_sample = random.sample(self.memory, BATCH_SIZE)
		else:
			mini_sample = self.memory

		states,actions,rewards,next_states,dones = zip(*mini_sample)
		self.trainer.train_step(states, actions, rewards, next_states, dones)

	def train_short_memory(self,state, action, reward, next_state, done):
		self.trainer.train_step(state, action, reward, next_state, done)

	def get_action(self, state):
		self.epsilon = self.epsilon_const - self.n_games
		final_move = [1,0,0]
		if random.randint(0,200) < self.epsilon:
			move = random.randint(0,4)
			#final_move[move] = 1
		else:
			#state0 = torch.tensor(state, dtype=torch.float)
			state0 = torch.from_numpy(state).float()
			prediction = self.model(state0)
			move = torch.argmax(prediction).item()
			#print(move)
			#final_move[move] = 1

		match move:
			case 0:
				final_move = [0,0,0]
			case 1:
				final_move = [1, 0, 0]
			case 2:
				final_move = [1,0,1]
			case 3:
				final_move = [1,1,0]
			case 4:
				final_move = [1,1,1]

		return final_move

def train():
	agents = []
	game = Conquete()
	players = game.players

	for player in players:
		agents.append(Agent())

	while True:
		for player in players:
			state_old = agents[player.id-1].get_state(game,player.id)
			final_move = agents[player.id-1].get_action(state_old)
			done = game.play_step(player,final_move)
			state_new = agents[player.id-1].get_state(game,player.id)
			agents[player.id-1].train_short_memory(state_old, final_move, player.reward, state_new, done)

			agents[player.id-1].remember(state_old, final_move, player.reward, state_new, done)

		if done:
			game.reset()
			player_win = 0
			best_score = 0
			for player in players:
				if player.score > best_score:
					player_win = player.id
					best_score = player.score
				elif player.score == best_score:
					player_win = player.id

			agent = agents[player_win-1]
			agent.n_games += 1
			agent.train_long_memory()
			agent.model.save()
			agents = []
			for player in players:
				agents.append(agent)




def control_debug():

	game = Conquete()
	player = game.players[0]

	while True:

		action = [0,0,0,0]

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
			if event.type == pygame.KEYDOWN:
				# Move Event
				if event.key == pygame.K_LEFT:
					action = [0,0,0,1]
				if event.key == pygame.K_RIGHT:
					action = [0,0,1,0]
				if event.key == pygame.K_UP:
					action = [1,0,0,0]
				if event.key == pygame.K_DOWN:
					action = [0,1,0,0]

		game.play_step(player, action)

if __name__ == '__main__':
	train()
	#control_debug()
