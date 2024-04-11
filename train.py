
import copy
import numpy as np

from game.game import Conquete, Direction
from IA.robot import Robot
from IA.data_robot import Data_robot, show_data
from save import Save

Fred = Robot('Fred', 1)
Lucie = Robot('Lucie', 2)

robots = [Fred,Lucie]
nb_game = 2

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
	player_position[player.position.y, player.position.x] = 1
	player_position = player_position.flatten()
	# RESULTA ==> [0,0,0,0,0,...]
	state = np.concatenate((player_direction, player_position))

	# OTEHR PLAYER POSITION ONE HOT Encoding
	other_player_position = np.zeros((game.height, game.width), dtype='int')
	for p in game.players:
		if p != player.id:
			other_player_position[p.position.y, p.position.x] = 1
	other_player_position = other_player_position.flatten()
	# RESULAT ==> [0,0,0,0,0,...]
	state = np.concatenate((state, other_player_position))

	grid = game.grid.copy().flatten()
	state = np.concatenate((state, grid))
	return state

def new_round():
	best_robot = None
	best_nb_win = 0
	for robot in robots:
		if robot.n_win > best_nb_win:
			best_nb_win = robot.n_win
			best_robot = robot

	print(f"Winner is : {best_robot.name}")
	for robot in robots:
		robot.model = copy.deepcopy(best_robot.model)
		robot.memory = copy.deepcopy(best_robot.memory)
		# if robot.id_game != best_robot.id_game:
		# 	robot.change_type("challenger")
		# else:
		# 	robot.change_type("master")
	best_robot.model.save()

datas = []

def init_robot_in_game():
	for robot in robots:
		data = Data_robot(robot.default_name)
		datas.append(data)


def init_player_robot():
	for i, player in enumerate(game.players):
		player.name = robots[i].name

def train(number_round = 10):
	current_round = 0
	init_robot_in_game()
	init_player_robot()
	save = Save(game.players)
	while True:
		for robot in robots:
			robot.state = get_state(robot.id_game)
			robot.get_action()
		for robot in robots:
			player = [player for player in game.players if player.id == robot.id_game]
			final_move = robot.final_move
			state_old = robot.state
			#Revoir la gestion des rewards car normalement c'est ici que je dois les récupérers
			done = game.play_step(robot.id_game, final_move)
			state_new = get_state(robot.id_game)
			save.add_line_round([current_round,robot.id_game,player[0].position,player[0].score,player[0].reward])
			robot.train_short_memory(state_old,final_move, player[0].reward, state_new,done)
			robot.remember(state_old, final_move, player[0].reward, state_new, done)

		if done:
			for robot in robots:
				robot.n_games += 1
				if robot.id_game == game.player_winner.id:
					save.new_won_resume(robot.id_game)
					robot.n_win += 1
				else:
					save.new_lose_resume(robot.id_game)
					robot.n_lose += 1
			current_round += 1
			for x, data in enumerate(datas):
				print(game.players[x].score)
				data.scores.append(game.players[x].score)
				data.total_score += game.players[x].score
				mean_score = data.total_score/robots[x].n_games
				data.mean_scores.append(mean_score)
			if current_round >= number_round:
				save.next_round()
				current_round = 0
				new_round()

			show_data(datas)
			game.reset()
			init_player_robot()
		save.save_to_csv()


if __name__ == '__main__':

	train()