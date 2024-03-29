import pygame

import torch
import random
import numpy as np
from collections import deque
from game import Conquete, Direction
from robot import Robot



Fred = Robot('Fred', 1)
Lucie = Robot('Lucie', 2)

robots = [Fred,Lucie]

game = Conquete()

def get_state(id):
	my_player = None

	for player in game.players:
		if player.id == id:
			my_player = player

	# DIRECTION
	dir_l = my_player.direction == Direction.LEFT
	dir_r = my_player.direction == Direction.RIGHT
	dir_u = my_player.direction == Direction.UP
	dir_d = my_player.direction == Direction.DOWN
	static = my_player.direction == Direction.STATIC
	player_direction = np.array([dir_l, dir_r, dir_u, dir_d, static], dtype='int')
	# RESULTA == > [0,0,0,0,0]

	# PLAYER POSITION ONE HOT Encoding
	player_position = np.zeros((game.height, game.width), dtype='int')
	player_position[player.position_grid.y, player.position_grid.x] = 1
	player_position = player_position.flatten()
	# RESULTA ==> [0,0,0,0,0,...]
	state = np.concatenate((player_direction, player_position))

	# OTEHR PLAYER POSITION ONE HOT Encoding
	other_player_position = np.zeros((game.height, game.width), dtype='int')
	for p in game.players:
		if p != player.id:
			other_player_position[p.position_grid.y, p.position_grid.x] = 1
	other_player_position = other_player_position.flatten()
	# RESULAT ==> [0,0,0,0,0,...]
	state = np.concatenate((state, other_player_position))

	grid = game.grid.copy().flatten()
	state = np.concatenate((state, grid))
	return state


def train():
	while True:
		for robot in robots:
			robot.state = get_state(robot.id_game)
			robot.get_action()
		for robot in robots:
			final_move = robot.final_move
			state_old = robot.state
			#Revoir la gestion des rewards car normalement c'est ici que je dois les récupérers
			reward , done = game.play_step(robot.id_game, final_move)
			state_new = get_state(robot.id_game)
			robot.train_short_memory(state_old,final_move, reward, state_new,done)

		if done:
			game.reset()
			#Check les scores

if __name__ == '__main__':
	train()