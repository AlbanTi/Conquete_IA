import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

import os


class Linear_QNet(nn.Module):
	def __init__(self, input_size, hidden_size, output_size):
		super().__init__()
		self.linear1 = nn.Linear(input_size, hidden_size)
		self.linear2 = nn.Linear(hidden_size, output_size)

	def forward(self, x):
		x = F.relu(self.linear1(x))
		x = self.linear2(x)
		return x

	def save(self, file_name='model.pth', model_folder_path = './model'):
		if not os.path.exists(model_folder_path):
			os.makedirs(model_folder_path)

		file_name = os.path.join(model_folder_path, file_name)
		torch.save(self.state_dict(),file_name)

class QTrainer():
	def __init__(self,model,lr,gamma):
		self.model = model
		self.lr = lr
		self.gamma = gamma
		self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
		self.criterion = nn.MSELoss()

	def train_step(self,state,action,reward,next_state,done):
		state = torch.tensor(state, dtype=torch.float)
		next_state = torch.tensor(next_state, dtype=torch.float)
		action = torch.tensor(action, dtype=torch.long)
		reward = torch.tensor(reward, dtype=torch.float)

		if len(state.shape) == 1:
			state = torch.unsqueeze(state,0)
			next_state = torch.unsqueeze(next_state,0)
			action = torch.unsqueeze(action,0)
			reward = torch.unsqueeze(reward,0)
			done = (done,)

		pred = self.model(state)

		target = pred.clone()
		for idx in range(len(done)):
			Q_new = reward[idx]
			if not done[idx]:
				Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))

			target[idx][torch.argmax(action).item()] = Q_new


		self.optimizer.zero_grad()
		loss = self.criterion(target,pred)
		loss.backward()

		self.optimizer.step()

class MultiInputCNN(nn.Module):
	def __init__(self, player_position, player_direction, other_player_position, grid):
		super(MultiInputCNN, self).__init__()

		#Couches de convolution pour joueur
		self.conv_player = nn.Linear(player_position, 64)

		#Couches de convolution pour la direction
		self.conv_direction = nn.Linear(player_direction, 64)

		#Couches de convolution pour la position des autres joueurs
		self.conv_other_players = nn.Linear(other_player_position, 64)

		#Couches de convolution pour la grid
		self.conv_grid = nn.Conv2d(1, 32, kernel_size=(3, 3))

		self.input_grid = torch.from_numpy(grid).unsqueeze(0).unsqueeze(0).float()
		self.input_grid_bn = nn.BatchNorm2d(32)

		self.fc = nn.Linear(64*3 + 32 , 128)

		#Sortie
		self.output_layer = nn.Linear(128, 4)

	def forward(self, player_input, direction_input,other_player_input, grid_input):
		player_out = F.relu(self.conv_player(player_input))
		direction_out = F.relu(self.conv_direction(direction_input))
		other_players_out = F.relu(self.conv_other_players(other_player_input))

		grid_out = F.relu(self.conv_grid(grid_input))
		grid_out = self.input_grid_bn(grid_out)

		grid_out = torch.flatten(grid_out, 1)

		merged = torch.cat((player_out, direction_out, other_players_out,grid_out), dim=1)

		fc_out = F.relu(self.fc(merged))

		output = self.output_layer(fc_out)

		return output

	def save(self, file_name='model.pth', model_folder_path = './model'):
		if not os.path.exists(model_folder_path):
			os.makedirs(model_folder_path)

		file_name = os.path.join(model_folder_path, file_name)
		torch.save(self.state_dict(),file_name)

class MonteCarloAgent(nn.Module):
	def __init__(self,state_dim, action_dim):
		super(MonteCarloAgent, self).__init__()
		self.policy_network = nn.Sequential(
			nn.Linear(state_dim, 128),
			nn.ReLU(),
			nn.Linear(128, action_dim)
		)

	def forward(self,x):
		output = self.policy_network(x)
		return output

	def save(self, file_name='model.pth', model_folder_path = './model'):
		if not os.path.exists(model_folder_path):
			os.makedirs(model_folder_path)

		file_name = os.path.join(model_folder_path, file_name)
		torch.save(self.state_dict(),file_name)

