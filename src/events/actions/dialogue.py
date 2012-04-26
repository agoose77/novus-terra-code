from .action import Action
import sudo


class dialogue(Action):
	""" Display a dialogue tree """
	def __init__(self, filename):
		super().__init__()
		
		self.filename = filename
		self.initialised = False

	def run(self):
		if not self.initialised:
			self.initialised = True
			sudo.world.dialogue_manager.display_dialogue(self.filename)
		if sudo.world.dialogue_manager.current_dialogue is not None:
			return Action.RUNNING
		else:
			self.initialised = False
			return Action.FINISHED


