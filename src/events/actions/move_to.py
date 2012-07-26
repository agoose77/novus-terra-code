from mathutils import Vector

from .action import Action
import sudo


class move_to(Action):
	""" Make an actor walk or run from its current location to a target location 

	entity : The ID of the entity to run the action on
	point : The location to walk to. Format as '[x, y, z]'
	"""
	
	def __init__(self, entity='', point='[0, 0, 0]'):
		super().__init__()

		self.entity = entity
		self.point = Vector(eval(point))

		self.initialised = False

	def run(self):
		entity = sudo.cell_manager.cell.id_entity.get(self.entity)
		
		if not self.initialised:
			entity.move_to(self.point)
			self.initialised = True

		if entity.path:
			return Action.RUNNING
		else:
			return Action.FINISHED
