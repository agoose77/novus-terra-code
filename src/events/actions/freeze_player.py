from .action import Action
import sudo


class freeze_player(Action):
	""" Freeze the player """
	def __init__(self):
		super().__init__()

	def run(self):
		sudo.player.freeze()
		return Action.FINISHED
