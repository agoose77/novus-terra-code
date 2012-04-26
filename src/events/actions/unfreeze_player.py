from .action import Action
import sudo


class unfreeze_player(Action):
	""" Unfreeze the player """
	def __init__(self):
		super().__init__()

	def run(self):
		sudo.player.unfreeze()
		return Action.FINISHED
