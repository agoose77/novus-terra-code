from mathutils import Vector

from .action import Action
import entities
import sudo


class look_at(Action):
	""" Make an actor look at a point

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

		if entity is None:
			self.error_msg = self.entity + ' does not exist in this cell.'
			return Action.FAILED

		if not isinstance(entity, entities.Actor):
			self.error_msg = self.entity +' is not an actor.'
			return Action.FAILED

		if not self.initialised:
			entity.look_at(self.point)
			self.initialised = True

		if entity.point_of_interest:
			return Action.RUNNING
		else:
			return Action.FINISHED
