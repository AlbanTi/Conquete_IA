from model import Linear_QNet,QTrainer
from collections import deque
import torch
import random
import numpy as np


MAX_MEMORY = 100_000
LR = 0.01
BATCH_SIZE = 1000

class Robot:
	def __init__(self,name,id_game, epsilon_const = 80, gamma = 0.99,type = "master"):
		self.name = name + "_" + type
		self.n_games = 0
		self.n_lose = 0
		self.n_win = 0
		self.epsilon = 0
		self.epsilon_const = epsilon_const
		self.gamma = gamma
		self.memory = deque(maxlen=MAX_MEMORY)
		self.model = Linear_QNet(2105, 256, 4)
		self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
		self.id_game = id_game
		self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
		self.final_move = [0,0,0,0]
		self.state = None


	def remember(self,state,action,reward,next_state,done):
		self.memory.append((state,action,reward,next_state,done))

	def get_action(self):
		self.epsilon = self.epsilon_const - self.n_games
		self.final_move = [0, 0, 0, 0]
		if random.randint(0,200) < self.epsilon:
			move = random.randint(0,3)
			self.final_move[move] = 1
		else:
			state0 = torch.tensor(self.state, dtype=torch.float)
			prediction = self.model(state0)
			move = torch.argmax(prediction).item()
			self.final_move[move] = 1

	def train_short_memory(self,state, action, reward, next_state, done):
		self.trainer.train_step(state, action, reward, next_state, done)

	def train_long_memory(self):
		if len(self.memory) > BATCH_SIZE:
			mini_sample = random.sample(self.memory, BATCH_SIZE)
		else:
			mini_sample = self.memory

		states,actions,rewards,next_states,dones = zip(*mini_sample)
		self.trainer.train_step(states, actions, rewards, next_states, dones)

	def save_model(self):
		self.model.save(self.name)

	def change_type(self,type):
		self.name = self.name + "_" + type