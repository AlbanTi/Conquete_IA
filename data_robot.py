import matplotlib.pyplot as plt
from IPython import display



import numpy as np

plt.ion()

class Data_robot:
	def __init__(self,robot,player):
		self.robot = robot
		self.player = player
		self.scores = 0
		self.mean_scores = 0
		self.total_score = 0


def show_data(datas):
	fig, axs = plt.subplots(len(datas))
	fig.suptitle('Training...',fontsize=18, y=0.95)
	for data, ax in zip(datas, axs.ravel()):
		ax.set_title(data.robot.default_name)
		ax.xlabel('Number of Games')
		ax.ylabel('Score')

	plt.show()
