from entity_base import EntityBase
import cell
import ui

"""

properties: (set on the KX_GameObject):
	- entity = 'Door'
	- cell: the name of the cell to teleport to
	- destination: the name of the object in the destination cell to teleport to
"""
class Door(EntityBase):
	"""

	"""
	def __init__(self, packet=None):
		EntityBase.__init__(self, packet)

		self.iteract_label = 'Enter'

	def on_interact(self, player):
		# TODO play sound - door open
		
		cell.CellManager.singleton.next_destination = self['destination']
		cell.CellManager.singleton.load('./data/cells/'+ self['cell'] +'.cell')
		