import cell
import entities


class Door(entities.EntityBase):
	""" An entity that teleports the player from one cell to another.

	properties (set on the KX_GameObject):
		- entity: Set to 'Door'
		- cell: the name of the cell to teleport to
		- destination: the name of the object in the destination cell to teleport to
	"""
	def __init__(self, packet=None):
		entities.EntityBase.__init__(self, packet)

		self.interact_label = 'Enter'

	def on_interact(self, player):
		# TODO play sound - door open

		cell.CellManager.singleton.next_destination = self['destination']
		cell.CellManager.singleton.load('./data/cells/' + self['cell'] + '.cell')
