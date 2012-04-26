from .action import Action
import sudo


class animate(Action):
	""" Control an animation on an entity 

	entity : The ID of the entity to run the action on
	action : The name of the action to run
	mode : One of 'play', 'loop' or 'stop' (If 'stop' it will stop the action on the specified layer
	start: Start frame
	end: End frame
	layer : Layer to run the animation on
	speed : Speed multiplier of the action (1.0 = no change)
	"""
	
	def __init__(self, entity='', action='', mode='play', start=1, end=1, layer=0, speed=1.0):
		super().__init__()

		self.entity = entity
		self.action = action
		self.start = float(start)
		self.end = float(end)
		self.layer = int(layer)
		self.speed = float(speed)

		if mode == 'play':
			self.mode = 0
		elif mode == 'loop':
			self.mode = 1
		elif mode == 'stop':
			self.mode = 'stop'

	def run(self):
		entity = sudo.cell_manager.cell.id_entity.get(self.entity)
		if entity is not None:
			if self.mode == 'stop':
				entity.stopAction(self.layer)
			else:
				entity.playAction(self.action, self.start, self.end, layer=self.layer, play_mode=self.mode, speed=self.speed)

		return Action.FINISHED
