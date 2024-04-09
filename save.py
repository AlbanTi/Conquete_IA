import csv
import os
import pandas as pd

class Save:
	def __init__(self, players):
		self.round = 1
		self.index = 1
		self.directory = ""
		self.directory_rounds = ""
		self.init_save()
		self.init_df_player(players)
		self.init_df_resume()
		self.init_df_round()



	def init_df_player(self,players):
		ids = []
		names = []
		for player in players:
			ids.append(player.id)
			names.append(player.name)
		self.df_player = pd.DataFrame(columns=["player_name"], index=ids, data=names)

	def init_df_resume(self):
		self.df_resume = pd.DataFrame(columns=["round","ID_player","won","lost"])

	def init_df_round(self):
		self.df_round = pd.DataFrame(columns=["index","ID_player","position","score","reward"])

	def next_round(self):
		self.round += 1

	def add_line_round(self, line):
		self.df_round = pd.concat([self.df_round, pd.DataFrame([line])], ignore_index=True)

	def new_won_resume(self, id_player):
		row = self.df_resume[(self.df_resume["ID_player"] == id_player) & (self.df_resume["round"] == self.round)]
		if not row.empty:
			row_index = row.index[0]
			self.df_resume.at[row_index, "won"] += 1
		else:
			print("Aucune ligne trouvé")

	def new_lose_resume(self, id_player):
		row = self.df_resume[(self.df_resume["ID_player"] == id_player) & (self.df_resume["round"] == self.round)]
		if not row.empty:
			row_index = row.index[0]
			self.df_resume.at[row_index, "lost"] += 1
		else:
			print("Aucune ligne trouvé")

	def init_save(self):
		dirNotFound = True
		while (dirNotFound):
			if os.path.isdir(f"saves/save_{self.index}"):
				self.index += 1
			else:
				self.directory = f"saves/save_{self.index}/"
				self.directory_rounds = self.directory + "rounds/"
				os.mkdir(self.directory)
				os.mkdir(self.directory_rounds)
				dirNotFound = False

	def save_to_csv(self):
		if self.directory != "":
			self.df_player.to_csv(self.directory + "players.csv")
			self.df_resume.to_csv(self.directory + "resumes.csv")
			self.df_round.to_csv(self.directory_rounds + f"round_{self.round}.csv")
		else:
			print("save not init")