import events.actions.Action as Action
import sudo


class dialogue(Action):
	""" Display a dialogue tree """
	def __init__(self, filename):
		super().__init__()
		sudo.world.dialogue_manager.display_dialogue(filename)

	def run(self):
		if sudo.world.dialogue_manager.current_dialogue is not None:
			return Action.RUNNING
		else:
			return Action.FINISHED
