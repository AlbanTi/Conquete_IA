import matplotlib.pyplot as plt
from IPython import display
#plt.ion()
class Data_robot:
	def __init__(self,name):
		self.name = name
		self.scores = []
		self.mean_scores = []
		self.total_score = 0


def show_data(datas):
	display.clear_output(wait=True)
	display.display(plt.gcf())
	fig, axs = plt.subplots(len(datas), 1, layout='constrained', sharey=True)
	for ax, data in zip(axs.flat, datas):
		ax.set_title(data.name)
		ax.plot(data.scores)
		ax.plot(data.mean_scores)
		ax.text(len(data.scores) - 1, data.scores[-1], str(data.scores[-1]))
		ax.text(len(data.mean_scores) - 1, data.mean_scores[-1], str(data.mean_scores[-1]))

	fig.text(0.5, 0.01, 'Number of Games', ha='center', va='center', fontsize=12)
	fig.text(0.01, 0.5, 'Score', ha='center', va='center', fontsize=12, rotation='vertical')

	plt.suptitle('Training...')

	#plt.tight_layout()

	plt.show(block=False)
	plt.pause(.1)
